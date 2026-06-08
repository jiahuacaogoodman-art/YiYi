from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ImportRecord(Base, TimestampMixin):
    __tablename__ = "import_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    importer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    file_name: Mapped[str] = mapped_column(String(255))
    stored_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="preview", index=True)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    success_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, default=0)
    skipped_count: Mapped[int] = mapped_column(Integer, default=0)
    duplicate_count: Mapped[int] = mapped_column(Integer, default=0)
    error_report_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    summary_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    importer = relationship("User")

