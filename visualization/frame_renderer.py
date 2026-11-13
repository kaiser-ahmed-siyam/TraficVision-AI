"""Compose detections, tracks, lines, and crossing labels into frames."""

from .bounding_boxes import draw_bounding_boxes
from .line_visualizer import draw_lines
from .tracking_visualizer import draw_tracks


class FrameRenderer:
    def render(self, frame, detections, tracks, lines, events=None, speed_estimates=None):
        import cv2

        output = draw_lines(frame, lines)
        output = draw_bounding_boxes(output, detections)
        output = draw_tracks(output, tracks, speed_estimates=speed_estimates)
        cv2.putText(output, f"Detections: {len(detections)}  Tracks: {len(tracks)}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
        if events:
            import cv2

            for index, event in enumerate(events):
                cv2.putText(output, f"{event.class_name} {event.direction}", (10, 25 + index * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
        return output
