from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.database import (
    Base
)


class PracticeAttemptQuestionIdentity(Base):

    __tablename__ = (
        "practice_attempt_question_identities"
    )

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            name=(
                "uq_practice_attempt_question_identity"
            )
        ),
    )


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )


    attempt_id: Mapped[int] = mapped_column(
        ForeignKey(
            "practice_attempts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    # -------------------------------------------------
    # Current reference.
    #
    # May become NULL if the question group is deleted
    # during curriculum reprocessing.
    # -------------------------------------------------

    question_group_id: Mapped[int | None] = (
        mapped_column(
            ForeignKey(
                "curriculum_question_groups.id",
                ondelete="SET NULL"
            ),
            nullable=True,
            index=True
        )
    )


    # -------------------------------------------------
    # Historical immutable identity.
    #
    # Examples:
    #
    # group:1
    # chunk:158
    # -------------------------------------------------

    logical_question_key: Mapped[str] = (
        mapped_column(
            String(200),
            nullable=False,
            index=True
        )
    )


    # -------------------------------------------------
    # Question-group metadata snapshots
    # -------------------------------------------------

    group_key: Mapped[str | None] = (
        mapped_column(
            String(150),
            nullable=True
        )
    )


    question_type: Mapped[str | None] = (
        mapped_column(
            String(50),
            nullable=True
        )
    )


    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="evaluation"
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )