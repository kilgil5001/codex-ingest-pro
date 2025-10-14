"""Lightweight pydantic stub for offline tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Type, TypeVar


class ValidationError(Exception):
    pass


T = TypeVar("T")


def Field(default: Any = None, **kwargs: Any) -> Any:
    return default


def validator(field_name: str, *, pre: bool = False) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        return func

    return decorator


class BaseModel:
    def __init__(self, **data: Any) -> None:
        for key, value in data.items():
            setattr(self, key, value)

    def dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class BaseSettings(BaseModel):
    class Config:
        env_prefix = ""
        case_sensitive = False


AnyHttpUrl = str
HttpUrl = str


def constr(**kwargs: Any) -> Type[str]:
    return str
