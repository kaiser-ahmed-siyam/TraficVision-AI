"""Tests for the importable repository scaffold."""

import importlib


EXPECTED_MODULES = (
    "config",
    "config.settings",
    "config.vehicle_classes",
    "models",
    "models.detector",
    "models.tracker",
    "models.model_loader",
    "core",
    "core.video_reader",
    "core.frame_processor",
    "core.preprocessor",
    "core.vehicle_detector",
    "core.vehicle_classifier",
    "core.vehicle_tracker",
    "core.track_history",
    "core.line_manager",
    "core.line_crossing",
    "core.counting_engine",
    "core.counter",
    "core.pipeline",
    "core.schemas",
    "visualization",
    "visualization.bounding_boxes",
    "visualization.tracking_visualizer",
    "visualization.line_visualizer",
    "visualization.frame_renderer",
    "analytics",
    "analytics.statistics",
    "analytics.charts",
    "analytics.report_generator",
    "database",
    "database.db",
    "database.models",
    "database.repository",
    "dashboard",
    "dashboard.sidebar",
    "dashboard.video_panel",
    "dashboard.metrics",
    "dashboard.analytics_panel",
    "dashboard.settings_panel",
    "dashboard.history_panel",
    "utils",
    "utils.logger",
    "utils.helpers",
    "utils.performance",
    "utils.file_manager",
)


def test_expected_modules_import_without_optional_runtime_dependencies():
    for module_name in EXPECTED_MODULES:
        importlib.import_module(module_name)


def test_app_exposes_main_entrypoint():
    app = importlib.import_module("app")

    assert callable(app.main)
