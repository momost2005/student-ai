from sqlalchemy import select

from app.db.database import (
    SessionLocal
)

from app.models.curriculum import (
    CurriculumChunk,
    CurriculumConcept,
    CurriculumChunkConcept,
    CurriculumQuestionSolution
)


db = SessionLocal()


try:

    # -------------------------------------------------
    # 1. Load the two concepts already created
    # -------------------------------------------------

    concept_codes = [
        "greatest_common_factor",
        "prime_factorization"
    ]


    concepts = {}


    for concept_code in concept_codes:

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
                == concept_code
            )
        )


        concept = (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )


        if not concept:

            raise RuntimeError(
                f"Concept not found: "
                f"{concept_code}"
            )


        concepts[
            concept_code
        ] = concept


    # -------------------------------------------------
    # 2. Define the two real curriculum questions
    # -------------------------------------------------

    question_specs = [
        {
            "chunk_id": 158,

            "final_answer": (
                "75 = 3 × 5^2; "
                "120 = 2^3 × 3 × 5; "
                "GCF = 15"
            ),

            "solution_steps": (
                "75 = 3 × 5^2\n"
                "120 = 2^3 × 3 × 5\n"
                "Common prime factors = 3 × 5\n"
                "GCF = 15"
            )
        },

        {
            "chunk_id": 159,

            "final_answer": (
                "60 = 2^2 × 3 × 5; "
                "130 = 2 × 5 × 13; "
                "GCF = 10"
            ),

            "solution_steps": (
                "60 = 2^2 × 3 × 5\n"
                "130 = 2 × 5 × 13\n"
                "Common prime factors = 2 × 5\n"
                "GCF = 10"
            )
        }
    ]


    # -------------------------------------------------
    # 3. Validate chunks
    # -------------------------------------------------

    for spec in question_specs:

        chunk = db.get(
            CurriculumChunk,
            spec["chunk_id"]
        )


        if not chunk:

            raise RuntimeError(
                f"Chunk not found: "
                f"{spec['chunk_id']}"
            )


        if (
            chunk.lesson_number
            != "3"
        ):

            raise RuntimeError(
                f"Chunk {chunk.id} "
                f"is not Lesson 3."
            )


        if (
            chunk.chunk_type
            != "practice_question"
        ):

            raise RuntimeError(
                f"Chunk {chunk.id} "
                f"is not a practice question."
            )


    # -------------------------------------------------
    # 4. Map concepts to each question
    # -------------------------------------------------

    created_mappings = 0


    for spec in question_specs:

        chunk_id = spec[
            "chunk_id"
        ]


        for concept in concepts.values():

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


            existing_mapping = (
                db.execute(
                    statement
                )
                .scalar_one_or_none()
            )


            if existing_mapping:
                continue


            mapping = (
                CurriculumChunkConcept(
                    chunk_id=chunk_id,
                    concept_id=concept.id
                )
            )


            db.add(
                mapping
            )

            created_mappings += 1


    # -------------------------------------------------
    # 5. Create or update verified solutions
    # -------------------------------------------------

    created_solutions = 0
    updated_solutions = 0


    for spec in question_specs:

        statement = (
            select(
                CurriculumQuestionSolution
            )
            .where(
                CurriculumQuestionSolution.chunk_id
                == spec["chunk_id"]
            )
        )


        solution = (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )


        if not solution:

            solution = (
                CurriculumQuestionSolution(
                    chunk_id=(
                        spec["chunk_id"]
                    ),

                    final_answer=(
                        spec["final_answer"]
                    ),

                    solution_steps=(
                        spec["solution_steps"]
                    ),

                    solution_source=(
                        "verified_calculation"
                    ),

                    verification_status=(
                        "verified"
                    )
                )
            )


            db.add(
                solution
            )

            created_solutions += 1


        else:

            solution.final_answer = (
                spec["final_answer"]
            )

            solution.solution_steps = (
                spec["solution_steps"]
            )

            solution.solution_source = (
                "verified_calculation"
            )

            solution.verification_status = (
                "verified"
            )


            updated_solutions += 1


    db.commit()


    # -------------------------------------------------
    # 6. Print result
    # -------------------------------------------------

    print()
    print("=" * 80)
    print("LESSON 3 GCF EVIDENCE QUESTIONS")
    print("=" * 80)


    print(
        f"Concept mappings created: "
        f"{created_mappings}"
    )

    print(
        f"Solutions created: "
        f"{created_solutions}"
    )

    print(
        f"Solutions updated: "
        f"{updated_solutions}"
    )


    print()


    for spec in question_specs:

        print(
            f"Chunk {spec['chunk_id']}"
        )

        print(
            f"Verified answer: "
            f"{spec['final_answer']}"
        )

        print(
            "Concepts:"
        )

        for concept_code in concept_codes:

            print(
                f"- {concept_code}"
            )

        print()


finally:

    db.close()