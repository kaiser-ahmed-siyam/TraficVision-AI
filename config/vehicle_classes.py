"""Supported vehicle classes from the pretrained COCO model."""

COCO_VEHICLE_CLASSES: dict[int, str] = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}

SUPPORTED_VEHICLE_CLASSES: tuple[str, ...] = tuple(COCO_VEHICLE_CLASSES.values())

__all__ = ["COCO_VEHICLE_CLASSES", "SUPPORTED_VEHICLE_CLASSES"]
