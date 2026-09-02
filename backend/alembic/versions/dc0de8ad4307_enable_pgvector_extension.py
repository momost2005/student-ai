"""enable pgvector extension

Revision ID: dc0de8ad4307
Revises: cf04a1da4408
Create Date: 2026-09-01 18:54:07.060944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc0de8ad4307'
down_revision: Union[str, Sequence[str], None] = 'cf04a1da4408'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE EXTENSION IF NOT EXISTS vector"
    )


def downgrade() -> None:
    op.execute(
        "DROP EXTENSION IF EXISTS vector"
    )
