from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.repositories.practice_session_repository import (
    PracticeSessionRepository
)
from app.services.curriculum_practice_service import (
    CurriculumPracticeService
)


class PracticeSessionService:

    def __init__(
        self,
        repository: PracticeSessionRepository,
        practice_service: CurriculumPracticeService
    ):
        self.repository = repository
        self.practice_service = practice_service


    def _session_result(
        self,
        db: Session,
        session
    ) -> dict:
        return {
            "session_id": session.id,
            "student_id": session.student_id,
            "curriculum_id": session.curriculum_id,
            "lesson_number": session.lesson_number,
            "status": session.status,
            "target_question_count": (
                session.target_question_count
            ),
            "questions_served": self.repository.count_questions(
                db=db,
                session_id=session.id
            ),
            "started_at": session.started_at,
            "completed_at": session.completed_at
        }


    def start_session(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        lesson_number: str,
        target_question_count: int
    ) -> dict:
        if not self.repository.student_exists(db, student_id):
            return {
                "status": "student_not_found",
                "feedback": "Student was not found."
            }

        if not self.repository.curriculum_exists(db, curriculum_id):
            return {
                "status": "curriculum_not_found",
                "feedback": "Curriculum was not found."
            }

        session = self.repository.create_session(
            db=db,
            student_id=student_id,
            curriculum_id=curriculum_id,
            lesson_number=lesson_number,
            target_question_count=target_question_count
        )
        return self._session_result(db, session)


    def get_next_question(
        self,
        db: Session,
        session_id: int,
        topic: str | None = None
    ) -> dict:
        session = self.repository.get_session(
            db=db,
            session_id=session_id,
            for_update=True
        )

        if session is None:
            return {
                "status": "session_not_found",
                "feedback": "Practice session was not found."
            }

        pending = self.repository.get_pending_question(
            db=db,
            session_id=session.id
        )

        if pending is not None:
            return {
                **self._session_result(db, session),
                "position": pending.sequence,
                "question": self.repository.decode_question(
                    pending
                ),
                "is_replay": True
            }

        if session.status != "active":
            return {
                **self._session_result(db, session),
                "position": None,
                "question": None,
                "is_replay": False
            }

        questions_served = self.repository.count_questions(
            db=db,
            session_id=session.id
        )

        if questions_served >= session.target_question_count:
            self.repository.complete_session(
                db=db,
                session=session,
                status="completed"
            )
            return {
                **self._session_result(db, session),
                "position": None,
                "question": None,
                "is_replay": False
            }

        used_keys = self.repository.get_used_question_keys(
            db=db,
            session_id=session.id
        )
        question = self.practice_service.get_question(
            db=db,
            curriculum_id=session.curriculum_id,
            lesson_number=session.lesson_number,
            topic=topic,
            excluded_question_keys=used_keys
        )

        if question is None:
            self.repository.complete_session(
                db=db,
                session=session,
                status="exhausted"
            )
            return {
                **self._session_result(db, session),
                "position": None,
                "question": None,
                "is_replay": False
            }

        position = questions_served + 1

        try:
            stored_question = self.repository.add_question(
                db=db,
                session_id=session.id,
                logical_question_key=(
                    question["logical_question_key"]
                ),
                sequence=position,
                question_payload=question
            )
        except IntegrityError:
            db.rollback()
            stored_question = self.repository.get_pending_question(
                db=db,
                session_id=session.id
            )
            if stored_question is None:
                raise
            question = self.repository.decode_question(
                stored_question
            )
            position = stored_question.sequence
            is_replay = True
        else:
            is_replay = False

        return {
            **self._session_result(db, session),
            "position": position,
            "question": question,
            "is_replay": is_replay
        }


    def validate_answer_submission(
        self,
        db: Session,
        session_id: int,
        student_id: int,
        curriculum_id: int,
        logical_question_key: str,
        idempotency_key: str | None
    ) -> dict | None:
        session = self.repository.get_session(db, session_id)

        if session is None:
            return {
                "status": "session_not_found",
                "feedback": "Practice session was not found."
            }

        if (
            session.student_id != student_id
            or session.curriculum_id != curriculum_id
        ):
            return {
                "status": "session_scope_mismatch",
                "feedback": (
                    "The practice session does not belong to "
                    "this student and curriculum."
                )
            }

        question = self.repository.get_question(
            db=db,
            session_id=session_id,
            logical_question_key=logical_question_key
        )

        if question is None:
            return {
                "status": "session_question_not_found",
                "feedback": (
                    "This logical question was not served in "
                    "the practice session."
                )
            }

        if question.attempt_id is not None:
            attempt = self.repository.get_attempt(
                db=db,
                attempt_id=question.attempt_id
            )
            if (
                attempt is None
                or idempotency_key is None
                or attempt.idempotency_key != idempotency_key
            ):
                return {
                    "status": "session_question_already_answered",
                    "feedback": (
                        "This practice-session question has "
                        "already been answered."
                    )
                }

        return None


    def attach_attempt(
        self,
        db: Session,
        session_id: int,
        student_id: int,
        curriculum_id: int,
        logical_question_key: str,
        attempt_id: int
    ) -> dict | None:
        question = self.repository.get_question(
            db=db,
            session_id=session_id,
            logical_question_key=logical_question_key
        )
        attempt = self.repository.get_attempt(db, attempt_id)

        if question is None or attempt is None:
            return {
                "status": "session_association_failed",
                "feedback": (
                    "The attempt could not be associated with "
                    "the practice session."
                )
            }

        attempt_key = self.repository.get_attempt_question_key(
            db=db,
            attempt_id=attempt_id
        )

        if (
            attempt.student_id != student_id
            or attempt.curriculum_id != curriculum_id
            or attempt_key != logical_question_key
        ):
            return {
                "status": "session_association_failed",
                "feedback": (
                    "The attempt identity does not match the "
                    "practice-session question."
                )
            }

        if question.attempt_id not in {None, attempt_id}:
            return {
                "status": "session_question_already_answered",
                "feedback": (
                    "This practice-session question has already "
                    "been answered."
                )
            }

        if question.attempt_id is None:
            self.repository.attach_attempt(
                db=db,
                question=question,
                attempt_id=attempt_id
            )

        return None
