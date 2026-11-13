"""Pipeline-facing ByteTrack wrapper with injectable implementations."""

from __future__ import annotations

from models.tracker import ByteTrackTracker


class VehicleTracker:
    def __init__(self, tracker=None, track_buffer: int = 30, confidence: float = 0.35):
        self.tracker = tracker or ByteTrackTracker(track_buffer, confidence)

    def update(self, detections, frame=None):
        return self.tracker.update(detections, frame)

    def get_active_tracks(self):
        return getattr(self.tracker, "active_tracks", [])

    def reset(self):
        if hasattr(self.tracker, "reset"):
            self.tracker.reset()
