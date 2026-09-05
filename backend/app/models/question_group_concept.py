from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column
)

from app.db.database import (
    Base
)


class CurriculumQuestionGroupConcept(Base):

    __tablename__ = (
        "curriculum_question_group_concepts"
    )

    __table_args__ = (
        UniqueConstraint(
            "question_group_id",
            "concept_id",
            name=(
                "uq_curriculum_question_group_concept"
            )
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


    concept_id: Mapped[int] = mapped_column(
        ForeignKey(
            "curriculum_concepts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )


    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )