"""Pure traffic-statistics calculations."""

from __future__ import annotations

from collections import Counter


def calculate_statistics(events, duration_seconds: float = 0.0) -> dict:
    by_class = Counter(event.class_name for event in events)
    by_direction = Counter(event.direction for event in events)
    total = len(events)
    minutes = duration_seconds / 60.0 if duration_seconds > 0 else 0.0
    vehicles_per_minute = total / minutes if minutes else 0.0
    return {
        "total": total,
        "total_vehicles": total,
        "vehicles_per_minute": vehicles_per_minute,
        "vehicles_per_hour": vehicles_per_minute * 60.0,
        "by_class": dict(by_class),
        "by_direction": dict(by_direction),
        "A_TO_B": by_direction.get("A_TO_B", 0),
        "B_TO_A": by_direction.get("B_TO_A", 0),
    }
