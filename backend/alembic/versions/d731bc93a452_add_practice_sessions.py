"""add practice sessions

Revision ID: d731bc93a452
Revises: f09c45e8b781
Create Date: 2026-09-06 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d731bc93a452"
down_revision: Union[str, Sequence[str], None] = "f09c45e8b781"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("curriculum_id", sa.Integer(), nullable=False),
        sa.Column(
            "lesson_number",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False
        ),
        sa.Column(
            "target_question_count",
            sa.Integer(),
            nullable=False
        ),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'exhausted')",
            name="ck_practice_session_status"
        ),
        sa.CheckConstraint(
            "target_question_count > 0",
            name="ck_practice_session_target_count"
        ),
        sa.ForeignKeyConstraint(
            ["curriculum_id"],
            ["curricula.id"]
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(
        op.f("ix_practice_sessions_curriculum_id"),
        "practice_sessions",
        ["curriculum_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_practice_sessions_lesson_number"),
        "practice_sessions",
        ["lesson_number"],
        unique=False
    )
    op.create_index(
        op.f("ix_practice_sessions_status"),
        "practice_sessions",
        ["status"],
        unique=False
    )
    op.create_index(
        op.f("ix_practice_sessions_student_id"),
        "practice_sessions",
        ["student_id"],
        unique=False
    )

    op.create_table(
        "practice_session_questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column(
            "logical_question_key",
            sa.String(length=200),
            nullable=False
        ),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("question_payload", sa.Text(), nullable=False),
        sa.Column("attempt_id", sa.Integer(), nullable=True),
        sa.Column("served_at", sa.DateTime(), nullable=False),
        sa.Column("answered_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["practice_attempts.id"],
            ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["practice_sessions.id"],
            ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "attempt_id",
            name="uq_practice_session_question_attempt"
        ),
        sa.UniqueConstraint(
            "session_id",
            "logical_question_key",
            name="uq_practice_session_logical_question"
        ),
        sa.UniqueConstraint(
            "session_id",
            "sequence",
            name="uq_practice_session_question_sequence"
        )
    )
    op.create_index(
        op.f("ix_practice_session_questions_attempt_id"),
        "practice_session_questions",
        ["attempt_id"],
        unique=False
    )
    op.create_index(
        op.f("ix_practice_session_questions_logical_question_key"),
        "practice_session_questions",
        ["logical_question_key"],
        unique=False
    )
    op.create_index(
        op.f("ix_practice_session_questions_session_id"),
        "practice_session_questions",
        ["session_id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_practice_session_questions_session_id"),
        table_name="practice_session_questions"
    )
    op.drop_index(
        op.f("ix_practice_session_questions_logical_question_key"),
        table_name="practice_session_questions"
    )
    op.drop_index(
        op.f("ix_practice_session_questions_attempt_id"),
        table_name="practice_session_questions"
    )
    op.drop_table("practice_session_questions")
    op.drop_index(
        op.f("ix_practice_sessions_student_id"),
        table_name="practice_sessions"
    )
    op.drop_index(
        op.f("ix_practice_sessions_status"),
        table_name="practice_sessions"
    )
    op.drop_index(
        op.f("ix_practice_sessions_lesson_number"),
        table_name="practice_sessions"
    )
    op.drop_index(
        op.f("ix_practice_sessions_curriculum_id"),
        table_name="practice_sessions"
    )
    op.drop_table("practice_sessions")
