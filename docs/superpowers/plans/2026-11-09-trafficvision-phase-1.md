# TrafficVision AI Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the importable TrafficVision AI foundation: complete package layout, validated configuration, supported vehicle-class mapping, logging, project metadata, documentation, and Phase 1 tests—without implementing detection or video processing.

**Architecture:** Keep all future subsystems represented as lightweight, side-effect-free Python packages. Put typed configuration and YAML loading in `config`, logging in `utils`, and keep optional heavy runtime dependencies out of import-time code. Root metadata and Streamlit deployment settings describe the runtime without starting the application.

**Tech Stack:** Python 3.11.9, `dataclasses`, pathlib, PyYAML, pytest, Streamlit/Ultralytics/OpenCV dependency metadata, AGPL-3.0.

**Spec:** `docs/superpowers/specs/2026-11-09-trafficvision-phase-1-design.md`

## Global Constraints

- Python 3.11.9 is the target interpreter.
- YOLO11n, ByteTrack, OpenCV, Streamlit, Plotly, SQLite, and Pytest are the selected project technologies.
- CPU compatibility is mandatory; no GPU-only dependency may be required.
- Paths must be environment-independent and relative to the project root.
- Phase 1 must not load YOLO weights or implement detection, tracking, video reading, dashboard behavior, or database behavior.
- The existing Apache-2.0 license must be replaced with AGPL-3.0.
- `.venv/`, generated media, databases, and local environment files must not be committed.

## Review Focus

- Importing the foundation on a machine without optional CV packages should work; the package initializers must not eagerly import Ultralytics, OpenCV, Streamlit, or Plotly. Test: `test_expected_modules_import_without_optional_runtime_dependencies` in Task 1.
- A caller running from a different current working directory should still resolve the default YAML and database path from the project root. Test: `test_default_paths_are_project_relative` in Task 2.
- Invalid YAML types and out-of-range thresholds should fail with a readable field-specific error rather than a raw `KeyError` or `TypeError`. Test: `test_invalid_settings_report_field_errors` in Task 2.
- Repeated logger setup should not duplicate output handlers. Test: `test_configure_logging_is_idempotent` in Task 3.
- Cloud configuration must not accidentally enable local-only live inputs. Test: `test_cloud_environment_disables_live_inputs` in Task 2.

---

### Task 1: Create the importable repository scaffold

**Files:**
- Create: `app.py`
- Create: `config/__init__.py`
- Create: `models/__init__.py`
- Create: `core/__init__.py`
- Create: `visualization/__init__.py`
- Create: `analytics/__init__.py`
- Create: `database/__init__.py`
- Create: `dashboard/__init__.py`
- Create: `utils/__init__.py`
- Create: all module placeholders listed in the specification under `models/`, `core/`, `visualization/`, `analytics/`, `database/`, `dashboard/`, and `utils/`
- Create: `tests/conftest.py`
- Create: `tests/test_scaffold.py`
- Create: empty `.gitkeep` files in `data/input/`, `data/output/`, `data/samples/`, and `assets/`

**Interfaces:**
- Consumes: none.
- Produces: side-effect-free importable modules matching the specification's repository structure; `app.py` exposes a placeholder `main() -> None` that does not import Streamlit at module import time.

- [ ] **Step 1: Write the failing scaffold test**

  Add `test_expected_modules_import_without_optional_runtime_dependencies`, which imports each expected package/module with `importlib.import_module` and asserts no import raises. Add `test_app_exposes_main_entrypoint`, which imports `app` and asserts `callable(app.main)`.

- [ ] **Step 2: Run the scaffold test to verify it fails**

  Run: `python -m pytest tests/test_scaffold.py -v`

  Expected: FAIL because the package modules and `app.main` do not exist yet.

- [ ] **Step 3: Create the scaffold**

  Add only module docstrings, package initializers, and the no-op `main()` entrypoint. Do not add runtime imports or detection behavior. Keep test fixtures limited to repository-root path setup.

- [ ] **Step 4: Run the scaffold test to verify it passes**

  Run: `python -m pytest tests/test_scaffold.py -v`

  Expected: PASS with all scaffold imports successful.

- [ ] **Step 5: Commit the scaffold**

  ```powershell
  git add app.py config models core visualization analytics database dashboard utils tests data assets
  git commit -m "chore: create trafficvision package scaffold"
  ```

### Task 2: Implement typed configuration and environment rules

**Files:**
- Create: `config/settings.py`
- Create: `config/vehicle_classes.py`
- Create: `config/default_config.yaml`
- Modify: `config/__init__.py`
- Modify: `tests/conftest.py`
- Create: `tests/test_settings.py`
- Create: `tests/test_vehicle_classes.py`

**Interfaces:**
- Consumes: `config/default_config.yaml` from Task 1's project root.
- Produces: `ApplicationSettings`, `ModelSettings`, `TrackingSettings`, `VideoSettings`, `CountingSettings`, `StorageSettings`, and `Settings` frozen dataclasses; `load_settings(config_path: Path | None = None, project_root: Path | None = None, environment: str | None = None) -> Settings`; `COCO_VEHICLE_CLASSES: dict[int, str]`; `SUPPORTED_VEHICLE_CLASSES: tuple[str, ...]`.

- [ ] **Step 1: Write failing configuration tests**

  Add tests for:

  - `load_settings()` reads the exact default values from the specification: confidence `0.35`, IoU `0.50`, image size `640`, device `"auto"`, ByteTrack buffer `30`, frame skip `0`, upload limit `100`, duration `300`, anchor `"bottom_center"`, hysteresis `8`, minimum age `3`, cooldown `5`, and database `trafficvision.db`.
  - `test_default_paths_are_project_relative` changes the current directory to a temporary directory and asserts the resolved database path remains under the supplied project root.
  - `test_invalid_settings_report_field_errors` loads invalid confidence and negative buffer values and asserts `ValueError` includes both field names.
  - `test_cloud_environment_disables_live_inputs` loads with `environment="cloud"` and asserts `settings.live_inputs_enabled is False`, while development defaults to `True`.
  - `test_vehicle_class_mapping_matches_coco_vehicle_classes` asserts the exact mapping `{2: "car", 3: "motorcycle", 5: "bus", 7: "truck"}` and stable class order.

- [ ] **Step 2: Run configuration tests to verify they fail**

  Run: `python -m pytest tests/test_settings.py tests/test_vehicle_classes.py -v`

  Expected: FAIL because the settings API and vehicle mapping are not implemented.

- [ ] **Step 3: Implement the minimal settings API**

  Parse YAML with `yaml.safe_load`, normalize missing sections to clear validation errors, validate numeric ranges and supported values, resolve relative paths against `project_root`, and derive `live_inputs_enabled` from the environment (`cloud` disables it). Export the public dataclasses and loader from `config/__init__.py`. Keep YAML values exactly as specified.

- [ ] **Step 4: Run configuration tests to verify they pass**

  Run: `python -m pytest tests/test_settings.py tests/test_vehicle_classes.py -v`

  Expected: PASS with all default, path, validation, environment, and class-mapping assertions green.

- [ ] **Step 5: Commit configuration**

  ```powershell
  git add config tests/test_settings.py tests/test_vehicle_classes.py tests/conftest.py
  git commit -m "feat: add validated project configuration"
  ```

### Task 3: Add logging and project metadata

**Files:**
- Create: `utils/logger.py`
- Create: `tests/test_logger.py`
- Create: `pyproject.toml`
- Create: `requirements.txt`
- Create: `requirements-dev.txt`
- Create: `.gitignore`
- Create: `.streamlit/config.toml`
- Create: `THIRD_PARTY_NOTICES.md`
- Modify: `utils/__init__.py`

**Interfaces:**
- Consumes: `Settings` logging values from Task 2 only by name; logger setup must not require optional application dependencies.
- Produces: `configure_logging(level: str = "INFO", logger_name: str = "trafficvision") -> logging.Logger` with idempotent handler setup.

- [ ] **Step 1: Write the failing logging tests**

  Add `test_configure_logging_returns_named_logger`, asserting the logger name and effective level, and `test_configure_logging_is_idempotent`, asserting repeated calls leave one managed stream handler attached.

- [ ] **Step 2: Run logging tests to verify they fail**

  Run: `python -m pytest tests/test_logger.py -v`

  Expected: FAIL because `configure_logging` does not exist.

- [ ] **Step 3: Implement logging and metadata**

  Configure a standard formatter, mark the handler with a private attribute so repeated setup can find it, and avoid mutating unrelated root handlers. Add Python 3.11 project metadata, pytest configuration, pinned runtime dependencies for the selected stack, development-only pytest/coverage tooling, ignore rules for `.venv/`, caches, databases, generated media, and secrets, Streamlit server/theme settings from the specification, and third-party licensing notes.

- [ ] **Step 4: Run logging tests and the full foundation suite**

  Run: `python -m pytest -v`

  Expected: PASS with all foundation tests green and no optional model import triggered.

- [ ] **Step 5: Commit metadata**

  ```powershell
  git add utils pyproject.toml requirements.txt requirements-dev.txt .gitignore .streamlit THIRD_PARTY_NOTICES.md tests/test_logger.py
  git commit -m "chore: add project metadata and logging"
  ```

### Task 4: Add documentation and AGPL-3.0 licensing

**Files:**
- Modify: `README.md`
- Replace: `LICENSE`
- Create: `docs/` links/usage content as needed, without duplicating the approved design or plan

**Interfaces:**
- Consumes: the configuration names and Phase 1 behavior produced by Tasks 1–3.
- Produces: user-facing setup instructions that describe only verified Phase 1 behavior, future phase boundaries, local/cloud constraints, and the AGPL-3.0 licensing/attribution policy.

- [ ] **Step 1: Write the documentation acceptance checks**

  Add `tests/test_project_files.py` to assert that README mentions Python 3.11, `streamlit run app.py`, `pytest`, CPU compatibility, cloud live-input limitations, and the Phase 1 status; assert that LICENSE contains the AGPL-3.0 identifier and `THIRD_PARTY_NOTICES.md` exists.

- [ ] **Step 2: Run documentation checks to verify they fail**

  Run: `python -m pytest tests/test_project_files.py -v`

  Expected: FAIL because the README/license still describe the old repository state.

- [ ] **Step 3: Update documentation and license**

  Replace the current Apache license text with the standard GNU AGPL-3.0 text, document the project structure and Phase 1 setup, explain that YOLO/ByteTrack/video processing are later phases, and include the deployment caveat that webcam/RTSP are local-only. Do not claim unimplemented features are complete.

- [ ] **Step 4: Run the full suite and import validation**

  Run: `python -m pytest -v; python -c "import app; from config import load_settings; print(load_settings())"`

  Expected: pytest exits `0`; the import command exits `0` and prints a settings object without downloading weights or opening a video device.

- [ ] **Step 5: Commit documentation and license**

  ```powershell
  git add README.md LICENSE tests/test_project_files.py docs
  git commit -m "docs: document phase one and adopt agpl license"
  ```

## Final verification

After all tasks, run:

```powershell
python -m pytest -v
python -m compileall -q app.py config models core visualization analytics database dashboard utils tests
python -c "import app; from config import load_settings; settings = load_settings(); print(settings.application.name)"
```

Expected: all tests pass, compilation exits `0`, and the final command prints `TrafficVision AI`.

## Spec coverage self-review

- Repository structure and imports: Task 1.
- Centralized values, validation, paths, local/cloud behavior: Task 2.
- Vehicle mapping: Task 2.
- Logging: Task 3.
- Requirements, pyproject, ignore rules, Streamlit config: Task 3.
- README, AGPL-3.0, third-party notices: Task 4.
- YOLO, tracking, video input, database, dashboard, and analytics are explicitly deferred to later phases per the approved Phase 1 design.
