import unittest

from fastapi.testclient import TestClient

from app.api.practice import get_practice_service
from app.db.database import get_db
from app.main import app


class FakePracticeService:

    def __init__(self, question):
        self.question = question
        self.calls = []

    def get_question(
        self,
        db,
        curriculum_id: int,
        lesson_number: str,
        topic: str | None = None
    ):
        self.calls.append({
            "db": db,
            "curriculum_id": curriculum_id,
            "lesson_number": lesson_number,
            "topic": topic
        })
        return self.question


class PracticeQuestionApiTests(unittest.TestCase):

    def setUp(self):
        self.db = object()
        app.dependency_overrides[get_db] = lambda: self.db

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_returns_unified_multi_select_question(self):
        service = FakePracticeService({
            "logical_question_key": "group:1",
            "question_group_id": 1,
            "selected_chunk_id": 150,
            "question_type": "multi_select",
            "lesson_number": "3",
            "question_number": "1",
            "content": "Select every coprime pair.",
            "options": [
                {
                    "chunk_id": 150,
                    "sequence": 1,
                    "content": "10 and 25"
                },
                {
                    "chunk_id": 151,
                    "sequence": 2,
                    "content": "17 and 31"
                }
            ],
            "sub_questions": [],
            "similarity": 0.92
        })
        app.dependency_overrides[get_practice_service] = (
            lambda: service
        )

        with TestClient(app) as client:
            response = client.get(
                "/api/practice/question",
                params={
                    "curriculum_id": 1,
                    "lesson_number": "3",
                    "topic": "greatest common factor"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "logical_question_key": "group:1",
            "question_type": "multi_select",
            "lesson_number": "3",
            "question_number": "1",
            "prompt": "Select every coprime pair.",
            "options": [
                {"id": 1, "text": "10 and 25"},
                {"id": 2, "text": "17 and 31"}
            ]
        })
        self.assertNotIn("selected_chunk_id", response.json())
        self.assertNotIn("question_group_id", response.json())
        self.assertNotIn("similarity", response.json())
        self.assertEqual(
            service.calls[0]["topic"],
            "greatest common factor"
        )

    def test_returns_unified_standard_question(self):
        service = FakePracticeService({
            "logical_question_key": "chunk:159",
            "question_group_id": None,
            "selected_chunk_id": 159,
            "question_type": "standard",
            "lesson_number": "3",
            "lesson_title": "Factors",
            "question_number": "2",
            "content": "Find the greatest common factor.",
            "options": [],
            "sub_questions": [],
            "similarity": 0.88
        })
        app.dependency_overrides[get_practice_service] = (
            lambda: service
        )

        with TestClient(app) as client:
            response = client.get(
                "/api/practice/question",
                params={
                    "curriculum_id": 1,
                    "lesson_number": "3"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["options"], [])
        self.assertEqual(
            response.json()["logical_question_key"],
            "chunk:159"
        )

    def test_returns_not_found_when_no_question_is_available(self):
        service = FakePracticeService(None)
        app.dependency_overrides[get_practice_service] = (
            lambda: service
        )

        with TestClient(app) as client:
            response = client.get(
                "/api/practice/question",
                params={
                    "curriculum_id": 1,
                    "lesson_number": "3"
                }
            )

        self.assertEqual(response.status_code, 404)

    def test_rejects_blank_lesson_number(self):
        service = FakePracticeService(None)
        app.dependency_overrides[get_practice_service] = (
            lambda: service
        )

        with TestClient(app) as client:
            response = client.get(
                "/api/practice/question",
                params={
                    "curriculum_id": 1,
                    "lesson_number": "   "
                }
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(service.calls, [])


if __name__ == "__main__":
    unittest.main()
