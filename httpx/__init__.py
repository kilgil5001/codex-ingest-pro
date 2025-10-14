"""Minimal httpx stub for tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


class HTTPError(Exception):
    pass


@dataclass
class Response:
    _json: Dict[str, Any]

    def json(self) -> Dict[str, Any]:
        return self._json

    def raise_for_status(self) -> None:
        return None


class AsyncClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None) -> None:
        self.base_url = base_url
        self.timeout = timeout

    async def request(self, method: str, url: str, **kwargs: Any) -> Response:
        return Response(_json={})

    async def aclose(self) -> None:
        return None
