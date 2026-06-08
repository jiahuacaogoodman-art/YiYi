from __future__ import annotations

from pydantic import BaseModel, Field


class UserStatisticsOut(BaseModel):
    total_answers: int = 0
    correct_count: int = 0
    wrong_count: int = 0
    correct_rate: float = 0
    subject_accuracy: list[dict] = Field(default_factory=list)
    chapter_mastery: list[dict] = Field(default_factory=list)
    recent_7_days: list[dict] = Field(default_factory=list)
    high_frequency_wrong_points: list[dict] = Field(default_factory=list)
    recommended_chapters: list[dict] = Field(default_factory=list)


class DashboardStatisticsOut(BaseModel):
    total_questions: int = 0
    published_questions: int = 0
    draft_questions: int = 0
    pending_review_questions: int = 0
    today_new_questions: int = 0
    total_users: int = 0
    today_practice_count: int = 0
    feedback_count: int = 0
    subject_distribution: list[dict] = Field(default_factory=list)
    user_practice_trend: list[dict] = Field(default_factory=list)
    top_wrong_knowledge_points: list[dict] = Field(default_factory=list)
    recent_import_records: list[dict] = Field(default_factory=list)
    recent_operation_logs: list[dict] = Field(default_factory=list)

