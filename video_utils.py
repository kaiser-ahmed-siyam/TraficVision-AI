"""Video helpers."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

_OPENCV_SAFE_CODECS = {"h264", "mpeg4", "mjpeg"}


def ensure_h264(path: Path) -> Path:
    """Return a path OpenCV can decode, transcoding to H.264 when needed.

    Returns the original path if the codec is already supported, or if
    ffmpeg/ffprobe are not installed (e.g. a local machine without ffmpeg).
    """
    path = Path(path)
    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        return path

    probe = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=codec_name", "-of", "json", str(path),
        ],
        capture_output=True,
        text=True,
    )
    codec = ""
    try:
        codec = json.loads(probe.stdout)["streams"][0]["codec_name"]
    except (KeyError, IndexError, ValueError):
        pass

    if codec in _OPENCV_SAFE_CODECS:
        return path

    out = Path(tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name)
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(path),
            "-vf", "scale='min(1280,iw)':-2",  # cap width to save CPU/RAM
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "28",
            "-an", str(out),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        out.unlink(missing_ok=True)
        raise RuntimeError(f"Could not convert video (codec: {codec or 'unknown'}): {result.stderr[-300:]}")
    return out
