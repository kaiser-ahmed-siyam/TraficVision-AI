"""Supervision ByteTrack adapter."""

from __future__ import annotations

from config.vehicle_classes import COCO_VEHICLE_CLASSES
from core.schemas import Detection, Track


class ByteTrackTracker:
    def __init__(self, track_buffer: int = 30, confidence: float = 0.35):
        try:
            import supervision as sv
        except ImportError as exc:
            raise RuntimeError("Supervision is required for ByteTrack tracking") from exc
        self._sv = sv
        try:
            self._tracker = sv.ByteTrack(lost_track_buffer=track_buffer, track_activation_threshold=confidence)
        except TypeError:
            self._tracker = sv.ByteTrack(track_buffer=track_buffer, track_activation_threshold=confidence)

    def update(self, detections: list[Detection], frame=None) -> list[Track]:
        import numpy as np

        if not detections:
            self._tracker.update_with_detections(self._sv.Detections.empty())
            return []
        sv_detections = self._sv.Detections(
            xyxy=np.array([item.bbox for item in detections]),
            confidence=np.array([item.confidence for item in detections]),
            class_id=np.array([item.class_id for item in detections]),
        )
        tracked = self._tracker.update_with_detections(sv_detections)
        tracks: list[Track] = []
        tracker_ids = tracked.tracker_id if tracked.tracker_id is not None else []
        for index, track_id in enumerate(tracker_ids):
            class_id = int(tracked.class_id[index]) if tracked.class_id is not None else None
            class_name = COCO_VEHICLE_CLASSES.get(class_id, "unknown")
            confidence = float(tracked.confidence[index]) if tracked.confidence is not None else 0.0
            tracks.append(Track(int(track_id), tuple(float(value) for value in tracked.xyxy[index]), class_name, confidence, class_id))
        return tracks
