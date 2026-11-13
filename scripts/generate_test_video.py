"""Generate a small synthetic video containing a moving vehicle rectangle."""

from pathlib import Path


def generate(path: str | Path, frames: int = 40, width: int = 320, height: int = 240) -> Path:
    import cv2
    import numpy as np

    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(output), cv2.VideoWriter_fourcc(*"mp4v"), 20.0, (width, height))
    try:
        for index in range(frames):
            frame = np.zeros((height, width, 3), dtype=np.uint8)
            y = 20 + index * 5
            cv2.rectangle(frame, (120, y), (180, y + 40), (255, 255, 255), -1)
            writer.write(frame)
    finally:
        writer.release()
    return output


if __name__ == "__main__":
    generate("data/samples/synthetic_crossing.mp4")
