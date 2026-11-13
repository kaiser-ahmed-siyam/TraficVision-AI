"""Typed contracts shared by the processing pipeline."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


Point = tuple[float, float]
BBox = tuple[float, float, float, float]


@dataclass(frozen=True)
class Detection:
    bbox: BBox
    class_id: int
    class_name: str
    confidence: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Track:
    track_id: int
    bbox: BBox
    class_name: str
    confidence: float = 0.0
    class_id: int | None = None
    age: int = 1
    speed_kmh: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineConfig:
    line_id: str
    start: Point
    end: Point
    enabled: bool = True
    direction: str = "both"
    hysteresis_pixels: float = 8.0


@dataclass(frozen=True)
class CrossingEvent:
    track_id: int
    line_id: str
    class_name: str
    direction: str
    frame_index: int
    timestamp_ms: float
    position: Point
    event_id: str | None = None

    @property
    def vehicle_class(self) -> str:
        """Compatibility name used by the event storage specification."""

        return self.class_name

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["vehicle_class"] = self.class_name
        result.pop("class_name", None)
        return result


@dataclass(frozen=True)
class FramePerformance:
    inference_ms: float = 0.0
    processing_ms: float = 0.0
    processing_fps: float = 0.0


@dataclass
class PipelineResult:
    frame: Any
    detections: list[Detection] = field(default_factory=list)
    tracks: list[Track] = field(default_factory=list)
    crossing_events: list[CrossingEvent] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)
    performance: FramePerformance = field(default_factory=FramePerformance)
    speed_estimates: dict[int, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame": self.frame,
            "detections": [item.to_dict() for item in self.detections],
            "tracks": [item.to_dict() for item in self.tracks],
            "crossing_events": [item.to_dict() for item in self.crossing_events],
            "statistics": self.statistics,
            "performance": asdict(self.performance),
            "speed_estimates": {
                track_id: asdict(value) if hasattr(value, "__dataclass_fields__") else value
                for track_id, value in self.speed_estimates.items()
            },
        }
