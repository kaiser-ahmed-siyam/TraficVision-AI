"""OpenCV bounding-box drawing helpers."""


CLASS_COLORS = {
    "car": (0, 255, 0),
    "motorcycle": (0, 255, 255),
    "bus": (255, 140, 0),
    "truck": (255, 0, 255),
}


def draw_bounding_boxes(frame, detections, color=None):
    import cv2

    output = frame.copy()
    for detection in detections:
        x1, y1, x2, y2 = (int(value) for value in detection.bbox)
        box_color = color or CLASS_COLORS.get(detection.class_name, (0, 255, 0))
        label = f"{detection.class_name} {detection.confidence:.2f}"
        cv2.rectangle(output, (x1, y1), (x2, y2), box_color, 3)
        (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2)
        label_y = max(label_height + baseline, y1)
        cv2.rectangle(output, (x1, label_y - label_height - baseline), (x1 + label_width + 6, label_y + 2), box_color, -1)
        cv2.putText(output, label, (x1 + 3, label_y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2, cv2.LINE_AA)
    return output
