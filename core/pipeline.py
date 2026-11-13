"""Independent detection, tracking, crossing, rendering, and metrics pipeline."""

from __future__ import annotations

import time
from pathlib import Path

from .counter import CountingEngine, LineCrossingDetector
from .line_manager import LineManager
from .schemas import Detection, FramePerformance, LineConfig, PipelineResult, Track
from .track_history import TrackHistory


def _detection(value) -> Detection:
    if isinstance(value, Detection):
        return value
    return Detection(tuple(value["bbox"]), int(value["class_id"]), value["class_name"], float(value["confidence"]))


def _track(value) -> Track:
    if isinstance(value, Track):
        return value
    return Track(int(value["track_id"]), tuple(value["bbox"]), value["class_name"], float(value.get("confidence", 0.0)), value.get("class_id"), int(value.get("age", 1)))


class TrafficPipeline:
    def __init__(
        self,
        reader=None,
        detector=None,
        tracker=None,
        preprocessor=None,
        line_manager: LineManager | None = None,
        counting_engine: CountingEngine | None = None,
        crossing_detector: LineCrossingDetector | None = None,
        renderer=None,
        frame_skip: int = 0,
        track_buffer: int = 30,
        speed_tracker=None,
    ):
        self.reader = reader
        self.detector = detector
        self.tracker = tracker
        self.preprocessor = preprocessor
        self.line_manager = line_manager or LineManager()
        self.counting_engine = counting_engine or CountingEngine()
        self.crossing_detector = crossing_detector or LineCrossingDetector()
        self.renderer = renderer
        self.frame_skip = max(0, frame_skip)
        self.track_buffer = max(0, track_buffer)
        self.speed_tracker = speed_tracker
        self.history = TrackHistory()
        self._last_processing_ms = 0.0
        self._total_inference_ms = 0.0
        self._processed_frames = 0

    def process_frame(self, frame, frame_index: int = 0, timestamp_ms: float = 0.0) -> PipelineResult:
        started = time.perf_counter()
        inference_started = time.perf_counter()
        prepared = self.preprocessor.process(frame) if self.preprocessor else frame
        raw_detections = self.detector.detect(prepared) if self.detector else []
        inference_ms = (time.perf_counter() - inference_started) * 1000.0
        detections = [_detection(item) for item in raw_detections]
        if self.preprocessor and self.preprocessor.last_transform:
            detections = [
                Detection(self.preprocessor.restore_bbox(item.bbox), item.class_id, item.class_name, item.confidence)
                for item in detections
            ]
        raw_tracks = self.tracker.update(detections, frame) if self.tracker else []
        tracks: list[Track] = []
        for value in raw_tracks:
            track = _track(value)
            record = self.history.update(track, frame_index)
            track.age = record.last_seen - record.first_seen + 1
            tracks.append(track)
        expired_track_ids = self.history.remove_missing(
            {track.track_id for track in tracks}, frame_index, self.track_buffer
        )
        for track_id in expired_track_ids:
            self.crossing_detector.forget_track(track_id)
            self.counting_engine.forget_track(track_id)
        speed_estimates = self.speed_tracker.update(tracks, timestamp_ms, frame_index) if self.speed_tracker else {}
        if self.speed_tracker:
            for track in tracks:
                estimate = speed_estimates.get(track.track_id)
                track.speed_kmh = estimate.speed_kmh if estimate else 0.0
            self.speed_tracker.remove_missing({track.track_id for track in tracks})

        events = []
        for track in tracks:
            for line in self.line_manager.enabled():
                event = self.crossing_detector.update(track, line, frame_index, timestamp_ms)
                if event is not None and self.counting_engine.add_event(event):
                    events.append(event)

        rendered = self.renderer.render(frame, detections, tracks, self.line_manager.enabled(), events, speed_estimates) if self.renderer else frame
        processing_ms = (time.perf_counter() - started) * 1000.0
        self._last_processing_ms = processing_ms
        self._total_inference_ms += inference_ms
        self._processed_frames += 1
        fps = 1000.0 / processing_ms if processing_ms > 0 else 0.0
        return PipelineResult(
            rendered,
            detections,
            tracks,
            events,
            self.counting_engine.statistics(),
            FramePerformance(inference_ms, processing_ms, fps),
            speed_estimates,
        )

    def run(self, stop_event=None, output_path: str | Path | None = None, max_frames: int | None = None, frame_callback=None):
        if self.reader is None:
            raise ValueError("TrafficPipeline.run requires a reader")
        opened_here = self.reader.capture is None
        if opened_here and not self.reader.open():
            raise RuntimeError(self.reader.last_error or "Unable to open source")
        writer = None
        try:
            if output_path is not None:
                import cv2

                metadata = self.reader.get_metadata()
                fps = metadata.fps if metadata.fps > 0 else 25.0
                writer = cv2.VideoWriter(str(output_path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (metadata.width, metadata.height))
                if not writer.isOpened():
                    raise RuntimeError(f"Unable to create processed video: {output_path}")
            results = []
            while max_frames is None or len(results) < max_frames:
                if stop_event is not None and stop_event.is_set():
                    break
                item = self.reader.read()
                if not item["success"]:
                    break
                if self.frame_skip and item["frame_index"] % (self.frame_skip + 1):
                    continue
                result = self.process_frame(item["frame"], item["frame_index"], item["timestamp_ms"])
                if writer is not None:
                    writer.write(result.frame)
                results.append(result)
                if frame_callback is not None:
                    frame_callback(result, len(results), metadata.frame_count if output_path is not None else None)
            return results
        finally:
            if writer is not None:
                writer.release()
            if opened_here:
                self.reader.release()

    def statistics(self) -> dict:
        result = self.counting_engine.statistics()
        result["processed_frames"] = self._processed_frames
        result["average_inference_ms"] = self._total_inference_ms / self._processed_frames if self._processed_frames else 0.0
        return result

    def reset(self) -> None:
        self.history.clear()
        self.counting_engine.reset()
        self.crossing_detector.reset()
        if self.speed_tracker:
            self.speed_tracker.reset()
        self._processed_frames = 0
        self._total_inference_ms = 0.0
