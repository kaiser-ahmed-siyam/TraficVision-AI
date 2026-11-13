"""General small helpers shared by UI and processing code."""

from pathlib import Path


def ensure_directory(path: str | Path) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(maximum, value))
