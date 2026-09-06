import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.practice import get_practice_session_service
from app.db.database import get_db
from app.main import app
from app.services.curriculum_practice_service import (
    CurriculumPracticeService
)
from app.services.practice_session_service import (
    PracticeSessionService
)


def session_record(**overrides):
    values = {
        "id": 7,
        "student_id": 1,
        "curriculum_id": 1,
        "lesson_number": "3",
        "status": "active",
        "target_question_count": 5,
        "started_at": datetime(2026, 9, 6, 12, 0, 0),
        "completed_at": None
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def raw_question(key="chunk:158"):
    return {
        "logical_question_key": key,
        "question_group_id": None,
        "selected_chunk_id": 158,
        "question_type": "standard",
        "lesson_number": "3",
        "lesson_title": "Factors",
        "question_number": "2",
        "instructions": None,
        "content": "Find the GCF.",
        "options": [],
        "sub_questions": [],
        "similarity": 0.9
    }


class PracticeSessionServiceTests(unittest.TestCase):

    def setUp(self):
        self.db = Mock()
        self.repository = Mock()
        self.practice_service = Mock()
        self.service = PracticeSessionService(
            repository=self.repository,
            practice_service=self.practice_service
        )

    def test_starts_session_for_existing_scope(self):
        session = session_record()
        self.repository.student_exists.return_value = True
        self.repository.curriculum_exists.return_value = True
        self.repository.create_session.return_value = session
        self.repository.count_questions.return_value = 0

        result = self.service.start_session(
            db=self.db,
            student_id=1,
            curriculum_id=1,
            lesson_number="3",
            target_question_count=5
        )

        self.assertEqual(result["session_id"], 7)
        self.assertEqual(result["status"], "active")
        self.repository.create_session.assert_called_once()

    def test_serves_unused_logical_question(self):
        session = session_record()
        question = raw_question()
        stored = SimpleNamespace(sequence=1)
        self.repository.get_session.return_value = session
        self.repository.get_pending_question.return_value = None
        self.repository.count_questions.side_effect = [0, 1]
        self.repository.get_used_question_keys.return_value = {
            "group:1"
        }
        self.practice_service.get_question.return_value = question
        self.repository.add_question.return_value = stored

        result = self.service.get_next_question(
            db=self.db,
            session_id=7,
            topic=None
        )

        self.assertEqual(result["question"], question)
        self.assertEqual(result["position"], 1)
        self.assertFalse(result["is_replay"])
        self.assertEqual(
            self.practice_service.get_question.call_args.kwargs[
                "excluded_question_keys"
            ],
            {"group:1"}
        )

    def test_replays_pending_question_without_retrieval(self):
        session = session_record()
        pending = SimpleNamespace(sequence=1)
        question = raw_question()
        self.repository.get_session.return_value = session
        self.repository.get_pending_question.return_value = pending
        self.repository.decode_question.return_value = question
        self.repository.count_questions.return_value = 1

        result = self.service.get_next_question(
            db=self.db,
            session_id=7
        )

        self.assertEqual(result["question"], question)
        self.assertTrue(result["is_replay"])
        self.practice_service.get_question.assert_not_called()

    def test_rejects_attempt_for_unserved_question(self):
        self.repository.get_session.return_value = session_record()
        self.repository.get_question.return_value = None

        result = self.service.validate_answer_submission(
            db=self.db,
            session_id=7,
            student_id=1,
            curriculum_id=1,
            logical_question_key="chunk:999",
            idempotency_key=None
        )

        self.assertEqual(
            result["status"],
            "session_question_not_found"
        )


class CurriculumPracticeExclusionTests(unittest.TestCase):

    def test_excludes_by_logical_question_key(self):
        search_service = Mock()
        group_repository = Mock()
        group = SimpleNamespace(id=1)
        search_service.search.return_value = [
            {
                "chunk_id": 150,
                "lesson_number": "3",
                "lesson_title": "Factors",
                "question_number": "1",
                "similarity": 0.95,
                "content": "Option one"
            },
            {
                "chunk_id": 151,
                "lesson_number": "3",
                "lesson_title": "Factors",
                "question_number": "1",
                "similarity": 0.94,
                "content": "Option two"
            },
            {
                "chunk_id": 158,
                "lesson_number": "3",
                "lesson_title": "Factors",
                "question_number": "2",
                "similarity": 0.90,
                "content": "Find the GCF."
            }
        ]
        group_repository.get_group_for_chunk.side_effect = [
            group,
            group,
            None
        ]
        service = CurriculumPracticeService(
            search_service=search_service,
            question_group_repository=group_repository
        )

        result = service.get_question(
            db=Mock(),
            curriculum_id=1,
            lesson_number="3",
            excluded_question_keys={"group:1"}
        )

        self.assertEqual(
            result["logical_question_key"],
            "chunk:158"
        )
        self.assertGreater(
            search_service.search.call_args.kwargs["limit"],
            5
        )


class FakePracticeSessionApiService:

    def __init__(self):
        self.calls = []

    def start_session(self, **kwargs):
        self.calls.append(("start", kwargs))
        return {
            "session_id": 7,
            "student_id": 1,
            "curriculum_id": 1,
            "lesson_number": "3",
            "status": "active",
            "target_question_count": 5,
            "questions_served": 0,
            "started_at": "2026-09-06T12:00:00",
            "completed_at": None
        }

    def get_next_question(self, **kwargs):
        self.calls.append(("next", kwargs))
        return {
            "session_id": 7,
            "student_id": 1,
            "curriculum_id": 1,
            "lesson_number": "3",
            "status": "active",
            "target_question_count": 5,
            "questions_served": 1,
            "started_at": "2026-09-06T12:00:00",
            "completed_at": None,
            "position": 1,
            "question": raw_question(),
            "is_replay": False
        }


class PracticeSessionApiTests(unittest.TestCase):

    def setUp(self):
        self.db = object()
        self.service = FakePracticeSessionApiService()
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[
            get_practice_session_service
        ] = lambda: self.service

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_starts_session(self):
        with TestClient(app) as client:
            response = client.post(
                "/api/practice/sessions",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "lesson_number": "3",
                    "target_question_count": 5
                }
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["session_id"], 7)
        self.assertEqual(response.json()["questions_served"], 0)

    def test_gets_next_unified_question(self):
        with TestClient(app) as client:
            response = client.get(
                "/api/practice/sessions/7/next-question"
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["question"],
            {
                "logical_question_key": "chunk:158",
                "question_type": "standard",
                "lesson_number": "3",
                "question_number": "2",
                "prompt": "Find the GCF.",
                "options": []
            }
        )


if __name__ == "__main__":
    unittest.main()
