from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.database import Base


class PracticeSession(Base):
    __tablename__ = "practice_sessions"

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'completed', 'exhausted')",
            name="ck_practice_session_status"
        ),
        CheckConstraint(
            "target_question_count > 0",
            name="ck_practice_session_target_count"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        index=True
    )

    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curricula.id"),
        nullable=False,
        index=True
    )

    lesson_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True
    )

    target_question_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class PracticeSessionQuestion(Base):
    __tablename__ = "practice_session_questions"

    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "logical_question_key",
            name="uq_practice_session_logical_question"
        ),
        UniqueConstraint(
            "session_id",
            "sequence",
            name="uq_practice_session_question_sequence"
        ),
        UniqueConstraint(
            "attempt_id",
            name="uq_practice_session_question_attempt"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    session_id: Mapped[int] = mapped_column(
        ForeignKey(
            "practice_sessions.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    logical_question_key: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        index=True
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    question_payload: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    attempt_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "practice_attempts.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    served_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    answered_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
