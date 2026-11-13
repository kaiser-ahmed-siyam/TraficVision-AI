"""Lazy YOLO model loading and device selection."""

from __future__ import annotations


def resolve_device(device: str = "auto") -> str:
    if device != "auto":
        return device
    try:
        import torch

        return "cuda" if torch.cuda.is_available() else "cpu"
    except ImportError:
        return "cpu"


def load_model(model_path: str, device: str = "auto"):
    try:
        from ultralytics import YOLO
    except ImportError as exc:
        raise RuntimeError("Ultralytics is required for YOLO inference") from exc
    resolved_device = resolve_device(device)
    model = YOLO(model_path)
    if hasattr(model, "to"):
        model.to(resolved_device)
    return model, resolved_device


class ModelLoader:
    def __init__(self, model_path: str = "yolo11n.pt", device: str = "auto"):
        self.model_path = model_path
        self.device = device
        self.model = None
        self.resolved_device: str | None = None

    def load(self):
        if self.model is None:
            self.model, self.resolved_device = load_model(self.model_path, self.device)
        return self.model
