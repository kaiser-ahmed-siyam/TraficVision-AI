"""SQLite-facing records."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SessionRecord:
    session_id: str
    source: str
    started_at: str
    ended_at: str | None = None


@dataclass(frozen=True)
class StatisticsRecord:
    session_id: str
    total_vehicles: int
    by_class_json: str
    by_direction_json: str
