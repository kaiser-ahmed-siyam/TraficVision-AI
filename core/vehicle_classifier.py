"""Small helpers for keeping track classes consistent with detections."""

from config.vehicle_classes import COCO_VEHICLE_CLASSES


def normalize_class_name(class_id: int | None, fallback: str = "unknown") -> str:
    return COCO_VEHICLE_CLASSES.get(class_id, fallback)


def filter_vehicle_classes(detections, selected_classes=None):
    selected = set(selected_classes or COCO_VEHICLE_CLASSES.values())
    return [item for item in detections if getattr(item, "class_name", item.get("class_name") if isinstance(item, dict) else None) in selected]
