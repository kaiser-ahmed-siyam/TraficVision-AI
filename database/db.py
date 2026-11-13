"""SQLite connection and schema initialization."""

from __future__ import annotations

import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT
);
CREATE TABLE IF NOT EXISTS crossing_events (
    event_id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES sessions(session_id),
    track_id INTEGER NOT NULL,
    line_id TEXT NOT NULL,
    class_name TEXT NOT NULL,
    direction TEXT NOT NULL,
    frame_index INTEGER NOT NULL,
    timestamp_ms REAL NOT NULL,
    position_x REAL NOT NULL,
    position_y REAL NOT NULL,
    UNIQUE(session_id, track_id, line_id)
);
CREATE TABLE IF NOT EXISTS session_statistics (
    session_id TEXT PRIMARY KEY REFERENCES sessions(session_id),
    total_vehicles INTEGER NOT NULL,
    by_class_json TEXT NOT NULL,
    by_direction_json TEXT NOT NULL
);
"""


def connect(database: str | Path) -> sqlite3.Connection:
    path = Path(database)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.executescript(SCHEMA)
    connection.commit()
    return connection
