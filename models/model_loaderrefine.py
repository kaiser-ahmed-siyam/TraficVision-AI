# """Lazy and validated loading of Ultralytics YOLO models."""

# from __future__ import annotations


# def resolve_device(device: str = "auto") -> str:
#     """Resolve ``auto`` to CUDA when available, otherwise CPU."""
#     requested = str(device).strip().lower()
#     if not requested:
#         raise ValueError("device must not be empty")

#     if requested == "auto":
#         try:
#             import torch
#         except ImportError:
#             return "cpu"
#         return "cuda:0" if torch.cuda.is_available() else "cpu"

#     if requested in {"cpu", "mps"}:
#         return requested

#     if requested == "cuda" or requested.startswith("cuda:") or requested.isdigit():
#         try:
#             import torch
#         except ImportError as exc:
#             raise RuntimeError(
#                 "PyTorch is required when an explicit CUDA device is selected"
#             ) from exc
#         if not torch.cuda.is_available():
#             raise RuntimeError(
#                 f"CUDA device '{requested}' was requested, but CUDA is not available"
#             )
#         return requested

#     raise ValueError(
#         "Unsupported device. Use 'auto', 'cpu', 'cuda', 'cuda:0', 'mps', or a GPU index."
#     )


# def load_model(model_path: str = "yolo11n.pt", device: str = "auto"):
#     """Load a YOLO model and return ``(model, resolved_device)``."""
#     if not str(model_path).strip():
#         raise ValueError("model_path must not be empty")

#     try:
#         from ultralytics import YOLO
#     except ImportError as exc:
#         raise RuntimeError(
#             "Ultralytics is required for YOLO inference. Install it with: pip install ultralytics"
#         ) from exc

#     resolved_device = resolve_device(device)
#     try:
#         model = YOLO(str(model_path))
#         if hasattr(model, "to"):
#             model.to(resolved_device)
#     except Exception as exc:
#         raise RuntimeError(
#             f"Could not load YOLO model '{model_path}' on device '{resolved_device}': {exc}"
#         ) from exc

#     return model, resolved_device


# class ModelLoader:
#     """Cache a loaded YOLO model so it is initialized only once."""

#     def __init__(self, model_path: str = "yolo11n.pt", device: str = "auto"):
#         self.model_path = str(model_path)
#         self.device = str(device)
#         self.model = None
#         self.resolved_device: str | None = None

#     def load(self):
#         """Return the cached model, loading it on the first call."""
#         if self.model is None:
#             self.model, self.resolved_device = load_model(self.model_path, self.device)
#         return self.model

#     def reset(self) -> None:
#         """Clear the cached model (useful when changing models/devices)."""
#         self.model = None
#         self.resolved_device = None
