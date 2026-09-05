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

from app.repositories.practice_attempt_question_repository import (
    PracticeAttemptQuestionRepository
)

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

from app.services.practice_evaluation_service import (
    PracticeEvaluationService
)


if len(sys.argv) < 3:

    print()
    print("Usage:")

    print(
        'python test_practice_evaluation.py '
        '<chunk_id> "<student_answer>"'
    )

    print()

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


db = SessionLocal()


try:

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


    curriculum_repository = (
        CurriculumRepository()
    )


    question_identity_repository = (
        PracticeAttemptQuestionRepository()
    )


    evaluation_service = (
        PracticeEvaluationService(
            repository=(
                curriculum_repository
            ),
            ai_gateway=(
                ai_gateway
            ),
            question_identity_repository=(
                question_identity_repository
            )
        )
    )


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
    print("--- Question Identity ---")


    print(
        f"Logical Question Key: "
        f"{result.get('logical_question_key')}"
    )


    print()
    print("--- Overall Evaluation ---")


    print(
        f"Attempt ID: "
        f"{result.get('attempt_id')}"
    )

    print(
        f"AI Status: "
        f"{result.get('ai_status')}"
    )

    print(
        f"Final Status: "
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