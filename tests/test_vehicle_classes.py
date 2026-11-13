"""Tests for the supported COCO vehicle classes."""

from config.vehicle_classes import COCO_VEHICLE_CLASSES, SUPPORTED_VEHICLE_CLASSES


def test_vehicle_class_mapping_matches_coco_vehicle_classes():
    assert COCO_VEHICLE_CLASSES == {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }
    assert SUPPORTED_VEHICLE_CLASSES == ("car", "motorcycle", "bus", "truck")
