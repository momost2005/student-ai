import sys

from app.db.database import (
    SessionLocal
)

from app.repositories.question_group_attempt_repository import (
    QuestionGroupAttemptRepository
)

from app.repositories.question_group_repository import (
    QuestionGroupRepository
)

from app.services.question_group_evaluation_service import (
    QuestionGroupEvaluationService
)


if len(sys.argv) < 3:

    print()
    print("Usage:")

    print(
        'python test_group_evaluation.py '
        '<group_id> "<selected_options>"'
    )

    sys.exit(1)


question_group_id = int(
    sys.argv[1]
)


selected_sequences = [
    int(
        value.strip()
    )

    for value
    in sys.argv[2].split(",")

    if value.strip()
]


db = SessionLocal()


try:

    repository = (
        QuestionGroupRepository()
    )


    attempt_repository = (
        QuestionGroupAttemptRepository()
    )


    service = (
        QuestionGroupEvaluationService(
            repository=repository,

            attempt_repository=(
                attempt_repository
            )
        )
    )


    result = (
        service.evaluate_multi_select(
            db=db,

            student_id=1,

            curriculum_id=1,

            question_group_id=(
                question_group_id
            ),

            selected_sequences=(
                selected_sequences
            )
        )
    )


    print()
    print("=" * 80)
    print("LOGICAL QUESTION EVALUATION")
    print("=" * 80)


    print(
        f"Attempt ID: "
        f"{result.get('attempt_id')}"
    )

    print(
        f"Logical Question: "
        f"{result.get('logical_question_key')}"
    )

    print(
        f"Question Type: "
        f"{result.get('question_type')}"
    )


    print()
    print("--- Student Answer ---")


    print(
        f"Selected: "
        f"{result.get('selected_sequences')}"
    )


    print()
    print("--- Evaluation ---")


    print(
        f"Status: "
        f"{result.get('status')}"
    )

    print(
        f"Feedback: "
        f"{result.get('feedback')}"
    )


    print()
    print("--- Concept Evidence ---")


    concept_diagnoses = (
        result.get(
            "concept_diagnoses",
            {}
        )
    )


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