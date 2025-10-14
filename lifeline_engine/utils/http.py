"""HTTP utilities with resiliency defaults."""
from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

import httpx


class HttpClient:
    """Wrapper around httpx with sensible defaults and retry support."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor

    async def get(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._retry("get", url, **kwargs)

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        return await self._retry("post", url, **kwargs)

    async def _retry(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        attempt = 0
        while True:
            try:
                response = await self._client.request(method, url, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPError as exc:  # pragma: no cover - network failure path
                attempt += 1
                if attempt > self._max_retries:
                    raise
                await asyncio.sleep(self._backoff_factor * attempt)

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "HttpClient":
        return self

    async def __aexit__(self, *exc_info: Any) -> None:
        await self.close()
