"""Tests for idempotent application logging."""

import logging

from utils.logger import configure_logging


def test_configure_logging_returns_named_logger():
    logger = configure_logging(level="DEBUG", logger_name="trafficvision-test")

    assert logger.name == "trafficvision-test"
    assert logger.level == logging.DEBUG


def test_configure_logging_is_idempotent():
    first = configure_logging(logger_name="trafficvision-idempotent")
    second = configure_logging(logger_name="trafficvision-idempotent")

    managed_handlers = [
        handler for handler in second.handlers if getattr(handler, "_trafficvision_managed", False)
    ]
    assert first is second
    assert len(managed_handlers) == 1
