from datetime import datetime

from sqlalchemy import (
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

from app.db.database import (
    Base
)


class CurriculumQuestionGroup(Base):

    __tablename__ = "curriculum_question_groups"

    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "page_number",
            "group_key",
            name="uq_curriculum_question_group"
        ),
    )


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )


    document_id: Mapped[int] = mapped_column(
        ForeignKey(
            "curriculum_documents.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True
    )


    lesson_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )


    group_key: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )


    question_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )


    question_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="standard"
    )


    instructions: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class CurriculumQuestionGroupChunk(Base):

    __tablename__ = "curriculum_question_group_chunks"

    __table_args__ = (
        UniqueConstraint(
            "question_group_id",
            "chunk_id",
            name="uq_question_group_chunk"
        ),
    )


    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )


    question_group_id: Mapped[int] = mapped_column(
        ForeignKey(
            "curriculum_question_groups.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    chunk_id: Mapped[int] = mapped_column(
        ForeignKey(
            "curriculum_chunks.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="question"
    )


    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )