"""Estimate per-track speed from bottom-center displacement."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from math import hypot

from .track_history import bottom_center


@dataclass(frozen=True)
class SpeedEstimate:
    track_id: int
    speed_kmh: float
    distance_pixels: float
    elapsed_seconds: float


class SpeedTracker:
    """Convert track displacement to smoothed km/h estimates.

    ``pixels_per_meter`` must be calibrated for the camera view. The tracker
    intentionally returns zero for a track's first observation and for invalid
    or non-forward timestamps.
    """

    def __init__(self, pixels_per_meter: float = 10.0, smoothing_window: int = 5, fps: float = 30.0):
        if pixels_per_meter <= 0:
            raise ValueError("pixels_per_meter must be greater than zero")
        if smoothing_window < 1:
            raise ValueError("smoothing_window must be positive")
        self.pixels_per_meter = float(pixels_per_meter)
        self.smoothing_window = int(smoothing_window)
        self.fps = float(fps) if fps > 0 else 30.0
        self._previous: dict[int, tuple[tuple[float, float], float | None, int]] = {}
        self._samples: defaultdict[int, deque[float]] = defaultdict(lambda: deque(maxlen=self.smoothing_window))

    def update(self, tracks, timestamp_ms: float | None = None, frame_index: int | None = None) -> dict[int, SpeedEstimate]:
        estimates: dict[int, SpeedEstimate] = {}
        current_time = timestamp_ms / 1000.0 if timestamp_ms is not None else None
        current_frame = frame_index if frame_index is not None else 0
        for track in tracks:
            point = bottom_center(track.bbox)
            previous = self._previous.get(track.track_id)
            if previous is None:
                speed = 0.0
                distance = 0.0
                elapsed = 0.0
            else:
                previous_point, previous_time, previous_frame = previous
                elapsed = (current_time - previous_time) if current_time is not None and previous_time is not None and current_time > previous_time else (current_frame - previous_frame) / self.fps
                distance = hypot(point[0] - previous_point[0], point[1] - previous_point[1])
                instantaneous = distance / self.pixels_per_meter / elapsed * 3.6 if elapsed > 0 else 0.0
                self._samples[track.track_id].append(max(0.0, instantaneous))
                speed = sum(self._samples[track.track_id]) / len(self._samples[track.track_id])
            self._previous[track.track_id] = (point, current_time, current_frame)
            estimates[track.track_id] = SpeedEstimate(track.track_id, speed, distance, elapsed)
        return estimates

    def reset(self) -> None:
        self._previous.clear()
        self._samples.clear()

    def remove_missing(self, active_ids: set[int]) -> None:
        for track_id in set(self._previous) - active_ids:
            self._previous.pop(track_id, None)
            self._samples.pop(track_id, None)
