"""Parameterized persistence operations for sessions and events."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from .db import connect


class TrafficRepository:
    def __init__(self, database):
        self.connection = connect(database)

    def create_session(self, source: str, session_id: str | None = None) -> str:
        identifier = session_id or str(uuid.uuid4())
        self.connection.execute("INSERT INTO sessions(session_id, source, started_at) VALUES (?, ?, ?)", (identifier, source, datetime.now(timezone.utc).isoformat()))
        self.connection.commit()
        return identifier

    def add_event(self, session_id, event) -> bool:
        event_id = event.event_id or str(uuid.uuid4())
        try:
            self.connection.execute(
            "INSERT INTO crossing_events(event_id, session_id, track_id, line_id, class_name, direction, frame_index, timestamp_ms, position_x, position_y) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (event_id, session_id, event.track_id, event.line_id, event.class_name, event.direction, event.frame_index, event.timestamp_ms, event.position[0], event.position[1]),
            )
            self.connection.commit()
            return True
        except Exception as exc:
            if "UNIQUE" in str(exc).upper():
                self.connection.rollback()
                return False
            raise

    def save_statistics(self, session_id, statistics: dict) -> None:
        self.connection.execute(
            "INSERT INTO session_statistics(session_id, total_vehicles, by_class_json, by_direction_json) VALUES (?, ?, ?, ?) ON CONFLICT(session_id) DO UPDATE SET total_vehicles=excluded.total_vehicles, by_class_json=excluded.by_class_json, by_direction_json=excluded.by_direction_json",
            (session_id, statistics.get("total_vehicles", 0), json.dumps(statistics.get("by_class", {})), json.dumps(statistics.get("by_direction", {}))),
        )
        self.connection.commit()

    def finish_session(self, session_id) -> None:
        self.connection.execute("UPDATE sessions SET ended_at = ? WHERE session_id = ?", (datetime.now(timezone.utc).isoformat(), session_id))
        self.connection.commit()

    def list_sessions(self):
        return [dict(row) for row in self.connection.execute("SELECT * FROM sessions ORDER BY started_at DESC").fetchall()]

    def get_events(self, session_id):
        return [dict(row) for row in self.connection.execute("SELECT * FROM crossing_events WHERE session_id = ? ORDER BY frame_index", (session_id,)).fetchall()]

    def close(self) -> None:
        self.connection.close()
