from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserAnswer(Base, TimestampMixin):
    __tablename__ = "user_answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    mode: Mapped[str] = mapped_column(String(50), default="practice", index=True)
    time_spent_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user = relationship("User")
    question = relationship("Question")


class UserFavorite(Base, TimestampMixin):
    __tablename__ = "user_favorites"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_favorite_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)

    user = relationship("User")
    question = relationship("Question")


class UserWrongQuestion(Base, TimestampMixin):
    __tablename__ = "user_wrong_questions"
    __table_args__ = (UniqueConstraint("user_id", "question_id", name="uq_user_wrong_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    wrong_count: Mapped[int] = mapped_column(Integer, default=1, index=True)
    last_wrong_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_answer_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    removed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

    user = relationship("User")
    question = relationship("Question")

