from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class SystemSettingOut(BaseModel):
    id: int
    key: str
    value: str
    description: str | None
    is_public: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemSettingUpdate(BaseModel):
    value: str
    description: str | None = None
    is_public: bool | None = None

