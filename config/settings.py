"""Validated, environment-independent application configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ApplicationSettings:
    """Application identity and runtime environment."""

    name: str
    environment: str


@dataclass(frozen=True)
class ModelSettings:
    """Object-detection model settings."""

    name: str
    confidence: float
    iou: float
    image_size: int
    device: str


@dataclass(frozen=True)
class TrackingSettings:
    """Multi-object tracking settings."""

    algorithm: str
    track_buffer: int


@dataclass(frozen=True)
class VideoSettings:
    """Video input and processing limits."""

    frame_skip: int
    max_upload_mb: int
    max_duration_seconds: int


@dataclass(frozen=True)
class CountingSettings:
    """Virtual-line counting settings."""

    anchor: str
    hysteresis_pixels: int
    minimum_track_age: int
    cooldown_frames: int


@dataclass(frozen=True)
class StorageSettings:
    """Persistent storage paths."""

    database: Path


@dataclass(frozen=True)
class LoggingSettings:
    """Application logging settings."""

    level: str


@dataclass(frozen=True)
class SpeedSettings:
    """Calibration and smoothing for track-speed estimates."""

    enabled: bool
    pixels_per_meter: float
    smoothing_window: int


@dataclass(frozen=True)
class Settings:
    """Complete validated application settings."""

    project_root: Path
    application: ApplicationSettings
    model: ModelSettings
    tracking: TrackingSettings
    video: VideoSettings
    counting: CountingSettings
    storage: StorageSettings
    logging: LoggingSettings
    speed: SpeedSettings

    @property
    def live_inputs_enabled(self) -> bool:
        """Return whether webcam and RTSP inputs are available."""

        return self.application.environment != "cloud"


def _section(data: dict[str, Any], name: str, errors: list[str]) -> dict[str, Any]:
    value = data.get(name)
    if not isinstance(value, dict):
        errors.append(f"{name}: expected a mapping")
        return {}
    return value


def _required(section: dict[str, Any], section_name: str, key: str, errors: list[str]) -> Any:
    if key not in section:
        errors.append(f"{section_name}.{key}: value is required")
        return None
    return section[key]


def _string(section: dict[str, Any], section_name: str, key: str, errors: list[str]) -> str:
    value = _required(section, section_name, key, errors)
    if value is None:
        return ""
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{section_name}.{key}: expected a non-empty string")
        return ""
    return value.strip()


def _number(
    section: dict[str, Any],
    section_name: str,
    key: str,
    errors: list[str],
    *,
    integer: bool = False,
    minimum: float | None = None,
    maximum: float | None = None,
) -> int | float:
    value = _required(section, section_name, key, errors)
    valid_number = isinstance(value, (int, float)) and not isinstance(value, bool)
    if not valid_number or (integer and not isinstance(value, int)):
        errors.append(f"{section_name}.{key}: expected a number")
        return 0
    if minimum is not None and value < minimum:
        errors.append(f"{section_name}.{key}: must be >= {minimum}")
    if maximum is not None and value > maximum:
        errors.append(f"{section_name}.{key}: must be <= {maximum}")
    return value


def load_settings(
    config_path: Path | None = None,
    project_root: Path | None = None,
    environment: str | None = None,
) -> Settings:
    """Load and validate settings from YAML.

    Relative configuration and database paths are resolved against
    ``project_root`` so callers do not depend on their current directory.
    """

    root = Path(project_root or Path(__file__).resolve().parents[1]).resolve()
    path = Path(config_path) if config_path is not None else root / "config" / "default_config.yaml"
    if not path.is_absolute():
        path = root / path

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"Unable to read configuration file {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Unable to parse configuration file {path}: {exc}") from exc

    if not isinstance(raw, dict):
        raise ValueError("Configuration root: expected a mapping")

    errors: list[str] = []
    application = _section(raw, "application", errors)
    model = _section(raw, "model", errors)
    tracking = _section(raw, "tracking", errors)
    video = _section(raw, "video", errors)
    counting = _section(raw, "counting", errors)
    storage = _section(raw, "storage", errors)
    logging = _section(raw, "logging", errors)
    speed = raw.get("speed", {})
    if not isinstance(speed, dict):
        errors.append("speed: expected a mapping")
        speed = {}

    application_name = _string(application, "application", "name", errors)
    app_environment = environment or _string(application, "application", "environment", errors)
    if app_environment not in {"development", "cloud", "production"}:
        errors.append("application.environment: expected development, cloud, or production")

    model_name = _string(model, "model", "name", errors)
    model_device = _string(model, "model", "device", errors)
    tracking_algorithm = _string(tracking, "tracking", "algorithm", errors)
    database_value = _string(storage, "storage", "database", errors)
    model_confidence = _number(model, "model", "confidence", errors, minimum=0.0, maximum=1.0)
    model_iou = _number(model, "model", "iou", errors, minimum=0.0, maximum=1.0)
    model_image_size = _number(model, "model", "image_size", errors, integer=True, minimum=1)
    track_buffer = _number(tracking, "tracking", "track_buffer", errors, integer=True, minimum=0)
    frame_skip = _number(video, "video", "frame_skip", errors, integer=True, minimum=0)
    max_upload_mb = _number(video, "video", "max_upload_mb", errors, integer=True, minimum=1)
    max_duration = _number(video, "video", "max_duration_seconds", errors, integer=True, minimum=1)
    hysteresis = _number(counting, "counting", "hysteresis_pixels", errors, integer=True, minimum=0)
    minimum_age = _number(counting, "counting", "minimum_track_age", errors, integer=True, minimum=0)
    cooldown = _number(counting, "counting", "cooldown_frames", errors, integer=True, minimum=0)

    anchor = _string(counting, "counting", "anchor", errors)
    if anchor not in {"bottom_center"}:
        errors.append("counting.anchor: expected bottom_center")
    level = _string(logging, "logging", "level", errors).upper()
    if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
        errors.append("logging.level: expected a standard logging level")

    speed_enabled = speed.get("enabled", True)
    pixels_per_meter = speed.get("pixels_per_meter", 10.0)
    smoothing_window = speed.get("smoothing_window", 5)
    if not isinstance(speed_enabled, bool):
        errors.append("speed.enabled: expected a boolean")
    if not isinstance(pixels_per_meter, (int, float)) or pixels_per_meter <= 0:
        errors.append("speed.pixels_per_meter: must be greater than zero")
    if not isinstance(smoothing_window, int) or smoothing_window < 1:
        errors.append("speed.smoothing_window: must be a positive integer")

    if errors:
        raise ValueError("Invalid configuration:\n- " + "\n- ".join(errors))

    database = Path(database_value)
    if not database.is_absolute():
        database = root / database

    return Settings(
        project_root=root,
        application=ApplicationSettings(application_name, app_environment),
        model=ModelSettings(
            model_name,
            float(model_confidence),
            float(model_iou),
            int(model_image_size),
            model_device,
        ),
        tracking=TrackingSettings(tracking_algorithm, int(track_buffer)),
        video=VideoSettings(int(frame_skip), int(max_upload_mb), int(max_duration)),
        counting=CountingSettings(anchor, int(hysteresis), int(minimum_age), int(cooldown)),
        storage=StorageSettings(database),
        logging=LoggingSettings(level),
        speed=SpeedSettings(bool(speed_enabled), float(pixels_per_meter), int(smoothing_window)),
    )


__all__ = [
    "ApplicationSettings",
    "CountingSettings",
    "LoggingSettings",
    "ModelSettings",
    "Settings",
    "SpeedSettings",
    "StorageSettings",
    "TrackingSettings",
    "VideoSettings",
    "load_settings",
]
