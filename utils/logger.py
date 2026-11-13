"""Small, idempotent logging setup for the application."""

from __future__ import annotations

import logging


_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
_MANAGED_ATTRIBUTE = "_trafficvision_managed"


def configure_logging(level: str = "INFO", logger_name: str = "trafficvision") -> logging.Logger:
    """Return a configured named logger without duplicating its handler."""

    normalized_level = level.upper()
    numeric_level = getattr(logging, normalized_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Unsupported logging level: {level}")

    logger = logging.getLogger(logger_name)
    logger.setLevel(numeric_level)
    logger.propagate = False

    formatter = logging.Formatter(_FORMAT)
    managed_handler = next(
        (handler for handler in logger.handlers if getattr(handler, _MANAGED_ATTRIBUTE, False)),
        None,
    )
    if managed_handler is None:
        managed_handler = logging.StreamHandler()
        setattr(managed_handler, _MANAGED_ATTRIBUTE, True)
        logger.addHandler(managed_handler)

    managed_handler.setLevel(numeric_level)
    managed_handler.setFormatter(formatter)
    return logger


__all__ = ["configure_logging"]
