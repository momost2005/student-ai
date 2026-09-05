from sqlalchemy import select

from app.db.database import SessionLocal

from app.models.curriculum import (
    CurriculumConcept,
    CurriculumChunkConcept
)


db = SessionLocal()


try:

    concept_specs = [
        {
            "code": "greatest_common_factor",
            "name": "Greatest Common Factor",
            "description": (
                "Finding the greatest factor "
                "shared by two or more numbers."
            )
        },
        {
            "code": "prime_factorization",
            "name": "Prime Factorization",
            "description": (
                "Expressing a whole number "
                "as a product of prime numbers."
            )
        },
        {
            "code": "common_factors",
            "name": "Common Factors",
            "description": (
                "Identifying factors shared "
                "by two or more numbers."
            )
        }
    ]


    concepts = {}


    for spec in concept_specs:

        statement = (
            select(
                CurriculumConcept
            )
            .where(
                CurriculumConcept.curriculum_id
                == 1,

                CurriculumConcept.lesson_number
                == "3",

                CurriculumConcept.code
                == spec["code"]
            )
        )

        concept = db.execute(
            statement
        ).scalar_one_or_none()


        if not concept:

            concept = CurriculumConcept(
                curriculum_id=1,
                lesson_number="3",
                code=spec["code"],
                name=spec["name"],
                description=spec["description"]
            )

            db.add(concept)
            db.flush()


        concepts[
            spec["code"]
        ] = concept


    # Question 160 asks the student to:
    # - find prime factorizations
    # - find the GCF

    chunk_id = 160

    concept_codes_for_chunk = [
        "greatest_common_factor",
        "prime_factorization"
    ]


    for concept_code in concept_codes_for_chunk:

        concept = concepts[
            concept_code
        ]

        statement = (
            select(
                CurriculumChunkConcept
            )
            .where(
                CurriculumChunkConcept.chunk_id
                == chunk_id,

                CurriculumChunkConcept.concept_id
                == concept.id
            )
        )

        mapping = db.execute(
            statement
        ).scalar_one_or_none()


        if not mapping:

            mapping = CurriculumChunkConcept(
                chunk_id=chunk_id,
                concept_id=concept.id
            )

            db.add(mapping)


    db.commit()


    print()
    print("=" * 80)
    print("LESSON 3 CONCEPTS")
    print("=" * 80)

    for concept in concepts.values():

        print(
            f"{concept.id}: "
            f"{concept.code} "
            f"({concept.name})"
        )


    print()
    print(
        "Chunk 160 mapped to:"
    )

    for concept_code in concept_codes_for_chunk:

        print(
            f"- {concept_code}"
        )


finally:

    db.close()