"""initial schema

Revision ID: 20260608_0001
Revises:
Create Date: 2026-06-08 00:00:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    ]


def create_timestamp_indexes(table: str) -> None:
    op.create_index(f"ix_{table}_created_at", table, ["created_at"])
    op.create_index(f"ix_{table}_updated_at", table, ["updated_at"])
    op.create_index(f"ix_{table}_deleted_at", table, ["deleted_at"])


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("label", sa.String(length=80), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_roles")),
    )
    op.create_index(op.f("ix_roles_name"), "roles", ["name"], unique=True)
    create_timestamp_indexes("roles")

    op.create_table(
        "subjects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("icon", sa.String(length=100), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_subjects")),
    )
    op.create_index(op.f("ix_subjects_code"), "subjects", ["code"], unique=True)
    op.create_index(op.f("ix_subjects_is_enabled"), "subjects", ["is_enabled"])
    op.create_index(op.f("ix_subjects_name"), "subjects", ["name"], unique=True)
    op.create_index(op.f("ix_subjects_sort_order"), "subjects", ["sort_order"])
    create_timestamp_indexes("subjects")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=80), nullable=False),
        sa.Column("nickname", sa.String(length=80), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=30), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], name=op.f("fk_users_role_id_roles")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_is_active"), "users", ["is_active"])
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"])
    op.create_index(op.f("ix_users_phone"), "users", ["phone"], unique=True)
    op.create_index(op.f("ix_users_role_id"), "users", ["role_id"])
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)
    create_timestamp_indexes("users")

    op.create_table(
        "chapters",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_chapters_subject_id_subjects")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_chapters")),
    )
    op.create_index(op.f("ix_chapters_code"), "chapters", ["code"])
    op.create_index(op.f("ix_chapters_is_enabled"), "chapters", ["is_enabled"])
    op.create_index(op.f("ix_chapters_name"), "chapters", ["name"])
    op.create_index(op.f("ix_chapters_sort_order"), "chapters", ["sort_order"])
    op.create_index(op.f("ix_chapters_subject_id"), "chapters", ["subject_id"])
    create_timestamp_indexes("chapters")

    op.create_table(
        "knowledge_points",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("chapter_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("label", sa.String(length=160), nullable=True),
        sa.Column("importance_level", sa.String(length=30), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], name=op.f("fk_knowledge_points_chapter_id_chapters")),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_knowledge_points_subject_id_subjects")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_knowledge_points")),
    )
    op.create_index(op.f("ix_knowledge_points_chapter_id"), "knowledge_points", ["chapter_id"])
    op.create_index(op.f("ix_knowledge_points_importance_level"), "knowledge_points", ["importance_level"])
    op.create_index(op.f("ix_knowledge_points_is_enabled"), "knowledge_points", ["is_enabled"])
    op.create_index(op.f("ix_knowledge_points_label"), "knowledge_points", ["label"])
    op.create_index(op.f("ix_knowledge_points_name"), "knowledge_points", ["name"])
    op.create_index(op.f("ix_knowledge_points_sort_order"), "knowledge_points", ["sort_order"])
    op.create_index(op.f("ix_knowledge_points_subject_id"), "knowledge_points", ["subject_id"])
    create_timestamp_indexes("knowledge_points")

    op.create_table(
        "exams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("exam_type", sa.String(length=50), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=True),
        sa.Column("total_score", sa.Float(), nullable=False),
        sa.Column("pass_score", sa.Float(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], name=op.f("fk_exams_created_by_id_users")),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_exams_subject_id_subjects")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exams")),
    )
    op.create_index(op.f("ix_exams_created_by_id"), "exams", ["created_by_id"])
    op.create_index(op.f("ix_exams_exam_type"), "exams", ["exam_type"])
    op.create_index(op.f("ix_exams_is_public"), "exams", ["is_public"])
    op.create_index(op.f("ix_exams_name"), "exams", ["name"])
    op.create_index(op.f("ix_exams_status"), "exams", ["status"])
    op.create_index(op.f("ix_exams_subject_id"), "exams", ["subject_id"])
    create_timestamp_indexes("exams")

    op.create_table(
        "import_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("importer_id", sa.Integer(), nullable=True),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("stored_file_path", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("success_count", sa.Integer(), nullable=False),
        sa.Column("failed_count", sa.Integer(), nullable=False),
        sa.Column("skipped_count", sa.Integer(), nullable=False),
        sa.Column("duplicate_count", sa.Integer(), nullable=False),
        sa.Column("error_report_path", sa.String(length=500), nullable=True),
        sa.Column("summary_json", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["importer_id"], ["users.id"], name=op.f("fk_import_records_importer_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_import_records")),
    )
    op.create_index(op.f("ix_import_records_importer_id"), "import_records", ["importer_id"])
    op.create_index(op.f("ix_import_records_status"), "import_records", ["status"])
    create_timestamp_indexes("import_records")

    op.create_table(
        "operation_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("operator_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=False),
        sa.Column("target_id", sa.String(length=80), nullable=True),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("ip_address", sa.String(length=80), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["operator_id"], ["users.id"], name=op.f("fk_operation_logs_operator_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_operation_logs")),
    )
    op.create_index(op.f("ix_operation_logs_action"), "operation_logs", ["action"])
    op.create_index(op.f("ix_operation_logs_operator_id"), "operation_logs", ["operator_id"])
    op.create_index(op.f("ix_operation_logs_target_id"), "operation_logs", ["target_id"])
    op.create_index(op.f("ix_operation_logs_target_type"), "operation_logs", ["target_type"])
    create_timestamp_indexes("operation_logs")

    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=40), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("analysis", sa.Text(), nullable=False),
        sa.Column("subject_id", sa.Integer(), nullable=False),
        sa.Column("chapter_id", sa.Integer(), nullable=False),
        sa.Column("knowledge_point_id", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.String(length=30), nullable=False),
        sa.Column("importance", sa.String(length=30), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("school", sa.String(length=160), nullable=True),
        sa.Column("has_image", sa.Boolean(), nullable=False),
        sa.Column("stem_image_url", sa.String(length=500), nullable=True),
        sa.Column("analysis_image_url", sa.String(length=500), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_by_id", sa.Integer(), nullable=True),
        sa.Column("practice_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("wrong_count", sa.Integer(), nullable=False),
        sa.Column("correct_rate", sa.Float(), nullable=False),
        sa.Column("favorite_count", sa.Integer(), nullable=False),
        sa.Column("feedback_count", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["chapter_id"], ["chapters.id"], name=op.f("fk_questions_chapter_id_chapters")),
        sa.ForeignKeyConstraint(["created_by_id"], ["users.id"], name=op.f("fk_questions_created_by_id_users")),
        sa.ForeignKeyConstraint(["knowledge_point_id"], ["knowledge_points.id"], name=op.f("fk_questions_knowledge_point_id_knowledge_points")),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], name=op.f("fk_questions_subject_id_subjects")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_questions")),
    )
    for column in [
        "chapter_id",
        "created_by_id",
        "difficulty",
        "has_image",
        "importance",
        "knowledge_point_id",
        "question_type",
        "school",
        "source",
        "status",
        "subject_id",
        "year",
    ]:
        op.create_index(f"ix_questions_{column}", "questions", [column])
    create_timestamp_indexes("questions")

    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_public", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_system_settings")),
    )
    op.create_index(op.f("ix_system_settings_is_public"), "system_settings", ["is_public"])
    op.create_index(op.f("ix_system_settings_key"), "system_settings", ["key"], unique=True)
    create_timestamp_indexes("system_settings")

    op.create_table(
        "exam_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], name=op.f("fk_exam_questions_exam_id_exams")),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_exam_questions_question_id_questions")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exam_questions")),
        sa.UniqueConstraint("exam_id", "question_id", name="uq_exam_question"),
    )
    op.create_index(op.f("ix_exam_questions_exam_id"), "exam_questions", ["exam_id"])
    op.create_index(op.f("ix_exam_questions_question_id"), "exam_questions", ["question_id"])
    create_timestamp_indexes("exam_questions")

    op.create_table(
        "exam_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("exam_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("wrong_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], name=op.f("fk_exam_records_exam_id_exams")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_exam_records_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exam_records")),
    )
    op.create_index(op.f("ix_exam_records_exam_id"), "exam_records", ["exam_id"])
    op.create_index(op.f("ix_exam_records_started_at"), "exam_records", ["started_at"])
    op.create_index(op.f("ix_exam_records_status"), "exam_records", ["status"])
    op.create_index(op.f("ix_exam_records_submitted_at"), "exam_records", ["submitted_at"])
    op.create_index(op.f("ix_exam_records_user_id"), "exam_records", ["user_id"])
    create_timestamp_indexes("exam_records")

    op.create_table(
        "question_feedback",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("feedback_type", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("handler_id", sa.Integer(), nullable=True),
        sa.Column("handled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("handler_note", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["handler_id"], ["users.id"], name=op.f("fk_question_feedback_handler_id_users")),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_question_feedback_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_question_feedback_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_feedback")),
    )
    op.create_index(op.f("ix_question_feedback_feedback_type"), "question_feedback", ["feedback_type"])
    op.create_index(op.f("ix_question_feedback_handler_id"), "question_feedback", ["handler_id"])
    op.create_index(op.f("ix_question_feedback_question_id"), "question_feedback", ["question_id"])
    op.create_index(op.f("ix_question_feedback_status"), "question_feedback", ["status"])
    op.create_index(op.f("ix_question_feedback_user_id"), "question_feedback", ["user_id"])
    create_timestamp_indexes("question_feedback")

    op.create_table(
        "question_options",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("option_key", sa.String(length=5), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_question_options_question_id_questions")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_options")),
    )
    op.create_index(op.f("ix_question_options_option_key"), "question_options", ["option_key"])
    op.create_index(op.f("ix_question_options_question_id"), "question_options", ["question_id"])
    create_timestamp_indexes("question_options")

    op.create_table(
        "question_tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(length=80), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_question_tags_question_id_questions")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_tags")),
    )
    op.create_index(op.f("ix_question_tags_question_id"), "question_tags", ["question_id"])
    op.create_index(op.f("ix_question_tags_tag"), "question_tags", ["tag"])
    create_timestamp_indexes("question_tags")

    op.create_table(
        "user_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("mode", sa.String(length=50), nullable=False),
        sa.Column("time_spent_seconds", sa.Integer(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_user_answers_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_answers_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_answers")),
    )
    op.create_index(op.f("ix_user_answers_is_correct"), "user_answers", ["is_correct"])
    op.create_index(op.f("ix_user_answers_mode"), "user_answers", ["mode"])
    op.create_index(op.f("ix_user_answers_question_id"), "user_answers", ["question_id"])
    op.create_index(op.f("ix_user_answers_user_id"), "user_answers", ["user_id"])
    create_timestamp_indexes("user_answers")

    op.create_table(
        "user_favorites",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_user_favorites_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_favorites_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_favorites")),
        sa.UniqueConstraint("user_id", "question_id", name="uq_user_favorite_question"),
    )
    op.create_index(op.f("ix_user_favorites_question_id"), "user_favorites", ["question_id"])
    op.create_index(op.f("ix_user_favorites_user_id"), "user_favorites", ["user_id"])
    create_timestamp_indexes("user_favorites")

    op.create_table(
        "user_wrong_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("wrong_count", sa.Integer(), nullable=False),
        sa.Column("last_wrong_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_answer_correct", sa.Boolean(), nullable=False),
        sa.Column("removed_at", sa.DateTime(timezone=True), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_user_wrong_questions_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_wrong_questions_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_wrong_questions")),
        sa.UniqueConstraint("user_id", "question_id", name="uq_user_wrong_question"),
    )
    op.create_index(op.f("ix_user_wrong_questions_last_answer_correct"), "user_wrong_questions", ["last_answer_correct"])
    op.create_index(op.f("ix_user_wrong_questions_last_wrong_at"), "user_wrong_questions", ["last_wrong_at"])
    op.create_index(op.f("ix_user_wrong_questions_question_id"), "user_wrong_questions", ["question_id"])
    op.create_index(op.f("ix_user_wrong_questions_removed_at"), "user_wrong_questions", ["removed_at"])
    op.create_index(op.f("ix_user_wrong_questions_user_id"), "user_wrong_questions", ["user_id"])
    op.create_index(op.f("ix_user_wrong_questions_wrong_count"), "user_wrong_questions", ["wrong_count"])
    create_timestamp_indexes("user_wrong_questions")

    op.create_table(
        "exam_record_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("record_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_exam_record_answers_question_id_questions")),
        sa.ForeignKeyConstraint(["record_id"], ["exam_records.id"], name=op.f("fk_exam_record_answers_record_id_exam_records")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exam_record_answers")),
        sa.UniqueConstraint("record_id", "question_id", name="uq_exam_record_question"),
    )
    op.create_index(op.f("ix_exam_record_answers_is_correct"), "exam_record_answers", ["is_correct"])
    op.create_index(op.f("ix_exam_record_answers_question_id"), "exam_record_answers", ["question_id"])
    op.create_index(op.f("ix_exam_record_answers_record_id"), "exam_record_answers", ["record_id"])
    create_timestamp_indexes("exam_record_answers")


def downgrade() -> None:
    for table in [
        "exam_record_answers",
        "user_wrong_questions",
        "user_favorites",
        "user_answers",
        "question_tags",
        "question_options",
        "question_feedback",
        "exam_records",
        "exam_questions",
        "system_settings",
        "questions",
        "operation_logs",
        "import_records",
        "exams",
        "knowledge_points",
        "chapters",
        "users",
        "subjects",
        "roles",
    ]:
        op.drop_table(table)

