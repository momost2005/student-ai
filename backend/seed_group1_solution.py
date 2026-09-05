import json

from sqlalchemy import select

from app.db.database import (
    SessionLocal
)

from app.models.question_group import (
    CurriculumQuestionGroup,
    CurriculumQuestionGroupSolution
)


db = SessionLocal()


try:

    # -------------------------------------------------
    # 1. Find logical question group
    # -------------------------------------------------

    group_statement = (
        select(
            CurriculumQuestionGroup
        )
        .where(
            CurriculumQuestionGroup.group_key
            == "question_1_gcf_of_1_pairs"
        )
    )


    group = (
        db.execute(
            group_statement
        )
        .scalar_one_or_none()
    )


    if not group:

        raise RuntimeError(
            "Question group was not found."
        )


    # -------------------------------------------------
    # 2. Verified correct selections
    #
    # GCF = 1:
    #
    # 2 -> 17 and 31
    # 3 -> 29 and 73
    # 4 -> 43 and 97
    # 6 -> 59 and 61
    # 8 -> 101 and 113
    # -------------------------------------------------

    payload = {
        "correct_option_sequences": [
            2,
            3,
            4,
            6,
            8
        ]
    }


    answer_payload = json.dumps(
        payload
    )


    explanation = (
        "The pairs with greatest common "
        "factor 1 are options 2, 3, 4, 6, "
        "and 8."
    )


    # -------------------------------------------------
    # 3. Insert or update solution
    # -------------------------------------------------

    solution_statement = (
        select(
            CurriculumQuestionGroupSolution
        )
        .where(
            CurriculumQuestionGroupSolution.question_group_id
            == group.id
        )
    )


    solution = (
        db.execute(
            solution_statement
        )
        .scalar_one_or_none()
    )


    created = False


    if not solution:

        solution = (
            CurriculumQuestionGroupSolution(
                question_group_id=group.id,
                answer_payload=answer_payload,
                explanation=explanation,
                solution_source=(
                    "verified_calculation"
                ),
                verification_status="verified"
            )
        )


        db.add(
            solution
        )

        created = True


    else:

        solution.answer_payload = (
            answer_payload
        )

        solution.explanation = (
            explanation
        )

        solution.solution_source = (
            "verified_calculation"
        )

        solution.verification_status = (
            "verified"
        )


    db.commit()

    db.refresh(
        solution
    )


    # -------------------------------------------------
    # 4. Output
    # -------------------------------------------------

    print()
    print("=" * 80)
    print("QUESTION GROUP SOLUTION")
    print("=" * 80)


    print(
        f"Question Group ID: "
        f"{group.id}"
    )

    print(
        f"Created Now: "
        f"{created}"
    )

    print(
        f"Question Type: "
        f"{group.question_type}"
    )

    print(
        f"Correct Options: "
        f"{payload['correct_option_sequences']}"
    )

    print(
        f"Solution Source: "
        f"{solution.solution_source}"
    )

    print(
        f"Verification Status: "
        f"{solution.verification_status}"
    )


finally:

    db.close()