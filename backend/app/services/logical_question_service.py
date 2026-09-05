from sqlalchemy import (
    func,
    select
)

from sqlalchemy.orm import (
    Session
)

from app.models.curriculum import (
    CurriculumChunk,
    CurriculumDocument,
    CurriculumPage
)

from app.models.practice_attempt_question import (
    PracticeAttemptQuestionIdentity
)

from app.models.question_group import (
    CurriculumQuestionGroup,
    CurriculumQuestionGroupChunk
)


class LogicalQuestionService:

    # -------------------------------------------------
    # Resolve a CURRENT curriculum chunk.
    # -------------------------------------------------

    def get_question_key_for_chunk(
        self,
        db: Session,
        chunk_id: int
    ) -> str:

        statement = (
            select(
                CurriculumQuestionGroup.id
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


        group_id = (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )


        if group_id is not None:

            return (
                f"group:{group_id}"
            )


        return (
            f"chunk:{chunk_id}"
        )


    # -------------------------------------------------
    # Resolve a HISTORICAL student attempt.
    #
    # Priority:
    #
    # 1. Saved historical snapshot
    # 2. Current chunk mapping
    # 3. Question-content snapshot fallback
    # -------------------------------------------------

    def get_question_key_for_attempt(
        self,
        db: Session,
        attempt
    ) -> str:

        # ---------------------------------------------
        # A. Historical identity is the most trusted
        #    source.
        # ---------------------------------------------

        identity_statement = (
            select(
                PracticeAttemptQuestionIdentity
            )
            .where(
                PracticeAttemptQuestionIdentity.attempt_id
                == attempt.id
            )
        )


        identity = (
            db.execute(
                identity_statement
            )
            .scalar_one_or_none()
        )


        if identity:

            return (
                identity.logical_question_key
            )


        # ---------------------------------------------
        # B. Older attempt without snapshot:
        #    resolve from current curriculum mapping.
        # ---------------------------------------------

        if attempt.chunk_id is not None:

            return (
                self.get_question_key_for_chunk(
                    db=db,
                    chunk_id=attempt.chunk_id
                )
            )


        # ---------------------------------------------
        # C. Last-resort historical fallback.
        # ---------------------------------------------

        return (
            f"snapshot:"
            f"{attempt.question_number}:"
            f"{attempt.question_content}"
        )


    # -------------------------------------------------
    # Count logical practice questions.
    #
    # Total =
    #
    # distinct question groups
    # +
    # ungrouped practice chunks
    # -------------------------------------------------

    def count_lesson_logical_practice_questions(
        self,
        db: Session,
        curriculum_id: int,
        lesson_number: str
    ) -> int:

        # ---------------------------------------------
        # A. Grouped logical questions
        # ---------------------------------------------

        grouped_statement = (
            select(
                func.count(
                    func.distinct(
                        CurriculumQuestionGroup.id
                    )
                )
            )
            .join(
                CurriculumQuestionGroupChunk,
                CurriculumQuestionGroupChunk.question_group_id
                == CurriculumQuestionGroup.id
            )
            .join(
                CurriculumChunk,
                CurriculumQuestionGroupChunk.chunk_id
                == CurriculumChunk.id
            )
            .join(
                CurriculumPage,
                CurriculumChunk.page_id
                == CurriculumPage.id
            )
            .join(
                CurriculumDocument,
                CurriculumPage.document_id
                == CurriculumDocument.id
            )
            .where(
                CurriculumDocument.curriculum_id
                == curriculum_id,

                CurriculumChunk.lesson_number
                == lesson_number,

                CurriculumChunk.chunk_type
                == "practice_question"
            )
        )


        grouped_count = (
            db.execute(
                grouped_statement
            )
            .scalar_one()
        )


        # ---------------------------------------------
        # B. Practice chunks outside any group
        # ---------------------------------------------

        ungrouped_statement = (
            select(
                func.count(
                    CurriculumChunk.id
                )
            )
            .join(
                CurriculumPage,
                CurriculumChunk.page_id
                == CurriculumPage.id
            )
            .join(
                CurriculumDocument,
                CurriculumPage.document_id
                == CurriculumDocument.id
            )
            .outerjoin(
                CurriculumQuestionGroupChunk,
                CurriculumQuestionGroupChunk.chunk_id
                == CurriculumChunk.id
            )
            .where(
                CurriculumDocument.curriculum_id
                == curriculum_id,

                CurriculumChunk.lesson_number
                == lesson_number,

                CurriculumChunk.chunk_type
                == "practice_question",

                CurriculumQuestionGroupChunk.id
                .is_(None)
            )
        )


        ungrouped_count = (
            db.execute(
                ungrouped_statement
            )
            .scalar_one()
        )


        return (
            grouped_count
            +
            ungrouped_count
        )