# TrafficVision AI

TrafficVision AI is a modular computer-vision project for detecting,
tracking, classifying, and counting vehicles crossing a configurable virtual
line in traffic videos and camera streams.

## Current status

The complete first implementation is present, including:

- Uploaded-file, webcam, and RTSP-capable OpenCV reading adapters.
- YOLO11n detection and Supervision ByteTrack adapters with CPU fallback
  device selection.
- Track history, configurable virtual lines, hysteresis, direction detection,
  minimum track age, and duplicate prevention.
- Real-time annotated-frame updates with per-track speed estimates and local
  webcam/RTSP monitoring.
- An independent pipeline that supports injected fake detectors/trackers for
  synthetic tests without model weights.
- OpenCV annotations, Plotly analytics, CSV reports, SQLite session history,
  and Streamlit dashboard sections.

Model weights are still downloaded on first real inference; the automated test
suite intentionally uses synthetic detectors so it remains CPU-only and does
not require a network download.

### Speed calibration

Speed is estimated from bottom-center track displacement. Set `speed.pixels_per_meter`
in `config/default_config.yaml` or use the Video Analysis calibration control.
The displayed km/h value is an estimate and requires camera-specific
calibration; it is not radar-grade speed measurement.

## Requirements

- Python 3.11.9 (the project targets Python 3.11 and does not require a GPU).
- Windows PowerShell, macOS/Linux shell, or another environment capable of
  running Python and OpenCV.

## Local setup

In Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

Load and inspect the Phase 1 configuration:

```powershell
py -3.11 -c "from config import load_settings; print(load_settings())"
```

Run the foundation tests:

```powershell
py -3.11 -m pytest -v
```

The eventual local dashboard will be started with:

```powershell
streamlit run app.py
```

## Configuration

Defaults live in [`config/default_config.yaml`](config/default_config.yaml),
and validation/loading is implemented in `config/settings.py`. Relative paths
are resolved from the project root rather than the current working directory.
Use `environment=\"cloud\"` when loading settings for the public deployment;
this disables webcam and RTSP inputs. Local webcam and RTSP support is
local-only because a public cloud process cannot reach a
visitor's private camera or CCTV network.

## Planned architecture

The implementation will keep the computer-vision engine independent from the
dashboard:

1. Video input and frame preprocessing.
2. YOLO11n vehicle detection on CPU or CUDA when available.
3. ByteTrack identity tracking.
4. Bottom-center track history and hysteresis-aware line crossing.
5. SQLite events, statistics, CSV reports, and Plotly analytics.
6. Streamlit dashboard and local live-monitor mode.

The public Streamlit Community Cloud demo will prioritize short uploaded
videos, enforce upload/duration limits, and release temporary data. It will
not promise continuous high-speed CCTV monitoring.

## Repository layout

```text
app.py                 Streamlit entry point
config/                Typed settings and vehicle classes
models/                Detection/tracking integrations
core/                  Video pipeline and counting engine
visualization/         Annotated-frame rendering
analytics/             Statistics and reports
database/              SQLite persistence
dashboard/             Streamlit UI components
utils/                 Shared helpers and logging
tests/                 Automated foundation and future pipeline tests
```

## License

TrafficVision AI is released under the GNU Affero General Public License,
version 3. See [`LICENSE`](LICENSE) and
[`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) for project and dependency
licensing information. Ultralytics usage and model distribution may require
AGPL-3.0 compliance or a separate commercial license; review the applicable
upstream terms before redistribution.
