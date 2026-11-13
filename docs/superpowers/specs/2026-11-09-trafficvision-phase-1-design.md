# TrafficVision AI Phase 1 Design

## Intent

Establish a reliable, importable foundation for TrafficVision AI, a CPU-compatible traffic video analysis application that will later detect, track, and count vehicles crossing configurable lines. Phase 1 makes the repository structure, configuration contract, development dependencies, documentation, and logging conventions explicit so later modules can be added without changing their public assumptions.

## Goals

- Create the complete package layout described by the project specification.
- Centralize validated application, model, tracking, video, counting, and storage settings.
- Define the supported COCO vehicle classes in one authoritative module.
- Provide environment-independent paths and development/cloud configuration hooks.
- Add reproducible runtime and development dependency files for Python 3.11.9.
- Establish logging and a minimal import-validation test.
- Document Windows local setup, Phase 1 scope, future pipeline phases, and AGPL-3.0 licensing.

## Non-goals

- No YOLO model loading or inference.
- No ByteTrack integration.
- No video decoding, webcam, or RTSP behavior.
- No Streamlit dashboard implementation.
- No database schema or analytics pipeline.
- No model weights, sample recordings, or generated media committed to the repository.

## Constraints

- Python 3.11.9 is the target interpreter.
- The application must remain CPU-compatible and suitable for Streamlit Community Cloud.
- Paths must resolve relative to the repository/project root rather than a machine-specific absolute path.
- The existing Apache-2.0 license is replaced with AGPL-3.0 to match the finalized project specification and the planned Ultralytics-based distribution model.
- The existing untracked `.venv/` is user environment state and must remain unmodified and ignored.

## Approaches considered

### Strict scaffold (selected)

Create the full package tree now, with importable package initializers and configuration/logging foundations only. This matches the specification's repository contract and lets later phases add implementations without repeatedly restructuring imports. The tradeoff is a larger initial file tree containing intentional placeholders.

### Minimal foundation

Create only the configuration package, root packaging files, tests, and documentation, then add other directories per phase. This produces a smaller first diff but postpones structural/import validation and makes the repository less faithful to the agreed architecture.

The strict scaffold is selected because the requested Phase 1 explicitly includes project-structure creation and the project has no existing implementation to preserve.

## Design decisions

- `config/settings.py` will expose typed settings objects plus a loader that reads `config/default_config.yaml`, applies environment overrides where useful, and validates ranges with readable errors.
- `config/vehicle_classes.py` will contain the exact COCO IDs `{2, 3, 5, 7}` and helper constants used by future detection code.
- Package `__init__.py` files will be lightweight and side-effect free; optional heavy dependencies will not be imported at package-import time.
- `utils/logger.py` will configure named application logging without requiring Streamlit, OpenCV, Ultralytics, or a database.
- `pyproject.toml` will define project metadata, pytest configuration, and formatting/linting-compatible defaults without introducing extra tool requirements beyond the stated stack.
- Runtime dependencies will be separated from development-only dependencies. Versions will be pinned to stable Python 3.11-compatible releases chosen for the initial environment.
- The root README will describe only what Phase 1 actually delivers and will clearly mark later capabilities as planned.

## Phase 1 completion checks

1. The expected package tree exists and imports without loading a model.
2. A default settings instance loads successfully from the YAML configuration.
3. Invalid settings produce a readable validation error.
4. Logging can be initialized more than once without duplicate handlers.
5. `python -m pytest` passes the foundation tests.
6. The repository documentation, ignore rules, dependency files, and AGPL license are present.

## Builder decisions left open

The implementer may choose the smallest typed configuration representation that satisfies the checks above, provided public names remain stable for later phases. Dependency patch versions may be adjusted if the Python 3.11 environment rejects a pinned release; any such adjustment must be recorded in the implementation ledger.
