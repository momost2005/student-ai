from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.curriculum import (
    CurriculumChunk,
    CurriculumConcept
)

from app.models.question_group import (
    CurriculumQuestionGroup,
    CurriculumQuestionGroupChunk,
    CurriculumQuestionGroupSolution
)

from app.models.question_group_concept import (
    CurriculumQuestionGroupConcept
)


class QuestionGroupRepository:

    def get_group(
        self,
        db: Session,
        question_group_id: int
    ) -> CurriculumQuestionGroup | None:

        return db.get(
            CurriculumQuestionGroup,
            question_group_id
        )


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


    def get_verified_solution(
        self,
        db: Session,
        question_group_id: int
    ) -> CurriculumQuestionGroupSolution | None:

        statement = (
            select(
                CurriculumQuestionGroupSolution
            )
            .where(
                CurriculumQuestionGroupSolution.question_group_id
                == question_group_id,

                CurriculumQuestionGroupSolution.verification_status
                == "verified"
            )
        )


        return (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )


    def get_group_concepts(
        self,
        db: Session,
        question_group_id: int
    ) -> list[CurriculumConcept]:

        statement = (
            select(
                CurriculumConcept
            )
            .join(
                CurriculumQuestionGroupConcept,
                CurriculumQuestionGroupConcept.concept_id
                == CurriculumConcept.id
            )
            .where(
                CurriculumQuestionGroupConcept.question_group_id
                == question_group_id
            )
            .order_by(
                CurriculumConcept.id
            )
        )


        return list(
            db.execute(
                statement
            )
            .scalars()
            .all()
        )