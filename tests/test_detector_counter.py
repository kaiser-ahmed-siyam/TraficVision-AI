"""Regression tests for detector output handling and counting state."""

import numpy as np

from core.counter import CountingEngine, LineCrossingDetector
from core.schemas import LineConfig, Track
from models.detector import VehicleDetector


class _Boxes:
    xyxy = np.array([[10.0, 20.0, 30.0, 50.0], [0.0, 0.0, 5.0, 5.0]])
    cls = np.array([2.0, 0.0])
    conf = np.array([0.91, 0.99])


class _Result:
    boxes = _Boxes()


class _Model:
    def __init__(self):
        self.calls = []

    def predict(self, **kwargs):
        self.calls.append(kwargs)
        return [_Result()]


def _track(track_id, bottom_y, age=1):
    return Track(track_id, (40, bottom_y - 20, 60, bottom_y), "car", 0.9, 2, age)


def test_detector_accepts_numpy_model_outputs_and_keyword_source():
    model = _Model()
    detector = VehicleDetector(model=model)

    detections = detector.detect(np.zeros((80, 100, 3), dtype=np.uint8))

    assert len(detections) == 1
    assert detections[0].class_name == "car"
    assert detections[0].bbox == (10.0, 20.0, 30.0, 50.0)
    assert model.calls[0]["source"].shape == (80, 100, 3)


def test_detector_normalizes_selected_class_names():
    detector = VehicleDetector(model=_Model(), selected_classes=[" BUS "])

    detections = detector.filter_vehicles(
        [{"class_id": 5, "class_name": "bus"}, {"class_id": 2, "class_name": "car"}],
        detector.selected_classes,
    )

    assert [item["class_name"] for item in detections] == ["bus"]


def test_counter_rebaselines_when_line_geometry_changes():
    detector = LineCrossingDetector(minimum_track_age=1, cooldown_frames=0)
    original = LineConfig("main_line", (0, 50), (100, 50), hysteresis_pixels=2)
    moved = LineConfig("main_line", (0, 20), (100, 20), hysteresis_pixels=2)

    assert detector.update(_track(1, 40), original, 1) is None
    assert detector.update(_track(1, 40, age=2), moved, 2) is None
    assert detector.update(_track(1, 45, age=3), moved, 3) is None
    event = detector.update(_track(1, 5, age=4), moved, 4)
    assert event is not None
    assert event.direction == "B_TO_A"


def test_expired_track_id_can_be_counted_again_for_a_new_vehicle():
    detector = LineCrossingDetector(minimum_track_age=1, cooldown_frames=0)
    engine = CountingEngine()
    line = LineConfig("main_line", (0, 50), (100, 50), hysteresis_pixels=2)

    detector.update(_track(7, 40), line, 1)
    first = detector.update(_track(7, 60, age=2), line, 2)
    assert first is not None
    assert engine.add_event(first) is True

    detector.forget_track(7)
    engine.forget_track(7)
    detector.update(_track(7, 40, age=1), line, 10)
    second = detector.update(_track(7, 60, age=2), line, 11)

    assert second is not None
    assert engine.add_event(second) is True
    assert engine.total == 2
