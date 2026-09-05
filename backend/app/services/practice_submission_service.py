from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.practice_attempt_repository import (
    PracticeAttemptRepository
)
from app.services.practice_evaluation_service import (
    PracticeEvaluationService
)
from app.services.question_group_evaluation_service import (
    QuestionGroupEvaluationService
)


class PracticeSubmissionService:

    def __init__(
        self,
        attempt_repository: PracticeAttemptRepository,
        standard_evaluation_service: PracticeEvaluationService,
        group_evaluation_service: QuestionGroupEvaluationService
    ):

        self.attempt_repository = attempt_repository
        self.standard_evaluation_service = standard_evaluation_service
        self.group_evaluation_service = group_evaluation_service


    def _existing_result(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        idempotency_key: str | None,
        logical_question_key: str
    ) -> dict | None:

        if idempotency_key is None:
            return None

        attempt = self.attempt_repository.get_by_idempotency_key(
            db=db,
            student_id=student_id,
            curriculum_id=curriculum_id,
            idempotency_key=idempotency_key
        )

        if attempt is None:
            return None

        result = self.attempt_repository.build_replay_result(
            db=db,
            attempt=attempt
        )

        if result["logical_question_key"] != logical_question_key:
            return {
                "status": "idempotency_conflict",
                "feedback": (
                    "This idempotency key was already used "
                    "for a different practice question."
                )
            }

        return result


    def submit(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        logical_question_key: str,
        answer,
        idempotency_key: str | None = None
    ) -> dict:

        if not isinstance(logical_question_key, str):
            return {
                "status": "invalid_question_key",
                "feedback": "The logical question key is invalid."
            }

        logical_question_key = logical_question_key.strip()

        if idempotency_key is not None:
            idempotency_key = idempotency_key.strip()

            if not idempotency_key or len(idempotency_key) > 200:
                return {
                    "status": "invalid_submission",
                    "feedback": (
                        "The idempotency key must contain between "
                        "1 and 200 characters."
                    )
                }

        existing = self._existing_result(
            db=db,
            student_id=student_id,
            curriculum_id=curriculum_id,
            idempotency_key=idempotency_key,
            logical_question_key=logical_question_key
        )

        if existing is not None:
            return existing

        try:
            prefix, raw_id = logical_question_key.split(":", 1)
            question_id = int(raw_id)
        except (ValueError, AttributeError):
            return {
                "status": "invalid_question_key",
                "feedback": "The logical question key is invalid."
            }

        if question_id <= 0 or prefix not in {"chunk", "group"}:
            return {
                "status": "invalid_question_key",
                "feedback": "The logical question key is invalid."
            }

        try:
            if prefix == "group":
                if isinstance(answer, dict):
                    selected_sequences = answer.get(
                        "selected_option_sequences"
                    )
                else:
                    selected_sequences = answer

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

                result = self.group_evaluation_service.evaluate_multi_select(
                    db=db,
                    student_id=student_id,
                    curriculum_id=curriculum_id,
                    question_group_id=question_id,
                    selected_sequences=selected_sequences,
                    idempotency_key=idempotency_key
                )
            else:
                if not isinstance(answer, str) or not answer.strip():
                    return {
                        "status": "invalid_answer",
                        "feedback": (
                            "A standard question answer must be "
                            "non-empty text."
                        )
                    }

                result = self.standard_evaluation_service.evaluate(
                    db=db,
                    student_id=student_id,
                    curriculum_id=curriculum_id,
                    chunk_id=question_id,
                    student_answer=answer,
                    idempotency_key=idempotency_key
                )

        except IntegrityError:
            db.rollback()

            existing = self._existing_result(
                db=db,
                student_id=student_id,
                curriculum_id=curriculum_id,
                idempotency_key=idempotency_key,
                logical_question_key=logical_question_key
            )

            if existing is None:
                raise

            return existing

        result["idempotent_replay"] = False
        return result
