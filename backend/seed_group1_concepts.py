from sqlalchemy import select

from app.db.database import (
    SessionLocal
)

from app.models.curriculum import (
    CurriculumConcept
)

from app.models.question_group import (
    CurriculumQuestionGroup
)

from app.models.question_group_concept import (
    CurriculumQuestionGroupConcept
)


db = SessionLocal()


try:

    # -------------------------------------------------
    # 1. Find Group 1
    # -------------------------------------------------

    group = (
        db.execute(
            select(
                CurriculumQuestionGroup
            )
            .where(
                CurriculumQuestionGroup.group_key
                == "question_1_gcf_of_1_pairs"
            )
        )
        .scalar_one_or_none()
    )


    if not group:

        raise RuntimeError(
            "Question group was not found."
        )


    # -------------------------------------------------
    # 2. Find GCF concept
    # -------------------------------------------------

    concept = (
        db.execute(
            select(
                CurriculumConcept
            )
            .where(
                CurriculumConcept.curriculum_id
                == 1,

                CurriculumConcept.lesson_number
                == "3",

                CurriculumConcept.code
                == "greatest_common_factor"
            )
        )
        .scalar_one_or_none()
    )


    if not concept:

        raise RuntimeError(
            "Greatest Common Factor concept "
            "was not found."
        )


    # -------------------------------------------------
    # 3. Find existing mapping
    # -------------------------------------------------

    mapping = (
        db.execute(
            select(
                CurriculumQuestionGroupConcept
            )
            .where(
                CurriculumQuestionGroupConcept.question_group_id
                == group.id,

                CurriculumQuestionGroupConcept.concept_id
                == concept.id
            )
        )
        .scalar_one_or_none()
    )


    created = False


    if not mapping:

        mapping = (
            CurriculumQuestionGroupConcept(
                question_group_id=group.id,
                concept_id=concept.id
            )
        )


        db.add(
            mapping
        )

        created = True


    db.commit()


    print()
    print("=" * 80)
    print("QUESTION GROUP CONCEPT MAPPING")
    print("=" * 80)


    print(
        f"Group ID: {group.id}"
    )

    print(
        f"Concept: {concept.name}"
    )

    print(
        f"Concept Code: {concept.code}"
    )

    print(
        f"Created Now: {created}"
    )


finally:

    db.close()