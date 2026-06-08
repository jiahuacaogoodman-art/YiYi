from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    feedback_type: str
    content: str = Field(min_length=1)


class FeedbackUpdate(BaseModel):
    status: str
    handler_note: str | None = None


class FeedbackOut(BaseModel):
    id: int
    question_id: int
    user_id: int
    feedback_type: str
    content: str
    status: str
    handler_id: int | None
    handled_at: datetime | None
    handler_note: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

