import unittest

from fastapi.testclient import TestClient

from app.api.progress import (
    get_student_concept_progress_service,
    get_student_progress_service
)
from app.db.database import get_db
from app.main import app


class FakeLessonProgressService:

    def __init__(self, result):
        self.result = result
        self.calls = []

    def get_lesson_progress(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakeConceptProgressService:

    def __init__(self, result):
        self.result = result
        self.calls = []

    def get_lesson_concept_progress(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class ProgressApiTests(unittest.TestCase):

    def setUp(self):
        self.db = object()
        app.dependency_overrides[get_db] = lambda: self.db

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_returns_lesson_progress_without_recalculation(self):
        expected = {
            "student_id": 1,
            "curriculum_id": 1,
            "lesson_number": "3",
            "total_attempts": 10,
            "assessed_attempts": 10,
            "correct_attempts": 3,
            "partial_attempts": 4,
            "incorrect_attempts": 3,
            "attempt_accuracy_percent": 30.0,
            "unique_questions_attempted": 4,
            "total_practice_questions": 46,
            "coverage_percent": 8.7,
            "current_correct": 0,
            "current_partial": 3,
            "current_incorrect": 1,
            "current_accuracy_percent": 0.0,
            "observed_performance_percent": 37.5,
            "mastery_status": "insufficient_evidence",
            "mastery_reason": "More practice is needed.",
            "mastery_evidence": {
                "minimum_unique_questions": 5,
                "minimum_coverage_percent": 10.0,
                "has_enough_evidence": False
            }
        }
        service = FakeLessonProgressService(expected)
        app.dependency_overrides[
            get_student_progress_service
        ] = lambda: service

        with TestClient(app) as client:
            response = client.get(
                "/api/progress/lesson",
                params={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "lesson_number": " 3 "
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)
        self.assertEqual(
            service.calls[0]["lesson_number"],
            "3"
        )

    def test_returns_concept_progress_without_recalculation(self):
        expected = [{
            "concept_code": "greatest_common_factor",
            "concept_name": "Greatest Common Factor",
            "total_occurrences": 8,
            "unique_questions_seen": 4,
            "historical_demonstrated_count": 4,
            "historical_needs_review_count": 2,
            "historical_insufficient_evidence_count": 0,
            "historical_unassessed_count": 2,
            "historical_evidence_count": 6,
            "unique_assessed_questions": 4,
            "current_demonstrated": 2,
            "current_needs_review": 2,
            "observed_understanding_percent": 50.0,
            "latest_assessed_status": "needs_review",
            "latest_assessed_attempt_id": 10,
            "has_enough_evidence": True,
            "minimum_unique_assessed_questions": 3,
            "classification": "developing",
            "classification_reason": "Mixed current evidence."
        }]
        service = FakeConceptProgressService(expected)
        app.dependency_overrides[
            get_student_concept_progress_service
        ] = lambda: service

        with TestClient(app) as client:
            response = client.get(
                "/api/progress/concepts",
                params={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "lesson_number": "3"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)
        self.assertEqual(
            service.calls[0]["db"],
            self.db
        )

    def test_returns_empty_concept_list(self):
        service = FakeConceptProgressService([])
        app.dependency_overrides[
            get_student_concept_progress_service
        ] = lambda: service

        with TestClient(app) as client:
            response = client.get(
                "/api/progress/concepts",
                params={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "lesson_number": "3"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_keeps_null_latest_evidence_fields(self):
        expected = [{
            "concept_code": "prime_factorization",
            "concept_name": "Prime Factorization",
            "total_occurrences": 3,
            "unique_questions_seen": 2,
            "historical_demonstrated_count": 0,
            "historical_needs_review_count": 0,
            "historical_insufficient_evidence_count": 2,
            "historical_unassessed_count": 1,
            "historical_evidence_count": 2,
            "unique_assessed_questions": 0,
            "current_demonstrated": 0,
            "current_needs_review": 0,
            "observed_understanding_percent": 0.0,
            "latest_assessed_status": None,
            "latest_assessed_attempt_id": None,
            "has_enough_evidence": False,
            "minimum_unique_assessed_questions": 3,
            "classification": "insufficient_evidence",
            "classification_reason": "More evidence is needed."
        }]
        service = FakeConceptProgressService(expected)
        app.dependency_overrides[
            get_student_concept_progress_service
        ] = lambda: service

        with TestClient(app) as client:
            response = client.get(
                "/api/progress/concepts",
                params={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "lesson_number": "3"
                }
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected)

    def test_rejects_blank_lesson_number(self):
        service = FakeLessonProgressService({})
        app.dependency_overrides[
            get_student_progress_service
        ] = lambda: service

        with TestClient(app) as client:
            response = client.get(
                "/api/progress/lesson",
                params={
                    "student_id": 1,
                    "curriculum_id": 1,
                    "lesson_number": "   "
                }
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(service.calls, [])

    def test_rejects_non_positive_identifiers(self):
        service = FakeConceptProgressService([])
        app.dependency_overrides[
            get_student_concept_progress_service
        ] = lambda: service

        with TestClient(app) as client:
            response = client.get(
                "/api/progress/concepts",
                params={
                    "student_id": 0,
                    "curriculum_id": -1,
                    "lesson_number": "3"
                }
            )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(service.calls, [])


if __name__ == "__main__":
    unittest.main()
