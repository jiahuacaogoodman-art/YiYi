from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SubjectBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    icon: str | None = Field(default=None, max_length=100)
    sort_order: int = 0
    is_enabled: bool = True
    description: str | None = None


class SubjectCreate(SubjectBase):
    pass


class SubjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    icon: str | None = Field(default=None, max_length=100)
    sort_order: int | None = None
    is_enabled: bool | None = None
    description: str | None = None


class SubjectOut(SubjectBase):
    id: int
    question_count: int = 0
    practiced_count: int = 0
    correct_rate: float = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ReorderItem(BaseModel):
    id: int
    sort_order: int


class ChapterBase(BaseModel):
    subject_id: int
    name: str = Field(min_length=1, max_length=120)
    code: str = Field(min_length=1, max_length=80)
    sort_order: int = 0
    is_enabled: bool = True
    description: str | None = None


class ChapterCreate(ChapterBase):
    pass


class ChapterUpdate(BaseModel):
    subject_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=120)
    code: str | None = Field(default=None, min_length=1, max_length=80)
    sort_order: int | None = None
    is_enabled: bool | None = None
    description: str | None = None


class ChapterOut(ChapterBase):
    id: int
    subject_name: str | None = None
    question_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ChapterBatchStatusIn(BaseModel):
    ids: list[int]
    is_enabled: bool


class KnowledgePointBase(BaseModel):
    subject_id: int
    chapter_id: int
    name: str = Field(min_length=1, max_length=160)
    label: str | None = Field(default=None, max_length=160)
    importance_level: str = "medium"
    description: str | None = None
    sort_order: int = 0
    is_enabled: bool = True


class KnowledgePointCreate(KnowledgePointBase):
    pass


class KnowledgePointUpdate(BaseModel):
    subject_id: int | None = None
    chapter_id: int | None = None
    name: str | None = Field(default=None, min_length=1, max_length=160)
    label: str | None = Field(default=None, max_length=160)
    importance_level: str | None = None
    description: str | None = None
    sort_order: int | None = None
    is_enabled: bool | None = None


class KnowledgePointOut(KnowledgePointBase):
    id: int
    subject_name: str | None = None
    chapter_name: str | None = None
    question_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class KnowledgePointImportItem(BaseModel):
    subject_name: str
    chapter_name: str
    name: str
    label: str | None = None
    importance_level: str = "medium"
    description: str | None = None

