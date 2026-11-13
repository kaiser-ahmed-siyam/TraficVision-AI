# TrafficVision AI Complete Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan in one continuous pass. The user requested implementation first and a final test run at the end.

**Goal:** Implement the remaining TrafficVision AI engine, counting, persistence, analytics, visualization, Streamlit dashboard, scripts, and integration tests on top of the Phase 1 foundation.

**Architecture:** Keep the pure counting and data layers independent of optional CV/UI dependencies. OpenCV, Ultralytics, Supervision, Streamlit, and Plotly are imported lazily or behind clear adapters. The pipeline accepts injectable detector/tracker components so synthetic tests can exercise counting without model weights.

**Tech Stack:** Python 3.11, OpenCV, NumPy, Ultralytics YOLO11n, Supervision ByteTrack, SQLite, pandas, Plotly, Streamlit, pytest.

**Spec:** `docs/superpowers/specs/2026-11-09-trafficvision-phase-1-design.md` plus the complete TrafficVision AI implementation specification supplied by the user.

## Global constraints

- CPU compatibility is mandatory; CUDA is optional.
- Uploaded videos, webcam, and RTSP use one pipeline; webcam/RTSP are local-only.
- Vehicle classes are COCO IDs 2, 3, 5, and 7.
- Count tracks using bottom-center coordinates, signed-distance line crossing, hysteresis, direction, minimum age, cooldown, and per-line deduplication.
- Do not load an entire video into memory.
- Do not require model weights for unit/integration tests.
- SQLite queries are parameterized and event IDs are unique.
- Streamlit reruns must not share mutable tracker state between users.

## Implementation units

1. Shared schemas, video reader, preprocessing, detection, and tracking adapters.
2. Track history, line configuration, crossing detection, counting, and pipeline.
3. Frame rendering, statistics, report generation, SQLite repository, and scripts.
4. Streamlit dashboard integration and cloud/local safeguards.
5. Synthetic tests and final verification.

## One-pass execution note

The implementation will be completed before the requested final verification pass. Tests will be added alongside the implementation but run together only after all units are present, as explicitly requested by the user.
