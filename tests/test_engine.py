"""Synthetic engine and crossing tests that do not require model weights."""

import numpy as np

from analytics.report_generator import events_to_csv
from core.counting_engine import CountingEngine
from core.line_crossing import LineCrossingDetector, signed_distance
from core.line_manager import LineManager
from core.pipeline import TrafficPipeline
from core.preprocessor import FramePreprocessor
from core.schemas import Detection, LineConfig, Track
from core.track_history import TrackHistory, bottom_center
from models.detector import VehicleDetector


LINE = LineConfig("main_line", (0, 50), (100, 50), hysteresis_pixels=2)


def track(track_id, bottom_y, age=3):
    return Track(track_id, (40, bottom_y - 20, 60, bottom_y), "car", 0.9, 2, age)


def test_signed_distance_and_direction_crossing_are_correct():
    assert signed_distance((50, 40), LINE) < 0
    assert signed_distance((50, 60), LINE) > 0
    detector = LineCrossingDetector(minimum_track_age=3, cooldown_frames=0)

    assert detector.update(track(1, 40, 3), LINE, 1) is None
    event = detector.update(track(1, 60, 4), LINE, 2, 100.0)

    assert event is not None
    assert event.direction == "A_TO_B"
    assert detector.update(track(1, 40, 5), LINE, 3) is None


def test_hysteresis_and_minimum_age_prevent_false_events():
    detector = LineCrossingDetector(minimum_track_age=3, cooldown_frames=0)

    assert detector.update(track(1, 40, 1), LINE, 1) is None
    assert detector.update(track(1, 51, 2), LINE, 2) is None
    assert detector.update(track(1, 60, 3), LINE, 3) is None


def test_counting_engine_deduplicates_track_line_events():
    detector = LineCrossingDetector(minimum_track_age=1, cooldown_frames=0)
    engine = CountingEngine()
    first = detector.update(track(9, 40, 1), LINE, 1)
    event = detector.update(track(9, 60, 2), LINE, 2)

    assert first is None
    assert event is not None
    assert engine.add_event(event) is True
    assert engine.add_event(event) is False
    assert engine.statistics()["total_vehicles"] == 1


def test_track_history_stores_bottom_center_and_resets():
    history = TrackHistory(max_length=2)
    assert bottom_center((0, 10, 20, 30)) == (10.0, 30.0)
    history.update(track(1, 40), 4)
    history.update(track(1, 45), 5)
    history.update(track(1, 50), 6)

    assert history.age(1) == 3
    assert len(history.get(1).positions) == 2
    history.clear()
    assert history.get(1) is None


def test_track_history_prunes_only_after_missing_buffer():
    history = TrackHistory(max_length=2)
    history.update(track(2, 40), 1)
    history.remove_missing(set(), current_frame=2, max_missing=2)
    assert history.get(2) is not None
    history.remove_missing(set(), current_frame=4, max_missing=2)
    assert history.get(2) is None


def test_pipeline_counts_synthetic_crossing():
    class FakeDetector:
        def __init__(self):
            self.index = 0

        def detect(self, frame):
            bottom = 40 if self.index < 2 else 60
            self.index += 1
            return [Detection((40, bottom - 20, 60, bottom), 2, "car", 0.95)]

    class FakeTracker:
        def update(self, detections, frame):
            return [Track(5, detections[0].bbox, "car", detections[0].confidence, 2)]

    pipeline = TrafficPipeline(
        detector=FakeDetector(),
        tracker=FakeTracker(),
        preprocessor=FramePreprocessor(target_size=0),
        line_manager=LineManager([LINE]),
        crossing_detector=LineCrossingDetector(minimum_track_age=1, cooldown_frames=0),
    )
    results = [pipeline.process_frame(np.zeros((100, 100, 3), dtype=np.uint8), index) for index in range(3)]

    assert sum(len(result.crossing_events) for result in results) == 1
    assert pipeline.statistics()["total_vehicles"] == 1


def test_detector_filters_only_supported_classes():
    detector = VehicleDetector(model=object())
    detections = [Detection((0, 0, 1, 1), 2, "car", 0.9), Detection((0, 0, 1, 1), 1, "person", 0.9)]

    assert detector.filter_vehicles(detections) == [detections[0]]


def test_selected_vehicle_classes_are_applied():
    detector = VehicleDetector(model=object(), selected_classes=["bus"])
    detections = [
        Detection((0, 0, 1, 1), 2, "car", 0.9),
        Detection((0, 0, 1, 1), 5, "bus", 0.9),
    ]

    assert [item.class_name for item in detector.filter_vehicles(detections, detector.selected_classes)] == ["bus"]


def test_preprocessor_preserves_aspect_and_restores_coordinates():
    frame = np.zeros((100, 200, 3), dtype=np.uint8)
    preprocessor = FramePreprocessor(target_size=100)
    processed = preprocessor.process(frame)

    assert processed.shape[:2] == (50, 100)
    assert preprocessor.restore_bbox((10, 10, 20, 20)) == (20.0, 20.0, 40.0, 40.0)


def test_csv_report_contains_crossing_event():
    detector = LineCrossingDetector(minimum_track_age=1, cooldown_frames=0)
    detector.update(track(4, 40, 1), LINE, 1)
    event = detector.update(track(4, 60, 2), LINE, 2)

    report = events_to_csv([event])
    assert "event_id,track_id,line_id,vehicle_class,direction" in report
    assert "4,main_line,car,A_TO_B" in report


def test_event_dict_and_statistics_use_specification_names():
    detector = LineCrossingDetector(minimum_track_age=1, cooldown_frames=0)
    engine = CountingEngine()
    detector.update(track(7, 40, 1), LINE, 1)
    event = detector.update(track(7, 60, 2), LINE, 2)
    engine.add_event(event)

    assert event.to_dict()["vehicle_class"] == "car"
    assert "class_name" not in event.to_dict()
    assert engine.statistics()["A_TO_B"] == 1
    assert engine.statistics()["car"] == 1
