"""Minimal Temporal workflow stubs for structural validation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta as _timedelta
from typing import Any, Awaitable, Callable, Dict, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class _WorkflowInfo:
    workflow_id: str = "demo-workflow"


def info() -> _WorkflowInfo:
    return _WorkflowInfo()


def timedelta(*, minutes: int = 0, seconds: int = 0) -> _timedelta:
    return _timedelta(minutes=minutes, seconds=seconds)


def defn(name: str | None = None) -> Callable[[type], type]:
    def decorator(cls: type) -> type:
        setattr(cls, "_temporal_workflow_name", name or cls.__name__)
        return cls

    return decorator


def signal(func: F) -> F:
    return func


def query(func: F) -> F:
    return func


def run(func: F) -> F:
    return func


async def execute_activity(*args: Any, **kwargs: Any) -> Any:  # pragma: no cover - runtime stub
    raise NotImplementedError("Activity execution is not available in the stub environment")
