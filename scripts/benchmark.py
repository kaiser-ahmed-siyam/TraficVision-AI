"""Basic pipeline benchmark entry point."""

import argparse
import time

from core.video_reader import VideoReader


def benchmark(source: str, max_frames: int = 100) -> dict:
    reader = VideoReader(source)
    if not reader.open():
        raise RuntimeError(reader.last_error or "Unable to open source")
    started = time.perf_counter()
    frames = 0
    try:
        while frames < max_frames:
            result = reader.read()
            if not result["success"]:
                break
            frames += 1
    finally:
        reader.release()
    elapsed = time.perf_counter() - started
    return {"frames": frames, "seconds": elapsed, "fps": frames / elapsed if elapsed else 0.0}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--max-frames", type=int, default=100)
    args = parser.parse_args()
    print(benchmark(args.source, args.max_frames))


if __name__ == "__main__":
    main()
