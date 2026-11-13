"""Compatibility alias for the independent traffic pipeline."""

from .pipeline import TrafficPipeline

FrameProcessor = TrafficPipeline

__all__ = ["FrameProcessor", "TrafficPipeline"]
