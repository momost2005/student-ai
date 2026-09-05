from sqlalchemy.orm import (
    Session
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.services.logical_question_service import (
    LogicalQuestionService
)

from app.services.mastery_settings import (
    MasterySettings
)


class StudentProgressService:

    ASSESSED_STATUSES = {
        "correct",
        "partial",
        "incorrect"
    }


    def __init__(
        self,
        repository: CurriculumRepository,
        mastery_settings: MasterySettings,
        logical_question_service: LogicalQuestionService
    ):

        self.repository = repository

        self.mastery_settings = (
            mastery_settings
        )

        self.logical_question_service = (
            logical_question_service
        )


    def get_lesson_progress(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        lesson_number: str
    ) -> dict:

        # -----------------------------------------
        # 1. Load student attempts
        # -----------------------------------------

        attempts = (
            self.repository
            .get_student_lesson_attempts(
                db=db,
                student_id=student_id,
                curriculum_id=curriculum_id,
                lesson_number=lesson_number
            )
        )


        assessed_attempts = [
            attempt
            for attempt in attempts
            if attempt.evaluation_status
            in self.ASSESSED_STATUSES
        ]


        total_attempts = len(
            attempts
        )


        assessed_count = len(
            assessed_attempts
        )


        # -----------------------------------------
        # 2. Historical attempt counts
        # -----------------------------------------

        correct_attempts = sum(
            1
            for attempt in assessed_attempts
            if attempt.evaluation_status
            == "correct"
        )


        partial_attempts = sum(
            1
            for attempt in assessed_attempts
            if attempt.evaluation_status
            == "partial"
        )


        incorrect_attempts = sum(
            1
            for attempt in assessed_attempts
            if attempt.evaluation_status
            == "incorrect"
        )


        attempt_accuracy = 0.0


        if assessed_count > 0:

            attempt_accuracy = (
                correct_attempts
                / assessed_count
                * 100
            )


        # -----------------------------------------
        # 3. Keep latest assessed attempt for each
        #    LOGICAL question.
        #
        #    Several chunks may now represent one
        #    question group.
        # -----------------------------------------

        latest_by_question = {}


        for attempt in assessed_attempts:

            question_key = (
                self.logical_question_service
                .get_question_key_for_attempt(
                    db=db,
                    attempt=attempt
                )
            )


            # Attempts are already ordered by
            # created_at / id, so the latest one
            # replaces the previous value.
            latest_by_question[
                question_key
            ] = attempt


        latest_attempts = list(
            latest_by_question.values()
        )


        unique_questions = len(
            latest_attempts
        )


        # -----------------------------------------
        # 4. Count LOGICAL curriculum questions
        # -----------------------------------------

        total_available_questions = (
            self.logical_question_service
            .count_lesson_logical_practice_questions(
                db=db,
                curriculum_id=curriculum_id,
                lesson_number=lesson_number
            )
        )


        # -----------------------------------------
        # 5. Coverage
        # -----------------------------------------

        coverage_percent = 0.0


        if total_available_questions > 0:

            coverage_percent = (
                unique_questions
                / total_available_questions
                * 100
            )


        # -----------------------------------------
        # 6. Current state
        # -----------------------------------------

        current_correct = sum(
            1
            for attempt in latest_attempts
            if attempt.evaluation_status
            == "correct"
        )


        current_partial = sum(
            1
            for attempt in latest_attempts
            if attempt.evaluation_status
            == "partial"
        )


        current_incorrect = sum(
            1
            for attempt in latest_attempts
            if attempt.evaluation_status
            == "incorrect"
        )


        current_accuracy = 0.0


        if unique_questions > 0:

            current_accuracy = (
                current_correct
                / unique_questions
                * 100
            )


        # -----------------------------------------
        # 7. Observed performance
        #
        # correct   = 1.0
        # partial   = 0.5
        # incorrect = 0.0
        # -----------------------------------------

        observed_score = 0.0


        if unique_questions > 0:

            observed_points = (
                current_correct
                +
                (
                    current_partial
                    * 0.5
                )
            )


            observed_score = (
                observed_points
                / unique_questions
                * 100
            )


        # -----------------------------------------
        # 8. Mastery evidence settings
        # -----------------------------------------

        minimum_unique_questions = (
            self.mastery_settings
            .get_minimum_unique_questions(
                db
            )
        )


        minimum_coverage_percent = (
            self.mastery_settings
            .get_minimum_coverage_percent(
                db
            )
        )


        proficient_threshold = (
            self.mastery_settings
            .get_proficient_threshold(
                db
            )
        )


        strong_threshold = (
            self.mastery_settings
            .get_strong_threshold(
                db
            )
        )


        has_enough_evidence = (
            unique_questions
            >= minimum_unique_questions

            and

            coverage_percent
            >= minimum_coverage_percent
        )


        # -----------------------------------------
        # 9. Mastery classification
        # -----------------------------------------

        if not has_enough_evidence:

            mastery_status = (
                "insufficient_evidence"
            )

            mastery_reason = (
                "More practice questions "
                "are needed before lesson "
                "mastery can be estimated."
            )


        elif observed_score >= strong_threshold:

            mastery_status = "strong"

            mastery_reason = (
                "The student is performing "
                "strongly across enough "
                "lesson evidence."
            )


        elif observed_score >= proficient_threshold:

            mastery_status = (
                "proficient"
            )

            mastery_reason = (
                "The student demonstrates "
                "proficiency across enough "
                "lesson evidence."
            )


        else:

            mastery_status = (
                "developing"
            )

            mastery_reason = (
                "There is enough evidence "
                "to assess the lesson, but "
                "performance still needs "
                "improvement."
            )


        # -----------------------------------------
        # 10. Result
        # -----------------------------------------

        return {
            "student_id":
                student_id,

            "curriculum_id":
                curriculum_id,

            "lesson_number":
                lesson_number,

            "total_attempts":
                total_attempts,

            "assessed_attempts":
                assessed_count,

            "correct_attempts":
                correct_attempts,

            "partial_attempts":
                partial_attempts,

            "incorrect_attempts":
                incorrect_attempts,

            "attempt_accuracy_percent":
                round(
                    attempt_accuracy,
                    2
                ),

            "unique_questions_attempted":
                unique_questions,

            "total_practice_questions":
                total_available_questions,

            "coverage_percent":
                round(
                    coverage_percent,
                    2
                ),

            "current_correct":
                current_correct,

            "current_partial":
                current_partial,

            "current_incorrect":
                current_incorrect,

            "current_accuracy_percent":
                round(
                    current_accuracy,
                    2
                ),

            "observed_performance_percent":
                round(
                    observed_score,
                    2
                ),

            "mastery_status":
                mastery_status,

            "mastery_reason":
                mastery_reason,

            "mastery_evidence": {
                "minimum_unique_questions":
                    minimum_unique_questions,

                "minimum_coverage_percent":
                    minimum_coverage_percent,

                "has_enough_evidence":
                    has_enough_evidence
            }
        }