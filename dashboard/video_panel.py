"""Uploaded-video controls and pipeline execution."""

from __future__ import annotations

import tempfile
from pathlib import Path


def render_video_analysis(settings, process_callback=None):
    import streamlit as st

    st.subheader("Upload and process video")
    uploaded = st.file_uploader("Choose an MP4, AVI, or MOV video", type=["mp4", "avi", "mov"])
    if uploaded is None:
        st.info("Upload a short traffic video to begin.")
        return None
    if uploaded.size and uploaded.size > settings.video.max_upload_mb * 1024 * 1024:
        st.error(f"Video exceeds the {settings.video.max_upload_mb} MB upload limit.")
        return None
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded.name).suffix) as handle:
        handle.write(uploaded.getbuffer())
        source = Path(handle.name)
    st.video(uploaded)
    classes = st.multiselect("Vehicle classes", ["car", "motorcycle", "bus", "truck"], default=["car", "motorcycle", "bus", "truck"])
    confidence = st.slider("Confidence", 0.05, 0.95, float(settings.model.confidence), 0.05)
    line_position = st.slider("Horizontal counting line position (%)", 10, 90, 50)
    direction = st.selectbox("Crossing direction", ["both", "a_to_b", "b_to_a"])
    pixels_per_meter = st.number_input("Speed calibration (pixels per meter)", min_value=0.1, value=float(settings.speed.pixels_per_meter), step=0.5)
    if st.button("Start processing", type="primary") and process_callback:
        live_preview = st.empty()
        live_status = st.empty()
        progress = st.progress(0.0, text="Processing frames...")

        def on_frame(result, processed_count, total_frames):
            live_preview.image(result.frame, channels="BGR")
            live_status.caption(f"Detections: {len(result.detections)} · Tracks: {len(result.tracks)} · Frame: {processed_count}")
            if total_frames:
                progress.progress(min(1.0, processed_count / total_frames), text=f"Processing frame {processed_count}/{total_frames}")
            else:
                progress.progress(0.0, text=f"Processing frame {processed_count}")

        with st.spinner("Processing video..."):
            return process_callback(source, classes, confidence, line_position, direction, pixels_per_meter, on_frame)
    return None


def render_live_monitor(settings, process_callback=None):
    import streamlit as st

    st.subheader("Local live monitor")
    if not settings.live_inputs_enabled:
        st.warning("Webcam and RTSP inputs are disabled in cloud mode; run TrafficVision AI locally for live monitoring.")
        return
    source_type = st.radio("Source", ["Webcam", "RTSP"])
    source = 0 if source_type == "Webcam" else st.text_input("RTSP URL")
    max_frames = st.number_input("Maximum frames for this run", min_value=1, value=1000, step=100)
    pixels_per_meter = st.number_input("Speed calibration (pixels per meter)", min_value=0.1, value=float(settings.speed.pixels_per_meter), step=0.5, key="live_pixels_per_meter")
    if st.button("Start live monitor", type="primary") and process_callback and (source_type == "Webcam" or source):
        preview = st.empty()
        status = st.empty()

        def on_frame(result, processed_count, total_frames):
            preview.image(result.frame, channels="BGR")
            status.caption(f"Live frame {processed_count} · {result.performance.processing_fps:.1f} FPS")

        return process_callback(source, int(max_frames), float(pixels_per_meter), on_frame)
