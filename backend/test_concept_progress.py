from app.db.database import (
    SessionLocal
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

from app.services.concept_progress_settings import (
    ConceptProgressSettings
)

from app.services.student_concept_progress_service import (
    StudentConceptProgressService
)


db = SessionLocal()


try:

    curriculum_repository = (
        CurriculumRepository()
    )


    system_settings_repository = (
        SystemSettingsRepository()
    )


    concept_settings = (
        ConceptProgressSettings(
            repository=(
                system_settings_repository
            )
        )
    )


    service = (
        StudentConceptProgressService(
            repository=(
                curriculum_repository
            ),
            settings=(
                concept_settings
            )
        )
    )


    results = (
        service
        .get_lesson_concept_progress(
            db=db,
            student_id=1,
            curriculum_id=1,
            lesson_number="3"
        )
    )


    print()
    print("=" * 80)
    print("CONCEPT PROGRESS")
    print("=" * 80)


    for item in results:

        print()

        print(
            f"Concept: "
            f"{item['concept_name']}"
        )

        print(
            f"Code: "
            f"{item['concept_code']}"
        )


        print()
        print("--- Historical Activity ---")

        print(
            f"Total Occurrences: "
            f"{item['total_occurrences']}"
        )

        print(
            f"Unique Questions Seen: "
            f"{item['unique_questions_seen']}"
        )

        print(
            f"Historical Demonstrated: "
            f"{item['historical_demonstrated_count']}"
        )

        print(
            f"Historical Needs Review: "
            f"{item['historical_needs_review_count']}"
        )

        print(
            f"Historical Insufficient Evidence: "
            f"{item['historical_insufficient_evidence_count']}"
        )


        print()
        print("--- Current Evidence ---")

        print(
            f"Unique Assessed Questions: "
            f"{item['unique_assessed_questions']}"
        )

        print(
            f"Current Demonstrated: "
            f"{item['current_demonstrated']}"
        )

        print(
            f"Current Needs Review: "
            f"{item['current_needs_review']}"
        )

        print(
            f"Observed Understanding: "
            f"{item['observed_understanding_percent']}%"
        )


        print()
        print("--- Latest Evidence ---")

        print(
            f"Latest Assessed Status: "
            f"{item['latest_assessed_status']}"
        )

        print(
            f"Latest Assessed Attempt: "
            f"{item['latest_assessed_attempt_id']}"
        )


        print()
        print("--- Classification ---")

        print(
            f"Has Enough Evidence: "
            f"{item['has_enough_evidence']}"
        )

        print(
            f"Minimum Unique Assessed Questions: "
            f"{item['minimum_unique_assessed_questions']}"
        )

        print(
            f"Classification: "
            f"{item['classification']}"
        )

        print(
            f"Classification Reason: "
            f"{item['classification_reason']}"
        )


finally:

    db.close()