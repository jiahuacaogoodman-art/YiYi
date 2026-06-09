"""learning interactions

Revision ID: 20260609_0002
Revises: 20260608_0001
Create Date: 2026-06-09 13:20:00.000000
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260609_0002"
down_revision: str | None = "20260608_0001"
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


def drop_timestamp_indexes(table: str) -> None:
    op.drop_index(f"ix_{table}_deleted_at", table_name=table)
    op.drop_index(f"ix_{table}_updated_at", table_name=table)
    op.drop_index(f"ix_{table}_created_at", table_name=table)


def upgrade() -> None:
    op.create_table(
        "user_notes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_user_notes_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_user_notes_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_notes")),
    )
    op.create_index(op.f("ix_user_notes_question_id"), "user_notes", ["question_id"])
    op.create_index(op.f("ix_user_notes_user_id"), "user_notes", ["user_id"])
    create_timestamp_indexes("user_notes")

    op.create_table(
        "question_comments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_pinned", sa.Boolean(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_question_comments_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_question_comments_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_comments")),
    )
    op.create_index(op.f("ix_question_comments_is_pinned"), "question_comments", ["is_pinned"])
    op.create_index(op.f("ix_question_comments_question_id"), "question_comments", ["question_id"])
    op.create_index(op.f("ix_question_comments_user_id"), "question_comments", ["user_id"])
    create_timestamp_indexes("question_comments")

    op.create_table(
        "question_likes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"], name=op.f("fk_question_likes_question_id_questions")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_question_likes_user_id_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_question_likes")),
        sa.UniqueConstraint("user_id", "question_id", name="uq_user_question_like"),
    )
    op.create_index(op.f("ix_question_likes_question_id"), "question_likes", ["question_id"])
    op.create_index(op.f("ix_question_likes_user_id"), "question_likes", ["user_id"])
    create_timestamp_indexes("question_likes")


def downgrade() -> None:
    drop_timestamp_indexes("question_likes")
    op.drop_index(op.f("ix_question_likes_user_id"), table_name="question_likes")
    op.drop_index(op.f("ix_question_likes_question_id"), table_name="question_likes")
    op.drop_table("question_likes")

    drop_timestamp_indexes("question_comments")
    op.drop_index(op.f("ix_question_comments_user_id"), table_name="question_comments")
    op.drop_index(op.f("ix_question_comments_question_id"), table_name="question_comments")
    op.drop_index(op.f("ix_question_comments_is_pinned"), table_name="question_comments")
    op.drop_table("question_comments")

    drop_timestamp_indexes("user_notes")
    op.drop_index(op.f("ix_user_notes_user_id"), table_name="user_notes")
    op.drop_index(op.f("ix_user_notes_question_id"), table_name="user_notes")
    op.drop_table("user_notes")