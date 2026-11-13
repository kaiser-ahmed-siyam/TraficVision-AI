"""Vehicle detection counting and virtual-line crossing state."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass

from config.vehicle_classes import SUPPORTED_VEHICLE_CLASSES

from .schemas import CrossingEvent, LineConfig, Point, Track
from .track_history import bottom_center


def signed_distance(point: Point, line: LineConfig) -> float:
    """Return the signed perpendicular distance from ``point`` to ``line``."""

    x1, y1 = line.start
    x2, y2 = line.end
    px, py = point
    denominator = math.hypot(x2 - x1, y2 - y1)
    if denominator == 0:
        return 0.0
    return ((x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)) / denominator


@dataclass
class _CrossingState:
    side: int
    line_signature: tuple
    last_event_frame: int | None = None
    counted: bool = False


class LineCrossingDetector:
    """Detect one stable crossing per track and line."""

    def __init__(self, minimum_track_age: int = 3, cooldown_frames: int = 5):
        if minimum_track_age < 0:
            raise ValueError("minimum_track_age must be non-negative")
        if cooldown_frames < 0:
            raise ValueError("cooldown_frames must be non-negative")
        self.minimum_track_age = int(minimum_track_age)
        self.cooldown_frames = int(cooldown_frames)
        self._states: dict[tuple[int, str], _CrossingState] = {}

    @staticmethod
    def _line_signature(line: LineConfig) -> tuple:
        return (
            tuple(float(value) for value in line.start),
            tuple(float(value) for value in line.end),
            float(line.hysteresis_pixels),
            line.direction.lower(),
            bool(line.enabled),
        )

    @staticmethod
    def _is_vehicle(track: Track) -> bool:
        return str(track.class_name).strip().lower() in {
            name.lower() for name in SUPPORTED_VEHICLE_CLASSES
        }

    def update(
        self,
        track: Track,
        line: LineConfig,
        frame_index: int,
        timestamp_ms: float = 0.0,
    ) -> CrossingEvent | None:
        if not line.enabled or track.age < self.minimum_track_age or not self._is_vehicle(track):
            return None

        key = (int(track.track_id), line.line_id)
        signature = self._line_signature(line)
        state = self._states.get(key)
        if state is not None and state.line_signature != signature:
            state = None
            self._states.pop(key, None)

        distance = signed_distance(bottom_center(track.bbox), line)
        if not math.isfinite(distance) or abs(distance) <= line.hysteresis_pixels:
            return None

        current_side = 1 if distance > 0 else -1
        if state is None:
            self._states[key] = _CrossingState(current_side, signature)
            return None

        previous_side = state.side
        state.side = current_side
        if previous_side == current_side or state.counted:
            return None

        direction = "A_TO_B" if previous_side < current_side else "B_TO_A"
        if line.direction.lower() not in {"both", direction.lower()}:
            return None

        if (
            state.last_event_frame is not None
            and frame_index - state.last_event_frame <= self.cooldown_frames
        ):
            return None

        state.last_event_frame = int(frame_index)
        state.counted = True
        return CrossingEvent(
            int(track.track_id),
            line.line_id,
            str(track.class_name).strip().lower(),
            direction,
            int(frame_index),
            float(timestamp_ms),
            bottom_center(track.bbox),
        )

    def forget_track(self, track_id: int) -> None:
        """Forget all line state for a track that has permanently disappeared."""

        for key in [key for key in self._states if key[0] == int(track_id)]:
            self._states.pop(key, None)

    def reset(self) -> None:
        self._states.clear()


class CountingEngine:
    """Store crossing events and prevent duplicate track/line counts."""

    def __init__(self):
        self.events: list[CrossingEvent] = []
        self._event_keys: set[tuple[int, str]] = set()

    def add_event(self, event: CrossingEvent | None) -> bool:
        if event is None:
            return False
        key = (int(event.track_id), event.line_id)
        if key in self._event_keys:
            return False
        self._event_keys.add(key)
        self.events.append(event)
        return True

    def forget_track(self, track_id: int) -> None:
        """Allow a recycled tracker ID to represent a new vehicle."""

        for key in [key for key in self._event_keys if key[0] == int(track_id)]:
            self._event_keys.discard(key)

    def reset(self) -> None:
        self.events.clear()
        self._event_keys.clear()

    @property
    def total(self) -> int:
        return len(self.events)

    def statistics(self) -> dict:
        by_class = Counter(event.class_name for event in self.events)
        by_direction = Counter(event.direction for event in self.events)
        duration_minutes = max((event.timestamp_ms for event in self.events), default=0.0) / 60000.0
        vehicles_per_minute = self.total / duration_minutes if duration_minutes else 0.0
        return {
            "total": self.total,
            "total_vehicles": self.total,
            "vehicles_per_minute": vehicles_per_minute,
            "vehicles_per_hour": vehicles_per_minute * 60.0,
            "by_class": dict(by_class),
            "by_direction": dict(by_direction),
            "car": by_class.get("car", 0),
            "motorcycle": by_class.get("motorcycle", 0),
            "bus": by_class.get("bus", 0),
            "truck": by_class.get("truck", 0),
            "A_TO_B": by_direction.get("A_TO_B", 0),
            "B_TO_A": by_direction.get("B_TO_A", 0),
        }


__all__ = ["CountingEngine", "LineCrossingDetector", "signed_distance"]
