# Real-time Speed Annotation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan in the current workspace.

**Goal:** Add live annotated-frame updates and calibrated per-track speed estimates to uploaded and local live processing.

**Architecture:** A pure `SpeedTracker` consumes existing track anchors and frame timestamps. `TrafficPipeline` updates it before rendering, `FrameRenderer` adds speed labels, and Streamlit supplies frame/progress callbacks without changing the core engine’s independence from UI.

**Tech Stack:** Python 3.11, NumPy/OpenCV, Streamlit, pytest.

**Spec:** `docs/superpowers/specs/2026-11-09-realtime-speed-annotation-design.md`

## Tasks

1. Add speed configuration and a timestamp-based `SpeedTracker` with smoothing and reset behavior.
2. Integrate speed estimates into pipeline results and tracking overlays.
3. Add Streamlit live frame callbacks, calibration controls, and local webcam/RTSP monitoring.
4. Add synthetic speed/pipeline tests and run the complete suite.
