import json

from sqlalchemy.orm import Session

from app.repositories.question_group_attempt_repository import (
    QuestionGroupAttemptRepository
)

from app.repositories.question_group_repository import (
    QuestionGroupRepository
)


class QuestionGroupEvaluationService:

    def __init__(
        self,
        repository: QuestionGroupRepository,
        attempt_repository: QuestionGroupAttemptRepository
    ):

        self.repository = repository

        self.attempt_repository = (
            attempt_repository
        )


    def evaluate_multi_select(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        question_group_id: int,
        selected_sequences: list[int],
        idempotency_key: str | None = None
    ) -> dict:

        if (
            not isinstance(selected_sequences, list)
            or any(
                not isinstance(value, int)
                or isinstance(value, bool)
                for value in selected_sequences
            )
        ):

            return {
                "status": "invalid_answer",
                "feedback": (
                    "A multi-select answer must be a list "
                    "of option numbers."
                )
            }

        group = (
            self.repository
            .get_group_for_curriculum(
                db=db,
                question_group_id=(
                    question_group_id
                ),
                curriculum_id=curriculum_id
            )
        )


        if not group:

            return {
                "status":
                    "question_not_found",

                "feedback":
                    "Question group was not found."
            }


        if (
            group.question_type
            != "multi_select"
        ):

            return {
                "status":
                    "unsupported_question_type",

                "feedback":
                    (
                        "This evaluator currently "
                        "supports multi-select "
                        "questions only."
                    )
            }


        # -------------------------------------------------
        # Options
        # -------------------------------------------------

        rows = (
            self.repository
            .get_group_chunks(
                db=db,
                question_group_id=(
                    question_group_id
                )
            )
        )


        valid_option_sequences = {
            mapping.sequence

            for (
                mapping,
                chunk
            ) in rows

            if mapping.role
            == "option"
        }


        selected = set(
            selected_sequences
        )


        invalid_selections = (
            selected
            -
            valid_option_sequences
        )


        if invalid_selections:

            return {
                "status":
                    "invalid_answer",

                "feedback":
                    (
                        "The answer contains "
                        "invalid option numbers."
                    ),

                "invalid_selections":
                    sorted(
                        invalid_selections
                    )
            }


        # -------------------------------------------------
        # Verified solution
        # -------------------------------------------------

        solution = (
            self.repository
            .get_verified_solution(
                db=db,
                question_group_id=(
                    question_group_id
                )
            )
        )


        if not solution:

            return {
                "status":
                    "cannot_evaluate",

                "feedback":
                    (
                        "No verified answer is "
                        "available for this question."
                    )
            }


        try:

            payload = json.loads(
                solution.answer_payload
            )


        except (json.JSONDecodeError, TypeError):

            return {
                "status":
                    "cannot_evaluate",

                "feedback":
                    (
                        "The verified answer "
                        "could not be processed."
                    )
            }


        raw_correct = payload.get(
            "correct_option_sequences"
        )


        if (
            not isinstance(raw_correct, list)
            or not raw_correct
            or any(
                not isinstance(value, int)
                or isinstance(value, bool)
                for value in raw_correct
            )
        ):

            return {
                "status": "cannot_evaluate",
                "feedback": (
                    "The verified answer has an invalid "
                    "multi-select format."
                )
            }


        correct = set(raw_correct)


        if not correct.issubset(valid_option_sequences):

            return {
                "status": "cannot_evaluate",
                "feedback": (
                    "The verified answer references options "
                    "that are not part of this question."
                )
            }


        correctly_selected = (
            selected
            &
            correct
        )


        missed = (
            correct
            -
            selected
        )


        incorrectly_selected = (
            selected
            -
            correct
        )


        # -------------------------------------------------
        # Overall deterministic result
        # -------------------------------------------------

        if selected == correct:

            status = "correct"

            feedback = (
                "Correct. You selected all verified "
                "correct options."
            )


        elif correctly_selected:

            status = "partial"


            feedback_parts = [
                (
                    "You selected some correct "
                    "options, but the answer is "
                    "not complete."
                )
            ]


            if missed:

                feedback_parts.append(
                    (
                        "Missed options: "
                        + ", ".join(
                            str(value)

                            for value
                            in sorted(
                                missed
                            )
                        )
                        + "."
                    )
                )


            if incorrectly_selected:

                feedback_parts.append(
                    (
                        "Incorrectly selected "
                        "options: "
                        + ", ".join(
                            str(value)

                            for value
                            in sorted(
                                incorrectly_selected
                            )
                        )
                        + "."
                    )
                )


            feedback = " ".join(
                feedback_parts
            )


        else:

            status = "incorrect"

            feedback = (
                "None of the selected options "
                "matches the verified correct "
                "set for this question."
            )


        # -------------------------------------------------
        # Concept evidence
        # -------------------------------------------------

        concepts = (
            self.repository
            .get_group_concepts(
                db=db,
                question_group_id=(
                    question_group_id
                )
            )
        )


        concept_diagnoses = {}


        for concept in concepts:

            if status == "correct":

                concept_status = (
                    "demonstrated"
                )

                concept_reason = (
                    "The student selected the "
                    "complete verified set of "
                    "correct options."
                )


            else:

                concept_status = (
                    "needs_review"
                )

                concept_reason = (
                    "The student did not select "
                    "the complete verified set "
                    "for this concept."
                )


            concept_diagnoses[
                concept.code
            ] = {
                "concept_id":
                    concept.id,

                "concept_name":
                    concept.name,

                "status":
                    concept_status,

                "reason":
                    concept_reason
            }


        # -------------------------------------------------
        # Save attempt + concept evidence
        # -------------------------------------------------

        attempt = (
            self.attempt_repository
            .save_attempt(
                db=db,

                student_id=student_id,

                curriculum_id=(
                    curriculum_id
                ),

                group=group,

                selected_sequences=(
                    sorted(
                        selected
                    )
                ),

                correct_sequences=(
                    sorted(
                        correct
                    )
                ),

                evaluation_status=(
                    status
                ),

                feedback=feedback,

                solution_source=(
                    solution.solution_source
                ),

                concept_diagnoses=(
                    concept_diagnoses
                ),

                idempotency_key=idempotency_key
            )
        )


        return {
            "attempt_id":
                attempt.id,

            "logical_question_key":
                f"group:{group.id}",

            "question_group_id":
                group.id,

            "question_type":
                group.question_type,

            "status":
                status,

            "selected_sequences":
                sorted(
                    selected
                ),

            "correct_sequences":
                sorted(
                    correct
                ),

            "correctly_selected":
                sorted(
                    correctly_selected
                ),

            "missed_sequences":
                sorted(
                    missed
                ),

            "incorrectly_selected":
                sorted(
                    incorrectly_selected
                ),

            "feedback":
                feedback,

            "solution_source":
                solution.solution_source,

            "concept_diagnoses":
                concept_diagnoses
        }
