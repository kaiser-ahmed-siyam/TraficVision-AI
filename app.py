"""Streamlit entry point for TrafficVision AI."""

from __future__ import annotations

import os
from pathlib import Path

from config import load_settings
from core.line_manager import LineManager
from core.schemas import LineConfig
from database.repository import TrafficRepository
from dashboard.analytics_panel import render_analytics
from dashboard.history_panel import render_history
from dashboard.metrics import render_metrics
from dashboard.settings_panel import render_settings
from dashboard.sidebar import render_sidebar
from dashboard.video_panel import render_live_monitor, render_video_analysis
from utils.logger import configure_logging
from utils.video_utils import ensure_h264


def _process_uploaded_video(source: Path, selected_classes, confidence, line_position, direction, pixels_per_meter, frame_callback, settings):
    from core.counter import LineCrossingDetector
    from core.pipeline import TrafficPipeline
    from core.preprocessor import FramePreprocessor
    from core.speed_tracker import SpeedTracker
    from core.video_reader import VideoReader
    from models.detector import VehicleDetector
    from core.vehicle_tracker import VehicleTracker
    from visualization.frame_renderer import FrameRenderer

    if source.stat().st_size > settings.video.max_upload_mb * 1024 * 1024:
        raise ValueError(f"Video exceeds the {settings.video.max_upload_mb} MB upload limit")
    playable = ensure_h264(source)  # transcode AV1/HEVC/etc. to H.264 so OpenCV can read it
    detector = VehicleDetector(settings.model.name, settings.model.device, confidence, settings.model.iou, settings.model.image_size, selected_classes=selected_classes)
    reader = VideoReader(playable)
    if not reader.open():
        raise RuntimeError(reader.last_error or "Unable to open uploaded video")
    metadata = reader.get_metadata()
    if metadata.duration_seconds > settings.video.max_duration_seconds:
        reader.release()
        source.unlink(missing_ok=True)
        if playable != source:
            playable.unlink(missing_ok=True)
        raise ValueError(f"Video exceeds the {settings.video.max_duration_seconds} second duration limit")
    line_y = metadata.height * float(line_position) / 100.0
    line = LineConfig(
        "main_line",
        (0, line_y),
        (metadata.width, line_y),
        direction=direction,
        hysteresis_pixels=settings.counting.hysteresis_pixels,
    )
    repository = TrafficRepository(settings.storage.database)
    session_id = repository.create_session(str(source))
    speed_tracker = SpeedTracker(pixels_per_meter, settings.speed.smoothing_window, metadata.fps)
    pipeline = TrafficPipeline(
        reader,
        detector,
        VehicleTracker(track_buffer=settings.tracking.track_buffer, confidence=confidence),
        FramePreprocessor(settings.model.image_size),
        LineManager([line]),
        crossing_detector=LineCrossingDetector(
            settings.counting.minimum_track_age,
            settings.counting.cooldown_frames,
        ),
        renderer=FrameRenderer(),
        frame_skip=settings.video.frame_skip,
        track_buffer=settings.tracking.track_buffer,
        speed_tracker=speed_tracker,
    )
    output = source.with_name(f"{source.stem}_trafficvision.mp4")
    try:
        results = pipeline.run(output_path=output, frame_callback=frame_callback)
        for event in pipeline.counting_engine.events:
            repository.add_event(session_id, event)
        repository.save_statistics(session_id, pipeline.statistics())
        repository.finish_session(session_id)
        return output.read_bytes(), results, pipeline, session_id
    finally:
        repository.close()
        reader.release()
        source.unlink(missing_ok=True)
        if playable != source:
            playable.unlink(missing_ok=True)
        output.unlink(missing_ok=True)


def _run_live_source(source, max_frames, pixels_per_meter, frame_callback, settings):
    from core.counter import LineCrossingDetector
    from core.line_manager import LineManager
    from core.pipeline import TrafficPipeline
    from core.preprocessor import FramePreprocessor
    from core.speed_tracker import SpeedTracker
    from core.video_reader import VideoReader
    from models.detector import VehicleDetector
    from core.vehicle_tracker import VehicleTracker
    from visualization.frame_renderer import FrameRenderer

    reader = VideoReader(source)
    if not reader.open():
        raise RuntimeError(reader.last_error or "Unable to open live source")
    metadata = reader.get_metadata()
    line_y = metadata.height / 2 if metadata.height else 240
    line = LineConfig(
        "main_line",
        (0, line_y),
        (metadata.width or 640, line_y),
        hysteresis_pixels=settings.counting.hysteresis_pixels,
    )
    pipeline = TrafficPipeline(
        reader,
        VehicleDetector(settings.model.name, settings.model.device, settings.model.confidence, settings.model.iou, settings.model.image_size),
        VehicleTracker(track_buffer=settings.tracking.track_buffer, confidence=settings.model.confidence),
        FramePreprocessor(settings.model.image_size),
        LineManager([line]),
        crossing_detector=LineCrossingDetector(
            settings.counting.minimum_track_age,
            settings.counting.cooldown_frames,
        ),
        renderer=FrameRenderer(),
        frame_skip=settings.video.frame_skip,
        track_buffer=settings.tracking.track_buffer,
        speed_tracker=SpeedTracker(pixels_per_meter, settings.speed.smoothing_window, metadata.fps),
    )
    try:
        return pipeline.run(max_frames=max_frames, frame_callback=frame_callback)
    finally:
        reader.release()


def main() -> None:
    """Run the Streamlit dashboard."""
    import streamlit as st

    settings = load_settings(environment=os.getenv("TRAFFICVISION_ENV") or None)
    configure_logging(settings.logging.level)
    st.set_page_config(page_title="TrafficVision AI", page_icon="🚦", layout="wide")
    if "statistics" not in st.session_state:
        st.session_state.statistics = {"total_vehicles": 0, "by_class": {}, "by_direction": {}}
    if "events" not in st.session_state:
        st.session_state.events = []
    page = render_sidebar(settings)
    st.title("TrafficVision AI")
    st.caption("VEHICLE DETECTION & TRAFFIC ANALYTICS")
    if page == "Dashboard":
        render_metrics(st.session_state.statistics)
        st.info("Use Video Analysis to process an uploaded traffic video.")
    elif page == "Video Analysis":
        result = render_video_analysis(settings, lambda source, classes, confidence, line_position, direction, pixels_per_meter, callback: _process_uploaded_video(source, classes, confidence, line_position, direction, pixels_per_meter, callback, settings))
        if result:
            output, results, pipeline, session_id = result
            st.session_state.statistics = pipeline.statistics()
            st.session_state.events = pipeline.counting_engine.events
            st.session_state.session_id = session_id
            st.success(f"Processed {len(results)} frames")
            st.subheader("Processed video")
            st.video(output, format="video/mp4")
            st.download_button("Download processed video", output, "trafficvision_processed.mp4", "video/mp4")
            if results:
                st.caption("Preview of the final annotated frame")
                st.image(results[-1].frame, channels="BGR")
    elif page == "Live Monitor":
        live_results = render_live_monitor(settings, lambda source, max_frames, pixels_per_meter, callback: _run_live_source(source, max_frames, pixels_per_meter, callback, settings))
        if live_results:
            st.success(f"Live monitor processed {len(live_results)} frames")
    elif page == "Analytics":
        render_metrics(st.session_state.statistics)
        render_analytics(st.session_state.statistics, st.session_state.events)
    elif page == "Settings":
        render_settings(settings)
    elif page == "History":
        render_history(TrafficRepository(settings.storage.database))


if __name__ == "__main__":
    main()
