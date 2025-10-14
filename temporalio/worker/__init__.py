"""Worker stubs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass
class Worker:
    client: object
    task_queue: str
    workflows: Sequence[type]
    activities: Iterable[object]

    async def run(self) -> None:  # pragma: no cover - runtime stub
        raise RuntimeError("Temporal worker cannot run in stub environment")
