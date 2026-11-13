"""Virtual counting-line drawing helpers."""


def draw_lines(frame, lines, color=(0, 0, 255)):
    import cv2

    output = frame.copy()
    for line in lines:
        start = tuple(int(value) for value in line.start)
        end = tuple(int(value) for value in line.end)
        cv2.line(output, start, end, color, 2)
        cv2.putText(output, line.line_id, start, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2, cv2.LINE_AA)
    return output
