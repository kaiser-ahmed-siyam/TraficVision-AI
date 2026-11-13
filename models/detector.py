"""Robust YOLO vehicle-detector adapter with lazy model initialization."""

from __future__ import annotations

import math
from typing import Any, Iterable

from config.vehicle_classes import COCO_VEHICLE_CLASSES
from core.schemas import Detection

from .model_loader import ModelLoader


def _to_numpy(value: Any):
    """Convert a tensor or array-like value to a NumPy array."""

    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "numpy"):
        return value.numpy()
    import numpy as np

    return np.asarray(value)


def _normalise_classes(selected_classes: Iterable[str] | None) -> set[str] | None:
    if selected_classes is None:
        return None
    return {str(name).strip().lower() for name in selected_classes}


class VehicleDetector:
    """Detect only supported COCO vehicle classes in one image/frame."""

    def __init__(
        self,
        model_path: str = "yolo11n.pt",
        device: str = "auto",
        confidence: float = 0.35,
        iou: float = 0.50,
        image_size: int = 640,
        model: Any | None = None,
        selected_classes: Iterable[str] | None = None,
    ) -> None:
        if not 0.0 < confidence <= 1.0:
            raise ValueError("confidence must be greater than 0 and at most 1")
        if not 0.0 < iou <= 1.0:
            raise ValueError("iou must be greater than 0 and at most 1")
        if int(image_size) <= 0:
            raise ValueError("image_size must be a positive integer")

        self.confidence = float(confidence)
        self.iou = float(iou)
        self.image_size = int(image_size)
        self.selected_classes = _normalise_classes(selected_classes)
        supported_names = {name.lower() for name in COCO_VEHICLE_CLASSES.values()}
        if self.selected_classes is not None:
            unknown = self.selected_classes - supported_names
            if unknown:
                raise ValueError(
                    "Unsupported vehicle class name(s): " + ", ".join(sorted(unknown))
                )
        self.loader = ModelLoader(model_path=model_path, device=device)
        self.model = model

    def _get_model(self):
        if self.model is None:
            self.model = self.loader.load()
        return self.model

    def detect(self, frame) -> list[Detection]:
        if frame is None:
            raise ValueError("frame must not be None")

        model = self._get_model()
        predict_kwargs = {
            "source": frame,
            "conf": self.confidence,
            "iou": self.iou,
            "imgsz": self.image_size,
            "verbose": False,
        }
        if self.loader.resolved_device is not None:
            predict_kwargs["device"] = self.loader.resolved_device

        results = model.predict(**predict_kwargs)
        detections: list[Detection] = []
        for result in results or []:
            boxes = getattr(result, "boxes", None)
            if boxes is None:
                continue
            xyxy = getattr(boxes, "xyxy", None)
            class_ids = getattr(boxes, "cls", None)
            confidences = getattr(boxes, "conf", None)
            if xyxy is None or class_ids is None or confidences is None:
                continue

            xyxy_array = _to_numpy(xyxy)
            if getattr(xyxy_array, "ndim", 0) == 1:
                xyxy_array = xyxy_array.reshape(1, -1)
            class_array = _to_numpy(class_ids).reshape(-1)
            confidence_array = _to_numpy(confidences).reshape(-1)

            for bbox, class_id, confidence in zip(xyxy_array, class_array, confidence_array):
                try:
                    class_number = int(class_id)
                    score = float(confidence)
                    coordinates = tuple(float(value) for value in bbox[:4])
                except (TypeError, ValueError):
                    continue
                if len(coordinates) != 4 or not all(math.isfinite(value) for value in coordinates):
                    continue
                if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                    continue
                if coordinates[2] <= coordinates[0] or coordinates[3] <= coordinates[1]:
                    continue
                class_name = COCO_VEHICLE_CLASSES.get(class_number)
                if class_name is None:
                    continue
                if self.selected_classes is not None and class_name.lower() not in self.selected_classes:
                    continue
                detections.append(Detection(coordinates, class_number, class_name, score))
        return detections

    @staticmethod
    def filter_vehicles(
        detections: Iterable[Detection | dict],
        selected_classes: Iterable[str] | None = None,
    ) -> list[Detection | dict]:
        selected = _normalise_classes(selected_classes)
        filtered: list[Detection | dict] = []
        for item in detections:
            if isinstance(item, dict):
                class_id = item.get("class_id")
                class_name = item.get("class_name")
            else:
                class_id = getattr(item, "class_id", None)
                class_name = getattr(item, "class_name", None)
            try:
                class_number = int(class_id)
            except (TypeError, ValueError):
                continue
            expected_name = COCO_VEHICLE_CLASSES.get(class_number)
            if expected_name is None:
                continue
            actual_name = str(class_name).strip().lower() if class_name is not None else expected_name
            if selected is not None and actual_name not in selected:
                continue
            filtered.append(item)
        return filtered


__all__ = ["VehicleDetector"]
