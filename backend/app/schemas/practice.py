from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.question import QuestionOut


class PracticeStartIn(BaseModel):
    mode: str = "sequential"
    subject_id: int | None = None
    chapter_id: int | None = None
    knowledge_point_id: int | None = None
    question_count: int = Field(default=20, ge=1, le=200)


class PracticeStartOut(BaseModel):
    mode: str
    total: int
    questions: list[QuestionOut]


class PracticeAnswerIn(BaseModel):
    question_id: int
    answer: str
    mode: str = "practice"
    time_spent_seconds: int | None = Field(default=None, ge=0)


class PracticeAnswerOut(BaseModel):
    question_id: int
    is_correct: bool
    correct_answer: str
    analysis: str
    added_to_wrong_book: bool
    wrong_count: int
    question_stat: dict


class WrongQuestionOut(BaseModel):
    id: int
    question: QuestionOut
    wrong_count: int
    last_wrong_at: datetime | None
    last_answer_correct: bool

    model_config = {"from_attributes": True}

