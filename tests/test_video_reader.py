"""Synthetic OpenCV video-reader tests."""

from scripts.generate_test_video import generate
from core.pipeline import TrafficPipeline
from core.preprocessor import FramePreprocessor
from core.schemas import LineConfig
from core.line_manager import LineManager
from core.video_reader import VideoReader


def test_video_reader_opens_and_reads_incrementally(tmp_path):
    path = generate(tmp_path / "sample.mp4", frames=4, width=64, height=48)
    reader = VideoReader(path)

    assert reader.open() is True
    metadata = reader.get_metadata()
    first = reader.read()
    reader.release()

    assert metadata.width == 64
    assert metadata.height == 48
    assert first["success"] is True
    assert first["frame_index"] == 0


def test_video_reader_handles_invalid_source(tmp_path):
    reader = VideoReader(tmp_path / "missing.mp4")

    assert reader.open() is False
    assert reader.last_error


def test_pipeline_writes_readable_processed_video(tmp_path):
    import cv2

    source = generate(tmp_path / "source.mp4", frames=3, width=64, height=48)

    class EmptyDetector:
        def detect(self, frame):
            return []

    class EmptyTracker:
        def update(self, detections, frame):
            return []

    reader = VideoReader(source)
    assert reader.open()
    pipeline = TrafficPipeline(
        reader=reader,
        detector=EmptyDetector(),
        tracker=EmptyTracker(),
        preprocessor=FramePreprocessor(0),
        line_manager=LineManager([LineConfig("main_line", (0, 24), (64, 24))]),
    )
    output = tmp_path / "processed.mp4"
    results = pipeline.run(output_path=output)
    capture = cv2.VideoCapture(str(output))
    opened, frame = capture.read()
    capture.release()

    assert len(results) == 3
    assert output.stat().st_size > 0
    assert opened is True
    assert frame.shape[:2] == (48, 64)
