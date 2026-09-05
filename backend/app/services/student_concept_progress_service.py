from sqlalchemy.orm import Session

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.services.concept_progress_settings import (
    ConceptProgressSettings
)


class StudentConceptProgressService:

    ASSESSED_STATUSES = {
        "demonstrated",
        "needs_review"
    }


    def __init__(
        self,
        repository: CurriculumRepository,
        settings: ConceptProgressSettings
    ):

        self.repository = repository
        self.settings = settings


    def _get_question_key(
        self,
        attempt
    ) -> str:

        if attempt.chunk_id is not None:

            return (
                f"chunk:{attempt.chunk_id}"
            )

        return (
            f"snapshot:"
            f"{attempt.question_number}:"
            f"{attempt.question_content}"
        )


    def get_lesson_concept_progress(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        lesson_number: str
    ) -> list[dict]:

        rows = (
            self.repository
            .get_student_lesson_concept_diagnoses(
                db=db,
                student_id=student_id,
                curriculum_id=curriculum_id,
                lesson_number=lesson_number
            )
        )


        concepts = {}


        for (
            diagnosis,
            attempt
        ) in rows:

            concept_code = (
                diagnosis.concept_code
            )


            if concept_code not in concepts:

                concepts[
                    concept_code
                ] = {
                    "concept_code":
                        concept_code,

                    "concept_name":
                        diagnosis.concept_name,

                    # ---------------------------------
                    # Historical raw occurrence counts
                    # ---------------------------------

                    "total_occurrences":
                        0,

                    "historical_demonstrated_count":
                        0,

                    "historical_needs_review_count":
                        0,

                    "historical_insufficient_evidence_count":
                        0,

                    # ---------------------------------
                    # Latest overall assessed evidence
                    # ---------------------------------

                    "latest_assessed_status":
                        None,

                    "latest_assessed_attempt_id":
                        None,

                    # ---------------------------------
                    # Internal working dictionaries
                    # ---------------------------------

                    "_unique_questions_seen":
                        set(),

                    "_latest_assessed_by_question":
                        {}
                }


            item = concepts[
                concept_code
            ]


            item[
                "total_occurrences"
            ] += 1


            question_key = (
                self._get_question_key(
                    attempt
                )
            )


            item[
                "_unique_questions_seen"
            ].add(
                question_key
            )


            status = (
                diagnosis.diagnosis_status
            )


            # -----------------------------------------
            # Historical counts
            # -----------------------------------------

            if status == "demonstrated":

                item[
                    "historical_demonstrated_count"
                ] += 1


            elif status == "needs_review":

                item[
                    "historical_needs_review_count"
                ] += 1


            elif (
                status
                == "insufficient_evidence"
            ):

                item[
                    "historical_insufficient_evidence_count"
                ] += 1


            # -----------------------------------------
            # Only real assessed evidence can update
            # the current result for a question.
            #
            # insufficient_evidence does NOT erase
            # earlier assessed evidence.
            # -----------------------------------------

            if (
                status
                in self.ASSESSED_STATUSES
            ):

                item[
                    "_latest_assessed_by_question"
                ][
                    question_key
                ] = {
                    "status":
                        status,

                    "attempt_id":
                        attempt.id
                }


                item[
                    "latest_assessed_status"
                ] = status

                item[
                    "latest_assessed_attempt_id"
                ] = attempt.id


        minimum_unique_questions = (
            self.settings
            .get_minimum_unique_assessed_questions(
                db
            )
        )


        weak_threshold = (
            self.settings
            .get_weak_threshold(
                db
            )
        )


        strong_threshold = (
            self.settings
            .get_strong_threshold(
                db
            )
        )


        results = []


        for item in concepts.values():

            unique_questions_seen = len(
                item[
                    "_unique_questions_seen"
                ]
            )


            latest_assessed_by_question = (
                item[
                    "_latest_assessed_by_question"
                ]
            )


            unique_assessed_questions = len(
                latest_assessed_by_question
            )


            current_demonstrated = sum(
                1
                for evidence
                in latest_assessed_by_question.values()
                if evidence["status"]
                == "demonstrated"
            )


            current_needs_review = sum(
                1
                for evidence
                in latest_assessed_by_question.values()
                if evidence["status"]
                == "needs_review"
            )


            observed_understanding = 0.0


            if unique_assessed_questions > 0:

                observed_understanding = (
                    current_demonstrated
                    / unique_assessed_questions
                    * 100
                )


            has_enough_evidence = (
                unique_assessed_questions
                >= minimum_unique_questions
            )


            # -----------------------------------------
            # Evidence-aware classification
            # -----------------------------------------

            if not has_enough_evidence:

                classification = (
                    "insufficient_evidence"
                )

                classification_reason = (
                    "More different assessed "
                    "questions are needed before "
                    "this concept can be classified."
                )


            elif (
                observed_understanding
                < weak_threshold
            ):

                classification = "weak"

                classification_reason = (
                    "Across enough different "
                    "questions, the student "
                    "frequently needs review "
                    "on this concept."
                )


            elif (
                observed_understanding
                < strong_threshold
            ):

                classification = (
                    "developing"
                )

                classification_reason = (
                    "Across enough different "
                    "questions, the student shows "
                    "some understanding but is "
                    "not yet consistently "
                    "demonstrating the concept."
                )


            else:

                classification = "strong"

                classification_reason = (
                    "Across enough different "
                    "questions, the student "
                    "consistently demonstrates "
                    "understanding of this concept."
                )


            result = {
                "concept_code":
                    item["concept_code"],

                "concept_name":
                    item["concept_name"],

                "total_occurrences":
                    item["total_occurrences"],

                "unique_questions_seen":
                    unique_questions_seen,

                "historical_demonstrated_count":
                    item[
                        "historical_demonstrated_count"
                    ],

                "historical_needs_review_count":
                    item[
                        "historical_needs_review_count"
                    ],

                "historical_insufficient_evidence_count":
                    item[
                        "historical_insufficient_evidence_count"
                    ],

                "unique_assessed_questions":
                    unique_assessed_questions,

                "current_demonstrated":
                    current_demonstrated,

                "current_needs_review":
                    current_needs_review,

                "observed_understanding_percent":
                    round(
                        observed_understanding,
                        2
                    ),

                "latest_assessed_status":
                    item[
                        "latest_assessed_status"
                    ],

                "latest_assessed_attempt_id":
                    item[
                        "latest_assessed_attempt_id"
                    ],

                "has_enough_evidence":
                    has_enough_evidence,

                "minimum_unique_assessed_questions":
                    minimum_unique_questions,

                "classification":
                    classification,

                "classification_reason":
                    classification_reason
            }


            results.append(
                result
            )


        results.sort(
            key=lambda item:
                item["concept_name"]
        )


        return results