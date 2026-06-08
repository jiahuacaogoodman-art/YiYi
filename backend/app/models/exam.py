from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Exam(Base, TimestampMixin):
    __tablename__ = "exams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    exam_type: Mapped[str] = mapped_column(String(50), default="mock", index=True)
    subject_id: Mapped[int | None] = mapped_column(ForeignKey("subjects.id"), nullable=True, index=True)
    total_score: Mapped[float] = mapped_column(Float, default=100)
    pass_score: Mapped[float] = mapped_column(Float, default=60)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    status: Mapped[str] = mapped_column(String(40), default="draft", index=True)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    subject = relationship("Subject")
    created_by = relationship("User")
    questions: Mapped[list["ExamQuestion"]] = relationship(
        back_populates="exam",
        cascade="all, delete-orphan",
        order_by="ExamQuestion.sort_order",
    )


class ExamQuestion(Base, TimestampMixin):
    __tablename__ = "exam_questions"
    __table_args__ = (UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    score: Mapped[float] = mapped_column(Float, default=5)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    exam: Mapped[Exam] = relationship(back_populates="questions")
    question = relationship("Question")


class ExamRecord(Base, TimestampMixin):
    __tablename__ = "exam_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exams.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_count: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="in_progress", index=True)

    exam = relationship("Exam")
    user = relationship("User")
    answers: Mapped[list["ExamRecordAnswer"]] = relationship(
        back_populates="record",
        cascade="all, delete-orphan",
    )


class ExamRecordAnswer(Base, TimestampMixin):
    __tablename__ = "exam_record_answers"
    __table_args__ = (UniqueConstraint("record_id", "question_id", name="uq_exam_record_question"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    record_id: Mapped[int] = mapped_column(ForeignKey("exam_records.id"), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"), index=True)
    answer: Mapped[str] = mapped_column(Text)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    score: Mapped[float] = mapped_column(Float, default=0)

    record: Mapped[ExamRecord] = relationship(back_populates="answers")
    question = relationship("Question")

