"""Speed-estimation and real-time annotation tests."""

from core.schemas import Track
from core.speed_tracker import SpeedTracker


def test_speed_tracker_converts_pixel_displacement_to_kmh():
    tracker = SpeedTracker(pixels_per_meter=10.0, smoothing_window=1)
    first = Track(1, (0, 0, 10, 10), "car")
    second = Track(1, (0, 10, 10, 20), "car")

    assert tracker.update([first], timestamp_ms=0, frame_index=0)[1].speed_kmh == 0.0
    estimate = tracker.update([second], timestamp_ms=1000, frame_index=1)[1]

    assert estimate.distance_pixels == 10.0
    assert estimate.speed_kmh == 3.6


def test_speed_tracker_resets_and_removes_missing_tracks():
    tracker = SpeedTracker()
    tracker.update([Track(1, (0, 0, 10, 10), "car")], timestamp_ms=100, frame_index=1)
    tracker.remove_missing(set())
    assert tracker.update([Track(1, (0, 0, 10, 10), "car")], timestamp_ms=200, frame_index=2)[1].speed_kmh == 0.0
    tracker.reset()
    assert tracker.update([Track(1, (0, 0, 10, 10), "car")], timestamp_ms=300, frame_index=3)[1].speed_kmh == 0.0
