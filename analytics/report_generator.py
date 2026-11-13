"""CSV report generation for crossing events."""

from __future__ import annotations

import csv
import io


def events_to_csv(events) -> str:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["event_id", "track_id", "line_id", "vehicle_class", "direction", "frame_index", "timestamp_ms", "x", "y"])
    writer.writeheader()
    for event in events:
        writer.writerow({
            "event_id": event.event_id or f"{event.track_id}_{event.line_id}_{event.frame_index}",
            "track_id": event.track_id,
            "line_id": event.line_id,
            "vehicle_class": event.class_name,
            "direction": event.direction,
            "frame_index": event.frame_index,
            "timestamp_ms": event.timestamp_ms,
            "x": event.position[0],
            "y": event.position[1],
        })
    return output.getvalue()
