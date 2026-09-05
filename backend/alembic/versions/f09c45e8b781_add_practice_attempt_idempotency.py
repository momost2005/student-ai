"""add practice attempt idempotency

Revision ID: f09c45e8b781
Revises: ff2688a033ef
Create Date: 2026-09-06 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f09c45e8b781"
down_revision: Union[str, Sequence[str], None] = "ff2688a033ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "practice_attempts",
        sa.Column(
            "idempotency_key",
            sa.String(length=200),
            nullable=True
        )
    )
    op.create_unique_constraint(
        "uq_practice_attempt_idempotency",
        "practice_attempts",
        [
            "student_id",
            "curriculum_id",
            "idempotency_key"
        ]
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_practice_attempt_idempotency",
        "practice_attempts",
        type_="unique"
    )
    op.drop_column(
        "practice_attempts",
        "idempotency_key"
    )
