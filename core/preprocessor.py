"""Aspect-preserving frame preprocessing with coordinate restoration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Transform:
    original_width: int
    original_height: int
    scale: float
    offset_x: float = 0.0
    offset_y: float = 0.0


class FramePreprocessor:
    def __init__(self, target_size: int = 640, roi: tuple[int, int, int, int] | None = None):
        self.target_size = target_size
        self.roi = roi
        self.last_transform: Transform | None = None

    def process(self, frame):
        image = self.apply_roi(frame, self.roi) if self.roi else frame
        return self.resize(image, self.target_size)

    def resize(self, frame, target_size: int):
        import cv2

        height, width = frame.shape[:2]
        scale = min(1.0, target_size / max(width, height)) if target_size else 1.0
        new_width = max(1, int(round(width * scale)))
        new_height = max(1, int(round(height * scale)))
        if (new_width, new_height) == (width, height):
            result = frame
        else:
            result = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)
        offset_x = self.roi[0] if self.roi else 0.0
        offset_y = self.roi[1] if self.roi else 0.0
        self.last_transform = Transform(frame.shape[1], frame.shape[0], scale, offset_x, offset_y)
        return result

    def apply_roi(self, frame, roi):
        if roi is None:
            return frame
        x1, y1, x2, y2 = (int(value) for value in roi)
        height, width = frame.shape[:2]
        x1, x2 = max(0, min(x1, width)), max(0, min(x2, width))
        y1, y2 = max(0, min(y1, height)), max(0, min(y2, height))
        if x2 <= x1 or y2 <= y1:
            raise ValueError("ROI must have positive width and height")
        return frame[y1:y2, x1:x2]

    def restore_bbox(self, bbox: tuple[float, float, float, float]) -> tuple[float, float, float, float]:
        if self.last_transform is None or self.last_transform.scale == 0:
            return bbox
        scale = self.last_transform.scale
        x1, y1, x2, y2 = bbox
        return (
            x1 / scale + self.last_transform.offset_x,
            y1 / scale + self.last_transform.offset_y,
            x2 / scale + self.last_transform.offset_x,
            y2 / scale + self.last_transform.offset_y,
        )
