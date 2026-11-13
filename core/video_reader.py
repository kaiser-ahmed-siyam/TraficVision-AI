"""Streaming OpenCV reader for files, webcams, and RTSP sources."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VideoMetadata:
    width: int
    height: int
    fps: float
    frame_count: int
    duration_seconds: float
    source_type: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class VideoReader:
    """Read frames incrementally from a video path, camera index, or RTSP URL."""

    def __init__(self, source: str | Path | int):
        self.source = source
        self.capture = None
        self.frame_index = 0
        self.last_error: str | None = None

    @property
    def source_type(self) -> str:
        if isinstance(self.source, int):
            return "webcam"
        source = str(self.source)
        return "rtsp" if source.lower().startswith(("rtsp://", "rtsps://")) else "file"

    def open(self) -> bool:
        import cv2

        self.release()
        self.capture = cv2.VideoCapture(self.source)
        if not self.capture.isOpened():
            self.last_error = f"Unable to open video source: {self.source}"
            self.release()
            return False
        self.frame_index = 0
        self.last_error = None
        return True

    def read(self) -> dict[str, Any]:
        if self.capture is None:
            return {"success": False, "frame": None, "frame_index": self.frame_index, "timestamp_ms": 0.0}
        success, frame = self.capture.read()
        if not success:
            return {
                "success": False,
                "frame": None,
                "frame_index": self.frame_index,
                "timestamp_ms": self._timestamp_ms(),
            }
        self.frame_index += 1
        return {
            "success": True,
            "frame": frame,
            "frame_index": self.frame_index - 1,
            "timestamp_ms": self._timestamp_ms(),
        }

    def _timestamp_ms(self) -> float:
        if self.capture is None:
            return 0.0
        try:
            return float(self.capture.get(0))
        except Exception:
            return 0.0

    def get_metadata(self) -> VideoMetadata:
        if self.capture is None:
            raise RuntimeError("Video source is not open")
        import cv2

        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        fps = float(self.capture.get(cv2.CAP_PROP_FPS) or 0.0)
        frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
        duration = frame_count / fps if fps > 0 else 0.0
        return VideoMetadata(width, height, fps, frame_count, duration, self.source_type)

    def release(self) -> None:
        if self.capture is not None:
            self.capture.release()
            self.capture = None

    def __enter__(self) -> "VideoReader":
        if not self.open():
            raise RuntimeError(self.last_error or "Unable to open video source")
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()
