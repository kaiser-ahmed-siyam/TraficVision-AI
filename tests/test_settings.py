"""Tests for validated TrafficVision settings."""

from pathlib import Path

import pytest

from config import load_settings


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_load_settings_uses_specification_defaults():
    settings = load_settings(project_root=PROJECT_ROOT)

    assert settings.application.name == "TrafficVision AI"
    assert settings.application.environment == "development"
    assert settings.model.name == "yolo11n.pt"
    assert settings.model.confidence == 0.35
    assert settings.model.iou == 0.50
    assert settings.model.image_size == 640
    assert settings.model.device == "auto"
    assert settings.tracking.algorithm == "bytetrack"
    assert settings.tracking.track_buffer == 30
    assert settings.video.frame_skip == 0
    assert settings.video.max_upload_mb == 100
    assert settings.video.max_duration_seconds == 300
    assert settings.counting.anchor == "bottom_center"
    assert settings.counting.hysteresis_pixels == 8
    assert settings.counting.minimum_track_age == 3
    assert settings.counting.cooldown_frames == 5
    assert settings.storage.database.name == "trafficvision.db"


def test_default_paths_are_project_relative(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    settings = load_settings(project_root=PROJECT_ROOT)

    assert settings.storage.database == PROJECT_ROOT / "trafficvision.db"


def test_invalid_settings_report_field_errors(tmp_path):
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text(
        """
application:
  name: TrafficVision AI
  environment: development
model:
  name: yolo11n.pt
  confidence: 2.0
  iou: 0.50
  image_size: 640
  device: auto
tracking:
  algorithm: bytetrack
  track_buffer: -1
video:
  frame_skip: 0
  max_upload_mb: 100
  max_duration_seconds: 300
counting:
  anchor: bottom_center
  hysteresis_pixels: 8
  minimum_track_age: 3
  cooldown_frames: 5
storage:
  database: trafficvision.db
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as error:
        load_settings(config_path=config_path, project_root=tmp_path)

    message = str(error.value)
    assert "model.confidence" in message
    assert "tracking.track_buffer" in message


def test_cloud_environment_disables_live_inputs():
    local = load_settings(project_root=PROJECT_ROOT, environment="development")
    cloud = load_settings(project_root=PROJECT_ROOT, environment="cloud")

    assert local.live_inputs_enabled is True
    assert cloud.live_inputs_enabled is False


def test_invalid_required_strings_report_field_errors(tmp_path):
    config_path = tmp_path / "missing-name.yaml"
    config_path.write_text(
        """
application:
  name: ""
  environment: development
model:
  name: ""
  confidence: 0.35
  iou: 0.50
  image_size: 640
  device: auto
tracking:
  algorithm: bytetrack
  track_buffer: 30
video:
  frame_skip: 0
  max_upload_mb: 100
  max_duration_seconds: 300
counting:
  anchor: bottom_center
  hysteresis_pixels: 8
  minimum_track_age: 3
  cooldown_frames: 5
storage:
  database: trafficvision.db
logging:
  level: INFO
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError) as error:
        load_settings(config_path=config_path, project_root=tmp_path)

    assert "application.name" in str(error.value)
    assert "model.name" in str(error.value)
