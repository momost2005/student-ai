import unittest

from fastapi.testclient import TestClient

from app.api.practice import (
    get_practice_session_service,
    get_practice_submission_service
)
from app.db.database import get_db
from app.main import app


class FakePracticeSubmissionService:

    def __init__(self, result):
        self.result = result
        self.calls = []

    def submit(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakePracticeSessionService:

    def __init__(self):
        self.validations = []
        self.attachments = []

    def validate_answer_submission(self, **kwargs):
        self.validations.append(kwargs)
        return None

    def attach_attempt(self, **kwargs):
        self.attachments.append(kwargs)
        return None


class PracticeAnswerApiTests(unittest.TestCase):

    def setUp(self):
        self.db = object()
        self.session_service = FakePracticeSessionService()
        app.dependency_overrides[get_db] = lambda: self.db
        app.dependency_overrides[
            get_practice_session_service
        ] = lambda: self.session_service

    def tearDown(self):
        app.dependency_overrides.clear()

    def _set_service(self, result):
        service = FakePracticeSubmissionService(result)
        app.dependency_overrides[
            get_practice_submission_service
        ] = lambda: service
        return service

    def test_submits_standard_answer(self):
        service = self._set_service({
            "attempt_id": 21,
            "logical_question_key": "chunk:159",
            "status": "correct",
            "feedback": "Correct.",
            "concept_diagnoses": {
                "greatest_common_factor": {
                    "status": "demonstrated",
                    "reason": "The method is correct."
                }
            },
            "idempotent_replay": False,
            "provider": "mock",
            "model": "mock-model"
        })

        with TestClient(app) as client:
            response = client.post(
                "/api/practice/answer",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "logical_question_key": "chunk:159",
                    "answer": "The GCF is 5.",
                    "idempotency_key": "mobile-request-1"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "attempt_id": 21,
            "logical_question_key": "chunk:159",
            "question_type": "standard",
            "status": "correct",
            "feedback": "Correct.",
            "concepts": [
                {
                    "code": "greatest_common_factor",
                    "status": "demonstrated",
                    "reason": "The method is correct."
                }
            ],
            "idempotent_replay": False
        })
        self.assertNotIn("provider", response.json())
        self.assertNotIn("model", response.json())
        self.assertEqual(
            service.calls[0]["answer"],
            "The GCF is 5."
        )

    def test_submits_multi_select_answer(self):
        service = self._set_service({
            "attempt_id": 22,
            "logical_question_key": "group:1",
            "question_type": "multi_select",
            "status": "partial",
            "feedback": "Missed options: 6, 8.",
            "concept_diagnoses": {
                "greatest_common_factor": {
                    "concept_id": 1,
                    "concept_name": "Greatest Common Factor",
                    "status": "needs_review",
                    "reason": "The verified set is incomplete."
                }
            },
            "idempotent_replay": False,
            "correct_sequences": [2, 3, 4, 6, 8]
        })

        with TestClient(app) as client:
            response = client.post(
                "/api/practice/answer",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "logical_question_key": "group:1",
                    "answer": [2, 3, 4]
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["question_type"],
            "multi_select"
        )
        self.assertEqual(
            response.json()["concepts"][0]["status"],
            "needs_review"
        )
        self.assertNotIn("correct_sequences", response.json())
        self.assertEqual(service.calls[0]["answer"], [2, 3, 4])

    def test_associates_session_answer_with_attempt(self):
        self._set_service({
            "attempt_id": 23,
            "logical_question_key": "group:1",
            "question_type": "multi_select",
            "status": "correct",
            "feedback": "Correct.",
            "concept_diagnoses": {},
            "idempotent_replay": False
        })

        with TestClient(app) as client:
            response = client.post(
                "/api/practice/answer",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "session_id": 7,
                    "logical_question_key": "group:1",
                    "answer": [2, 3, 4, 6, 8],
                    "idempotency_key": "session-answer-1"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["session_id"], 7)
        self.assertEqual(
            self.session_service.attachments[0]["attempt_id"],
            23
        )
        self.assertEqual(
            self.session_service.validations[0][
                "logical_question_key"
            ],
            "group:1"
        )

    def test_returns_not_found_for_unknown_question(self):
        self._set_service({
            "status": "question_not_found",
            "feedback": "Question group was not found."
        })

        with TestClient(app) as client:
            response = client.post(
                "/api/practice/answer",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "logical_question_key": "group:999",
                    "answer": [1]
                }
            )

        self.assertEqual(response.status_code, 404)

    def test_returns_conflict_for_reused_idempotency_key(self):
        self._set_service({
            "status": "idempotency_conflict",
            "feedback": "The key belongs to another question."
        })

        with TestClient(app) as client:
            response = client.post(
                "/api/practice/answer",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "logical_question_key": "chunk:159",
                    "answer": "5",
                    "idempotency_key": "already-used"
                }
            )

        self.assertEqual(response.status_code, 409)

    def test_rejects_wrong_answer_shape_before_service(self):
        service = self._set_service({})

        with TestClient(app) as client:
            response = client.post(
                "/api/practice/answer",
                json={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "logical_question_key": "group:1",
                    "answer": {"selected": [2, 3]}
                }
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(service.calls, [])


if __name__ == "__main__":
    unittest.main()
