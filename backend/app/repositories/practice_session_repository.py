import json
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.curriculum import (
    Curriculum,
    PracticeAttempt,
    Student
)
from app.models.practice_attempt_question import (
    PracticeAttemptQuestionIdentity
)
from app.models.practice_session import (
    PracticeSession,
    PracticeSessionQuestion
)


class PracticeSessionRepository:

    def student_exists(
        self,
        db: Session,
        student_id: int
    ) -> bool:
        return db.get(Student, student_id) is not None


    def curriculum_exists(
        self,
        db: Session,
        curriculum_id: int
    ) -> bool:
        return db.get(Curriculum, curriculum_id) is not None


    def create_session(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        lesson_number: str,
        target_question_count: int
    ) -> PracticeSession:
        session = PracticeSession(
            student_id=student_id,
            curriculum_id=curriculum_id,
            lesson_number=lesson_number,
            status="active",
            target_question_count=target_question_count
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session


    def get_session(
        self,
        db: Session,
        session_id: int,
        for_update: bool = False
    ) -> PracticeSession | None:
        statement = select(PracticeSession).where(
            PracticeSession.id == session_id
        )

        if for_update:
            statement = statement.with_for_update()

        return db.execute(statement).scalar_one_or_none()


    def get_pending_question(
        self,
        db: Session,
        session_id: int
    ) -> PracticeSessionQuestion | None:
        statement = (
            select(PracticeSessionQuestion)
            .where(
                PracticeSessionQuestion.session_id == session_id,
                PracticeSessionQuestion.attempt_id.is_(None)
            )
            .order_by(PracticeSessionQuestion.sequence)
            .limit(1)
        )
        return db.execute(statement).scalar_one_or_none()


    def get_used_question_keys(
        self,
        db: Session,
        session_id: int
    ) -> set[str]:
        statement = select(
            PracticeSessionQuestion.logical_question_key
        ).where(
            PracticeSessionQuestion.session_id == session_id
        )
        return set(db.execute(statement).scalars().all())


    def count_questions(
        self,
        db: Session,
        session_id: int
    ) -> int:
        statement = select(
            func.count(PracticeSessionQuestion.id)
        ).where(
            PracticeSessionQuestion.session_id == session_id
        )
        return db.execute(statement).scalar_one()


    def add_question(
        self,
        db: Session,
        session_id: int,
        logical_question_key: str,
        sequence: int,
        question_payload: dict
    ) -> PracticeSessionQuestion:
        question = PracticeSessionQuestion(
            session_id=session_id,
            logical_question_key=logical_question_key,
            sequence=sequence,
            question_payload=json.dumps(question_payload)
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        return question


    def decode_question(
        self,
        question: PracticeSessionQuestion
    ) -> dict:
        return json.loads(question.question_payload)


    def complete_session(
        self,
        db: Session,
        session: PracticeSession,
        status: str
    ) -> None:
        session.status = status
        session.completed_at = datetime.utcnow()
        db.commit()


    def get_question(
        self,
        db: Session,
        session_id: int,
        logical_question_key: str
    ) -> PracticeSessionQuestion | None:
        statement = select(PracticeSessionQuestion).where(
            PracticeSessionQuestion.session_id == session_id,
            PracticeSessionQuestion.logical_question_key
            == logical_question_key
        )
        return db.execute(statement).scalar_one_or_none()


    def get_attempt(
        self,
        db: Session,
        attempt_id: int
    ) -> PracticeAttempt | None:
        return db.get(PracticeAttempt, attempt_id)


    def get_attempt_question_key(
        self,
        db: Session,
        attempt_id: int
    ) -> str | None:
        statement = select(
            PracticeAttemptQuestionIdentity.logical_question_key
        ).where(
            PracticeAttemptQuestionIdentity.attempt_id == attempt_id
        )
        return db.execute(statement).scalar_one_or_none()


    def attach_attempt(
        self,
        db: Session,
        question: PracticeSessionQuestion,
        attempt_id: int
    ) -> None:
        question.attempt_id = attempt_id
        question.answered_at = datetime.utcnow()
        db.commit()
