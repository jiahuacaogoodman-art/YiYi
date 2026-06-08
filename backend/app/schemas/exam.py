from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.question import QuestionOut


class ExamQuestionIn(BaseModel):
    question_id: int
    score: float = Field(default=5, gt=0)
    sort_order: int = 0


class ExamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=160)
    exam_type: str = "mock"
    subject_id: int | None = None
    total_score: float = 100
    pass_score: float = 60
    duration_minutes: int = Field(default=60, ge=1)
    is_public: bool = False
    status: str = "draft"
    description: str | None = None
    questions: list[ExamQuestionIn] = Field(default_factory=list)


class ExamUpdate(BaseModel):
    name: str | None = None
    exam_type: str | None = None
    subject_id: int | None = None
    total_score: float | None = None
    pass_score: float | None = None
    duration_minutes: int | None = Field(default=None, ge=1)
    is_public: bool | None = None
    status: str | None = None
    description: str | None = None
    questions: list[ExamQuestionIn] | None = None


class ExamOut(BaseModel):
    id: int
    name: str
    exam_type: str
    subject_id: int | None
    subject_name: str | None = None
    total_score: float
    pass_score: float
    duration_minutes: int
    is_public: bool
    status: str
    description: str | None
    question_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ExamDetailOut(ExamOut):
    questions: list[QuestionOut] = Field(default_factory=list)


class AutoGenerateExamIn(BaseModel):
    name: str
    subject_id: int
    chapter_ids: list[int] = Field(default_factory=list)
    question_count: int = Field(default=20, ge=1, le=200)
    easy_ratio: float = Field(default=0.4, ge=0, le=1)
    medium_ratio: float = Field(default=0.4, ge=0, le=1)
    hard_ratio: float = Field(default=0.2, ge=0, le=1)
    duration_minutes: int = Field(default=60, ge=1)
    is_public: bool = False


class ExamStartOut(BaseModel):
    record_id: int
    exam: ExamDetailOut
    started_at: datetime
    deadline_at: datetime


class ExamSubmitAnswerIn(BaseModel):
    question_id: int
    answer: str


class ExamSubmitIn(BaseModel):
    record_id: int
    answers: list[ExamSubmitAnswerIn]


class ExamRecordOut(BaseModel):
    id: int
    exam_id: int
    exam_name: str | None = None
    user_id: int
    started_at: datetime
    submitted_at: datetime | None
    score: float | None
    correct_count: int
    wrong_count: int
    status: str
    answers: list[dict] = Field(default_factory=list)

    model_config = {"from_attributes": True}

