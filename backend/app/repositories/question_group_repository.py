from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.curriculum import (
    CurriculumChunk
)

from app.models.question_group import (
    CurriculumQuestionGroup,
    CurriculumQuestionGroupChunk
)


class QuestionGroupRepository:

    def get_group_for_chunk(
        self,
        db: Session,
        chunk_id: int
    ) -> CurriculumQuestionGroup | None:

        statement = (
            select(
                CurriculumQuestionGroup
            )
            .join(
                CurriculumQuestionGroupChunk,
                CurriculumQuestionGroupChunk.question_group_id
                == CurriculumQuestionGroup.id
            )
            .where(
                CurriculumQuestionGroupChunk.chunk_id
                == chunk_id
            )
            .order_by(
                CurriculumQuestionGroup.id
            )
            .limit(1)
        )


        return (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )


    def get_group_chunks(
        self,
        db: Session,
        question_group_id: int
    ) -> list[
        tuple[
            CurriculumQuestionGroupChunk,
            CurriculumChunk
        ]
    ]:

        statement = (
            select(
                CurriculumQuestionGroupChunk,
                CurriculumChunk
            )
            .join(
                CurriculumChunk,
                CurriculumQuestionGroupChunk.chunk_id
                == CurriculumChunk.id
            )
            .where(
                CurriculumQuestionGroupChunk.question_group_id
                == question_group_id
            )
            .order_by(
                CurriculumQuestionGroupChunk.sequence,
                CurriculumQuestionGroupChunk.id
            )
        )


        return list(
            db.execute(
                statement
            ).all()
        )