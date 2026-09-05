from sqlalchemy import select

from sqlalchemy.orm import Session

from app.models.practice_attempt_question import (
    PracticeAttemptQuestionIdentity
)

from app.models.question_group import (
    CurriculumQuestionGroup,
    CurriculumQuestionGroupChunk
)


class PracticeAttemptQuestionRepository:

    def save_identity(
        self,
        db: Session,
        attempt_id: int,
        chunk_id: int
    ) -> PracticeAttemptQuestionIdentity:

        # -------------------------------------------------
        # 1. Historical snapshot is immutable.
        #
        # If this attempt already has an identity,
        # return it without recalculating anything.
        # -------------------------------------------------

        existing_statement = (
            select(
                PracticeAttemptQuestionIdentity
            )
            .where(
                PracticeAttemptQuestionIdentity.attempt_id
                == attempt_id
            )
        )


        existing_identity = (
            db.execute(
                existing_statement
            )
            .scalar_one_or_none()
        )


        if existing_identity:

            return existing_identity


        # -------------------------------------------------
        # 2. Find current logical question group
        # -------------------------------------------------

        group_statement = (
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


        group = (
            db.execute(
                group_statement
            )
            .scalar_one_or_none()
        )


        # -------------------------------------------------
        # 3. Build historical identity
        # -------------------------------------------------

        if group:

            logical_question_key = (
                f"group:{group.id}"
            )

            question_group_id = (
                group.id
            )

            group_key = (
                group.group_key
            )

            question_type = (
                group.question_type
            )


        else:

            logical_question_key = (
                f"chunk:{chunk_id}"
            )

            question_group_id = None
            group_key = None
            question_type = "standard"


        # -------------------------------------------------
        # 4. Save immutable snapshot
        # -------------------------------------------------

        identity = (
            PracticeAttemptQuestionIdentity(
                attempt_id=attempt_id,

                question_group_id=(
                    question_group_id
                ),

                logical_question_key=(
                    logical_question_key
                ),

                group_key=group_key,

                question_type=(
                    question_type
                ),

                source="evaluation"
            )
        )


        db.add(
            identity
        )

        db.commit()

        db.refresh(
            identity
        )


        return identity


    def get_identity_for_attempt(
        self,
        db: Session,
        attempt_id: int
    ) -> PracticeAttemptQuestionIdentity | None:

        statement = (
            select(
                PracticeAttemptQuestionIdentity
            )
            .where(
                PracticeAttemptQuestionIdentity.attempt_id
                == attempt_id
            )
        )


        return (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )