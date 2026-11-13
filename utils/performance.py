"""Timing helpers used by the pipeline and benchmark script."""

import time
from contextlib import contextmanager


@contextmanager
def timed():
    started = time.perf_counter()
    result = {"elapsed_ms": 0.0}
    try:
        yield result
    finally:
        result["elapsed_ms"] = (time.perf_counter() - started) * 1000.0
