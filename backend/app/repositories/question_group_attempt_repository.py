import json

from datetime import datetime

from sqlalchemy.orm import Session

from app.models.curriculum import (
    PracticeAttempt,
    PracticeAttemptConcept
)

from app.models.practice_attempt_question import (
    PracticeAttemptQuestionIdentity
)

from app.models.question_group import (
    CurriculumQuestionGroup
)


class QuestionGroupAttemptRepository:

    def save_attempt(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        group: CurriculumQuestionGroup,
        selected_sequences: list[int],
        correct_sequences: list[int],
        evaluation_status: str,
        feedback: str,
        solution_source: str,
        concept_diagnoses: dict[str, dict],
        idempotency_key: str | None = None
    ) -> PracticeAttempt:

        # -------------------------------------------------
        # 1. Question snapshot
        # -------------------------------------------------

        question_content = (
            group.instructions
            or
            "Logical curriculum question"
        )


        student_answer = json.dumps(
            {
                "selected_option_sequences":
                    selected_sequences
            }
        )


        reference_answer = json.dumps(
            {
                "correct_option_sequences":
                    correct_sequences
            }
        )


        # -------------------------------------------------
        # 2. Practice attempt
        # -------------------------------------------------

        attempt = PracticeAttempt(
            student_id=student_id,

            curriculum_id=curriculum_id,

            idempotency_key=idempotency_key,

            chunk_id=None,

            question_number=(
                group.question_number
            ),

            question_content=(
                question_content
            ),

            lesson_number=(
                group.lesson_number
            ),

            lesson_title=None,

            student_answer=(
                student_answer
            ),

            reference_answer=(
                reference_answer
            ),

            evaluation_status=(
                evaluation_status
            ),

            feedback=feedback,

            solution_source=(
                solution_source
            ),

            ai_provider=None,

            ai_model=None
        )


        db.add(
            attempt
        )

        db.flush()


        # -------------------------------------------------
        # 3. Logical-question identity
        # -------------------------------------------------

        identity = (
            PracticeAttemptQuestionIdentity(
                attempt_id=attempt.id,

                question_group_id=(
                    group.id
                ),

                logical_question_key=(
                    f"group:{group.id}"
                ),

                group_key=(
                    group.group_key
                ),

                question_type=(
                    group.question_type
                ),

                source="group_evaluation"
            )
        )


        db.add(
            identity
        )


        # -------------------------------------------------
        # 4. Concept evidence snapshots
        # -------------------------------------------------

        for (
            concept_code,
            diagnosis
        ) in concept_diagnoses.items():

            attempt_concept = (
                PracticeAttemptConcept(
                    attempt_id=attempt.id,

                    concept_id=(
                        diagnosis["concept_id"]
                    ),

                    concept_code=(
                        concept_code
                    ),

                    concept_name=(
                        diagnosis["concept_name"]
                    ),

                    source=(
                        "question_group_mapping"
                    ),

                    diagnosis_status=(
                        diagnosis["status"]
                    ),

                    diagnosis_reason=(
                        diagnosis["reason"]
                    ),

                    diagnosis_source=(
                        "deterministic_evaluation"
                    ),

                    diagnosed_at=(
                        datetime.utcnow()
                    )
                )
            )


            db.add(
                attempt_concept
            )


        db.commit()

        db.refresh(
            attempt
        )


        return attempt
