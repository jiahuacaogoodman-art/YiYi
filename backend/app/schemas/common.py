from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=200)


class PageOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[Any]


class MessageOut(BaseModel):
    message: str


class BatchIdsIn(BaseModel):
    ids: list[int] = Field(default_factory=list)

