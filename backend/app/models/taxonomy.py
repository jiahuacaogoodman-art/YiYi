from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Subject(Base, TimestampMixin):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    icon: Mapped[str | None] = mapped_column(String(100))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    chapters: Mapped[list["Chapter"]] = relationship(back_populates="subject")
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(back_populates="subject")


class Chapter(Base, TimestampMixin):
    __tablename__ = "chapters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    code: Mapped[str] = mapped_column(String(80), index=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    description: Mapped[str | None] = mapped_column(Text)

    subject: Mapped[Subject] = relationship(back_populates="chapters")
    knowledge_points: Mapped[list["KnowledgePoint"]] = relationship(back_populates="chapter")


class KnowledgePoint(Base, TimestampMixin):
    __tablename__ = "knowledge_points"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), index=True)
    chapter_id: Mapped[int] = mapped_column(ForeignKey("chapters.id"), index=True)
    name: Mapped[str] = mapped_column(String(160), index=True)
    label: Mapped[str | None] = mapped_column(String(160), index=True)
    importance_level: Mapped[str] = mapped_column(String(30), default="medium", index=True)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    subject: Mapped[Subject] = relationship(back_populates="knowledge_points")
    chapter: Mapped[Chapter] = relationship(back_populates="knowledge_points")

