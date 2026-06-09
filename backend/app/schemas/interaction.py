from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.question import QuestionOut


class NoteIn(BaseModel):
    content: str = Field(min_length=1, max_length=4000)


class NoteOut(BaseModel):
    id: int
    question_id: int
    content: str
    created_at: datetime
    updated_at: datetime
    question: QuestionOut | None = None


class CommentIn(BaseModel):
    content: str = Field(min_length=1, max_length=1000)


class CommentOut(BaseModel):
    id: int
    question_id: int
    content: str
    is_pinned: bool
    user_id: int
    username: str
    nickname: str
    created_at: datetime
    updated_at: datetime
    is_mine: bool = False
    question: QuestionOut | None = None


class LikeStatusOut(BaseModel):
    question_id: int
    is_liked: bool
    like_count: int