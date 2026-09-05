import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from app.repositories.curriculum_repository import (
    CurriculumRepository
)
from app.services.practice_submission_service import (
    PracticeSubmissionService
)


class PracticeSubmissionServiceTests(unittest.TestCase):

    def setUp(self):
        self.db = Mock()
        self.attempt_repository = Mock()
        self.standard_service = Mock()
        self.group_service = Mock()

        self.service = PracticeSubmissionService(
            attempt_repository=self.attempt_repository,
            standard_evaluation_service=self.standard_service,
            group_evaluation_service=self.group_service
        )


    def test_dispatches_group_submission(self):
        self.attempt_repository.get_by_idempotency_key.return_value = None
        self.group_service.evaluate_multi_select.return_value = {
            "attempt_id": 12,
            "logical_question_key": "group:1",
            "status": "correct"
        }

        result = self.service.submit(
            db=self.db,
            student_id=1,
            curriculum_id=1,
            logical_question_key="group:1",
            answer={
                "selected_option_sequences": [2, 3, 4]
            },
            idempotency_key="submission-1"
        )

        self.assertEqual(result["attempt_id"], 12)
        self.assertFalse(result["idempotent_replay"])
        self.group_service.evaluate_multi_select.assert_called_once()
        self.standard_service.evaluate.assert_not_called()


    def test_returns_existing_attempt_for_retry(self):
        attempt = SimpleNamespace(id=12)
        self.attempt_repository.get_by_idempotency_key.return_value = attempt
        self.attempt_repository.build_replay_result.return_value = {
            "attempt_id": 12,
            "logical_question_key": "group:1",
            "status": "correct",
            "idempotent_replay": True
        }

        result = self.service.submit(
            db=self.db,
            student_id=1,
            curriculum_id=1,
            logical_question_key="group:1",
            answer=[2, 3, 4],
            idempotency_key="submission-1"
        )

        self.assertEqual(result["attempt_id"], 12)
        self.assertTrue(result["idempotent_replay"])
        self.group_service.evaluate_multi_select.assert_not_called()
        self.standard_service.evaluate.assert_not_called()


    def test_rejects_reusing_key_for_another_question(self):
        attempt = SimpleNamespace(id=12)
        self.attempt_repository.get_by_idempotency_key.return_value = attempt
        self.attempt_repository.build_replay_result.return_value = {
            "attempt_id": 12,
            "logical_question_key": "group:1",
            "status": "correct",
            "idempotent_replay": True
        }

        result = self.service.submit(
            db=self.db,
            student_id=1,
            curriculum_id=1,
            logical_question_key="chunk:158",
            answer="42",
            idempotency_key="submission-1"
        )

        self.assertEqual(result["status"], "idempotency_conflict")
        self.group_service.evaluate_multi_select.assert_not_called()
        self.standard_service.evaluate.assert_not_called()


    def test_dispatches_standard_submission(self):
        self.standard_service.evaluate.return_value = {
            "attempt_id": 13,
            "logical_question_key": "chunk:158",
            "status": "correct"
        }

        result = self.service.submit(
            db=self.db,
            student_id=1,
            curriculum_id=1,
            logical_question_key="chunk:158",
            answer="42"
        )

        self.assertEqual(result["attempt_id"], 13)
        self.assertFalse(result["idempotent_replay"])
        self.standard_service.evaluate.assert_called_once()
        self.group_service.evaluate_multi_select.assert_not_called()


class CurriculumRepositoryAttemptTests(unittest.TestCase):

    def test_saves_attempt_without_concept_mappings(self):
        repository = CurriculumRepository()
        repository.get_chunk_concepts = Mock(return_value=[])
        db = Mock()
        chunk = SimpleNamespace(
            id=158,
            question_number="2",
            content="Question",
            lesson_number="3",
            lesson_title="Factors"
        )

        attempt = repository.save_practice_attempt(
            db=db,
            student_id=1,
            curriculum_id=1,
            chunk=chunk,
            student_answer="42",
            reference_answer=None,
            evaluation_status="cannot_evaluate",
            feedback="No verified answer.",
            solution_source=None,
            ai_provider=None,
            ai_model=None,
            concept_diagnoses=None,
            idempotency_key="submission-2"
        )

        self.assertEqual(attempt.idempotency_key, "submission-2")
        db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
