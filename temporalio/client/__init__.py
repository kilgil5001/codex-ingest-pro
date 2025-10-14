"""Client stubs."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Client:
    address: str

    @classmethod
    async def connect(cls, address: str) -> "Client":
        return cls(address=address)
