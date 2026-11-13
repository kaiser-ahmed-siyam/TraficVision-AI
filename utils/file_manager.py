"""Temporary video-file helpers."""

from pathlib import Path
import tempfile


def save_uploaded_file(uploaded_file, suffix: str | None = None) -> Path:
    extension = suffix or Path(getattr(uploaded_file, "name", "upload.mp4")).suffix
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=extension)
    try:
        handle.write(uploaded_file.getbuffer())
    finally:
        handle.close()
    return Path(handle.name)
