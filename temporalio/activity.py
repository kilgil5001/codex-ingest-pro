"""Minimal Temporal activity decorator stubs for local testing."""
from __future__ import annotations

from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def defn(name: str | None = None) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        setattr(func, "_temporal_activity_name", name or func.__name__)
        return func

    return decorator
