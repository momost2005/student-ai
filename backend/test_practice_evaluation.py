import sys

from app.ai.gateway import (
    AIGateway
)

from app.ai.registry import (
    AIProviderRegistry
)

from app.ai.settings import (
    AISettings
)

from app.db.database import (
    SessionLocal
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

from app.services.practice_evaluation_service import (
    PracticeEvaluationService
)


# -------------------------------------------------
# Command-line arguments
# -------------------------------------------------

if len(sys.argv) < 3:

    print()
    print(
        "Usage:"
    )

    print(
        'python test_practice_evaluation.py '
        '<chunk_id> "<student_answer>"'
    )

    print()

    print(
        "Example:"
    )

    print(
        'python test_practice_evaluation.py '
        '158 "GCF = 15"'
    )

    sys.exit(1)


try:

    chunk_id = int(
        sys.argv[1]
    )

except ValueError:

    print(
        "chunk_id must be an integer."
    )

    sys.exit(1)


student_answer = " ".join(
    sys.argv[2:]
)


# -------------------------------------------------
# Database
# -------------------------------------------------

db = SessionLocal()


try:

    # ---------------------------------------------
    # AI infrastructure
    # ---------------------------------------------

    system_repository = (
        SystemSettingsRepository()
    )


    ai_settings = (
        AISettings(
            system_repository
        )
    )


    ai_registry = (
        AIProviderRegistry()
    )


    ai_gateway = (
        AIGateway(
            settings=ai_settings,
            registry=ai_registry
        )
    )


    # ---------------------------------------------
    # Curriculum repository
    # ---------------------------------------------

    curriculum_repository = (
        CurriculumRepository()
    )


    # ---------------------------------------------
    # Evaluation service
    # ---------------------------------------------

    evaluation_service = (
        PracticeEvaluationService(
            repository=(
                curriculum_repository
            ),
            ai_gateway=(
                ai_gateway
            )
        )
    )


    # ---------------------------------------------
    # Evaluate
    # ---------------------------------------------

    result = (
        evaluation_service.evaluate(
            db=db,
            student_id=1,
            curriculum_id=1,
            chunk_id=chunk_id,
            student_answer=(
                student_answer
            )
        )
    )


    # ---------------------------------------------
    # Output
    # ---------------------------------------------

    print()
    print("=" * 80)
    print("PRACTICE EVALUATION")
    print("=" * 80)


    print(
        f"Chunk ID: "
        f"{chunk_id}"
    )

    print(
        f"Student Answer: "
        f"{student_answer}"
    )


    print()
    print("--- Overall Evaluation ---")


    print(
        f"Attempt ID: "
        f"{result.get('attempt_id')}"
    )

    print(
        f"Status: "
        f"{result.get('status')}"
    )

    print(
        f"Feedback: "
        f"{result.get('feedback')}"
    )


    print()
    print("--- AI ---")


    print(
        f"Provider: "
        f"{result.get('provider')}"
    )

    print(
        f"Model: "
        f"{result.get('model')}"
    )

    print(
        f"Solution Source: "
        f"{result.get('solution_source')}"
    )


    print()
    print("--- Concept Diagnoses ---")


    concept_diagnoses = (
        result.get(
            "concept_diagnoses",
            {}
        )
    )


    if not concept_diagnoses:

        print(
            "No concept diagnoses returned."
        )


    else:

        for (
            concept_code,
            diagnosis
        ) in concept_diagnoses.items():

            print()

            print(
                f"Concept: "
                f"{concept_code}"
            )

            print(
                f"Status: "
                f"{diagnosis.get('status')}"
            )

            print(
                f"Reason: "
                f"{diagnosis.get('reason')}"
            )


finally:

    db.close()