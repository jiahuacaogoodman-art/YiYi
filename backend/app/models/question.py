from __future__ import annotations

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    stem: Mapped[str] = mapped_column(Text)
    question_type: Mapped[str] = mapped_column(String(40), index=True)
    correct_answer: Mapped[str] = mapped_column(Text)
    analysis: Mapped[str] = mapped_column(Text)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), index=True)
    knowledge_point_id: Mapped[int] = mapped_column(ForeignKey("knowledge_points.id"), index=True)
    difficulty: Mapped[str] = mapped_column(String(30), default="medium", index=True)
    importance: Mapped[str] = mapped_column(String(30), default="normal", index=True)
    source: Mapped[str] = mapped_column(String(50), default="self_built", index=True)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    school: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    has_image: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    stem_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    analysis_image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    practice_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_rate: Mapped[float] = mapped_column(Float, default=0)
    favorite_count: Mapped[int] = mapped_column(Integer, default=0)
    feedback_count: Mapped[int] = mapped_column(Integer, default=0)

    subject = relationship("Subject")
    chapter = relationship("Chapter")
    knowledge_point = relationship("KnowledgePoint")
    created_by = relationship("User")
    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="QuestionOption.option_key",
    )
    tags: Mapped[list["QuestionTag"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
    )


class QuestionOption(Base, TimestampMixin):
    __tablename__ = "question_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    option_key: Mapped[str] = mapped_column(String(5), index=True)
    content: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    question: Mapped[Question] = relationship(back_populates="options")


class QuestionTag(Base, TimestampMixin):
    __tablename__ = "question_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    tag: Mapped[str] = mapped_column(String(80), index=True)

    question: Mapped[Question] = relationship(back_populates="tags")

