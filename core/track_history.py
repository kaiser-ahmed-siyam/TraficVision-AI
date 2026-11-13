"""Short-lived bottom-center histories for active tracks."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field

from .schemas import Point, Track


def bottom_center(bbox) -> Point:
    x1, y1, x2, y2 = bbox
    return ((float(x1) + float(x2)) / 2.0, float(y2))


@dataclass
class TrackRecord:
    class_name: str
    positions: deque[Point] = field(default_factory=deque)
    first_seen: int = 0
    last_seen: int = 0
    counted_lines: set[str] = field(default_factory=set)
    line_sides: dict[str, int] = field(default_factory=dict)


class TrackHistory:
    def __init__(self, max_length: int = 30):
        self.max_length = max_length
        self.records: dict[int, TrackRecord] = {}

    def update(self, track: Track, frame_index: int) -> TrackRecord:
        record = self.records.get(track.track_id)
        if record is None:
            record = TrackRecord(track.class_name, deque(maxlen=self.max_length), first_seen=frame_index)
            self.records[track.track_id] = record
        record.class_name = track.class_name
        record.positions.append(bottom_center(track.bbox))
        record.last_seen = frame_index
        return record

    def get(self, track_id: int) -> TrackRecord | None:
        return self.records.get(track_id)

    def age(self, track_id: int) -> int:
        record = self.records.get(track_id)
        return 0 if record is None else record.last_seen - record.first_seen + 1

    def clear(self) -> None:
        self.records.clear()

    def remove_missing(self, active_ids: set[int], current_frame: int | None = None, max_missing: int | None = None) -> set[int]:
        removed: set[int] = set()
        if current_frame is None or max_missing is None:
            return removed
        for track_id, record in list(self.records.items()):
            if track_id not in active_ids and current_frame - record.last_seen > max_missing:
                self.records.pop(track_id, None)
                removed.add(track_id)
        return removed
