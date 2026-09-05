import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import (
    PracticeAttempt,
    PracticeAttemptConcept
)
from app.models.practice_attempt_question import (
    PracticeAttemptQuestionIdentity
)


class PracticeAttemptRepository:

    def get_by_idempotency_key(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        idempotency_key: str
    ) -> PracticeAttempt | None:

        statement = (
            select(PracticeAttempt)
            .where(
                PracticeAttempt.student_id == student_id,
                PracticeAttempt.curriculum_id == curriculum_id,
                PracticeAttempt.idempotency_key == idempotency_key
            )
        )

        return db.execute(statement).scalar_one_or_none()


    def build_replay_result(
        self,
        db: Session,
        attempt: PracticeAttempt
    ) -> dict:

        identity_statement = (
            select(PracticeAttemptQuestionIdentity)
            .where(
                PracticeAttemptQuestionIdentity.attempt_id
                == attempt.id
            )
        )

        identity = (
            db.execute(identity_statement)
            .scalar_one_or_none()
        )

        concept_statement = (
            select(PracticeAttemptConcept)
            .where(
                PracticeAttemptConcept.attempt_id
                == attempt.id
            )
            .order_by(PracticeAttemptConcept.id)
        )

        concepts = list(
            db.execute(concept_statement)
            .scalars()
            .all()
        )

        concept_diagnoses = {
            concept.concept_code: {
                "concept_id": concept.concept_id,
                "concept_name": concept.concept_name,
                "status": concept.diagnosis_status,
                "reason": concept.diagnosis_reason
            }
            for concept in concepts
        }

        result = {
            "attempt_id": attempt.id,
            "logical_question_key": (
                identity.logical_question_key
                if identity
                else None
            ),
            "question_group_id": (
                identity.question_group_id
                if identity
                else None
            ),
            "question_type": (
                identity.question_type
                if identity
                else None
            ),
            "status": attempt.evaluation_status,
            "feedback": attempt.feedback,
            "solution_source": attempt.solution_source,
            "concept_diagnoses": concept_diagnoses,
            "idempotent_replay": True
        }

        if identity and identity.question_group_id is not None:
            try:
                student_answer = json.loads(attempt.student_answer)
                reference_answer = json.loads(
                    attempt.reference_answer or "{}"
                )
            except (json.JSONDecodeError, TypeError):
                student_answer = {}
                reference_answer = {}

            selected = sorted(
                student_answer.get(
                    "selected_option_sequences",
                    []
                )
            )
            correct = sorted(
                reference_answer.get(
                    "correct_option_sequences",
                    []
                )
            )

            result.update({
                "selected_sequences": selected,
                "correct_sequences": correct,
                "correctly_selected": sorted(
                    set(selected) & set(correct)
                ),
                "missed_sequences": sorted(
                    set(correct) - set(selected)
                ),
                "incorrectly_selected": sorted(
                    set(selected) - set(correct)
                )
            })

        return result
