"""OpenCV track annotation helpers."""


def draw_tracks(frame, tracks, color=(255, 170, 0), speed_estimates=None):
    import cv2

    output = frame.copy()
    for track in tracks:
        x1, y1, x2, y2 = (int(value) for value in track.bbox)
        cv2.rectangle(output, (x1, y1), (x2, y2), color, 3)
        estimate = speed_estimates.get(track.track_id) if speed_estimates else None
        speed = estimate.speed_kmh if estimate is not None else getattr(track, "speed_kmh", 0.0)
        cv2.putText(output, f"ID {track.track_id} {track.class_name} {speed:.1f} km/h", (x1, min(output.shape[0] - 5, y2 + 20)), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 2, cv2.LINE_AA)
    return output
