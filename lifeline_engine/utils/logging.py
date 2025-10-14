"""Logging utilities with consistent formatting for activities."""
from __future__ import annotations

import logging
from contextlib import contextmanager
from time import monotonic
from typing import Dict, Iterator, Optional


LOGGER_NAME = "lifeline_engine"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide logging once."""

    if logging.getLogger(LOGGER_NAME).handlers:
        return
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    root_logger = logging.getLogger(LOGGER_NAME)
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a module-level logger."""

    configure_logging()
    return logging.getLogger(f"{LOGGER_NAME}.{name}" if name else LOGGER_NAME)


@contextmanager
def activity_context(activity_name: str, extra: Optional[Dict[str, str]] = None) -> Iterator[None]:
    """Context manager that logs activity execution time for observability."""

    logger = get_logger("activity")
    payload = {"activity": activity_name, **(extra or {})}
    start = monotonic()
    logger.info("start", extra=payload)
    try:
        yield
    finally:
        duration = monotonic() - start
        payload["duration_seconds"] = f"{duration:.3f}"
        logger.info("end", extra=payload)
