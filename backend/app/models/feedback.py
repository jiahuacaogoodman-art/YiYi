from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class QuestionFeedback(Base, TimestampMixin):
    __tablename__ = "question_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    feedback_type: Mapped[str] = mapped_column(String(50), index=True)
    content: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    handler_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    handled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handler_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    question = relationship("Question")
    user = relationship("User", foreign_keys=[user_id])
    handler = relationship("User", foreign_keys=[handler_id])

