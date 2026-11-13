"""Visualization regression tests."""

import numpy as np

from core.schemas import Detection, LineConfig, Track
from visualization.frame_renderer import FrameRenderer


def test_renderer_draws_visible_detection_and_track_boxes():
    frame = np.zeros((100, 100, 3), dtype=np.uint8)
    output = FrameRenderer().render(
        frame,
        [Detection((20, 20, 60, 60), 2, "car", 0.9)],
        [Track(1, (20, 20, 60, 60), "car")],
        [LineConfig("main_line", (0, 80), (100, 80))],
    )

    assert output.shape == frame.shape
    assert int(np.count_nonzero(output)) > 0
    assert int(output[20, 20].sum()) > 0
