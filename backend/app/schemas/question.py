from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator


class QuestionOptionIn(BaseModel):
    option_key: str = Field(min_length=1, max_length=5)
    content: str = Field(min_length=1)
    image_url: str | None = None
    sort_order: int = 0


class QuestionOptionOut(QuestionOptionIn):
    id: int

    model_config = {"from_attributes": True}


class QuestionBase(BaseModel):
    stem: str = Field(min_length=1)
    question_type: str
    correct_answer: str = Field(min_length=1)
    analysis: str = Field(min_length=1)
    subject_id: int
    chapter_id: int
    knowledge_point_id: int
    difficulty: str = "medium"
    importance: str = "normal"
    source: str = "self_built"
    year: int | None = None
    school: str | None = None
    has_image: bool = False
    stem_image_url: str | None = None
    analysis_image_url: str | None = None
    status: str = "draft"
    options: list[QuestionOptionIn] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_options(self) -> "QuestionBase":
        if self.question_type in {"single_choice", "multiple_choice"} and len(self.options) < 2:
            raise ValueError("选择题至少需要 2 个选项")
        if self.question_type == "true_false" and not self.options:
            self.options = [
                QuestionOptionIn(option_key="A", content="正确", sort_order=1),
                QuestionOptionIn(option_key="B", content="错误", sort_order=2),
            ]
        return self


class QuestionCreate(QuestionBase):
    pass


class QuestionUpdate(BaseModel):
    stem: str | None = None
    question_type: str | None = None
    correct_answer: str | None = None
    analysis: str | None = None
    subject_id: int | None = None
    chapter_id: int | None = None
    knowledge_point_id: int | None = None
    difficulty: str | None = None
    importance: str | None = None
    source: str | None = None
    year: int | None = None
    school: str | None = None
    has_image: bool | None = None
    stem_image_url: str | None = None
    analysis_image_url: str | None = None
    status: str | None = None
    options: list[QuestionOptionIn] | None = None
    tags: list[str] | None = None


class QuestionOut(BaseModel):
    id: int
    stem: str
    question_type: str
    correct_answer: str
    analysis: str
    subject_id: int
    chapter_id: int
    knowledge_point_id: int
    subject_name: str | None = None
    chapter_name: str | None = None
    knowledge_point_name: str | None = None
    difficulty: str
    importance: str
    source: str
    year: int | None
    school: str | None
    has_image: bool
    stem_image_url: str | None
    analysis_image_url: str | None
    status: str
    practice_count: int
    correct_count: int
    wrong_count: int
    correct_rate: float
    favorite_count: int
    feedback_count: int
    note_count: int = 0
    comment_count: int = 0
    like_count: int = 0
    options: list[QuestionOptionOut] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    is_favorited: bool = False
    is_liked: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionListOut(BaseModel):
    id: int
    stem: str
    question_type: str
    subject_id: int
    chapter_id: int
    knowledge_point_id: int
    subject_name: str | None = None
    chapter_name: str | None = None
    knowledge_point_name: str | None = None
    difficulty: str
    importance: str
    source: str
    year: int | None
    status: str
    practice_count: int
    correct_rate: float
    favorite_count: int
    feedback_count: int
    note_count: int = 0
    comment_count: int = 0
    like_count: int = 0
    tags: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class QuestionBatchIn(BaseModel):
    ids: list[int] = Field(min_length=1)
    action: str
    subject_id: int | None = None
    chapter_id: int | None = None
    knowledge_point_id: int | None = None
    difficulty: str | None = None
    tags: list[str] | None = None


class DuplicateCheckIn(BaseModel):
    stem: str
    threshold: float = Field(default=0.82, ge=0, le=1)


class DuplicateItemOut(BaseModel):
    question_id: int
    stem: str
    similarity: float
    duplicate_type: str


class ImportPreviewOut(BaseModel):
    import_record_id: int
    total_count: int
    valid_count: int
    failed_count: int
    duplicate_count: int
    rows: list[dict]


class ImportTaxonomyMappingIn(BaseModel):
    row_number: int | None = None
    subject_name: str | None = None
    chapter_name: str | None = None
    knowledge_point_name: str | None = None
    target_subject_id: int | None = None
    target_chapter_id: int | None = None
    target_knowledge_point_id: int | None = None
    skip: bool = False


class ImportConfirmIn(BaseModel):
    import_record_id: int
    auto_create_taxonomy: bool = True
    skip_duplicates: bool = True
    taxonomy_mappings: list[ImportTaxonomyMappingIn] = Field(default_factory=list)

class ImportRecordOut(BaseModel):
    id: int
    file_name: str
    status: str
    total_count: int
    success_count: int
    failed_count: int
    skipped_count: int
    duplicate_count: int
    error_report_path: str | None
    created_at: datetime

    model_config = {"from_attributes": True}