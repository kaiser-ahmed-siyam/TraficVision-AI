"""Validation and management of one or more virtual counting lines."""

from __future__ import annotations

from .schemas import LineConfig, Point


class LineManager:
    def __init__(self, lines: list[LineConfig] | None = None):
        self.lines: dict[str, LineConfig] = {}
        for line in lines or []:
            self.add(line)

    def add(self, line: LineConfig) -> LineConfig:
        self._validate(line)
        self.lines[line.line_id] = line
        return line

    def update(self, line_id: str, **changes) -> LineConfig:
        current = self.get(line_id)
        updated = LineConfig(
            line_id=current.line_id,
            start=changes.get("start", current.start),
            end=changes.get("end", current.end),
            enabled=changes.get("enabled", current.enabled),
            direction=changes.get("direction", current.direction),
            hysteresis_pixels=changes.get("hysteresis_pixels", current.hysteresis_pixels),
        )
        return self.add(updated)

    def get(self, line_id: str = "main_line") -> LineConfig:
        if line_id not in self.lines:
            raise KeyError(f"Unknown counting line: {line_id}")
        return self.lines[line_id]

    def enabled(self) -> list[LineConfig]:
        return [line for line in self.lines.values() if line.enabled]

    @staticmethod
    def _validate(line: LineConfig) -> None:
        if not line.line_id.strip():
            raise ValueError("line_id must not be empty")
        if line.start == line.end:
            raise ValueError("counting line endpoints must be different")
        if line.direction.lower() not in {"both", "a_to_b", "b_to_a"}:
            raise ValueError("direction must be both, a_to_b, or b_to_a")
        if line.hysteresis_pixels < 0:
            raise ValueError("hysteresis_pixels must be non-negative")
