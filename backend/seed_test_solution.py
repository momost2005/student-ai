from app.db.database import SessionLocal

from app.models.curriculum import (
    CurriculumQuestionSolution
)


db = SessionLocal()


try:

    solution = CurriculumQuestionSolution(
        chunk_id=160,

        final_answer=(
            "GCF = 45"
        ),

        solution_steps=(
            "45 = 3^2 × 5\n"
            "135 = 3^3 × 5\n"
            "180 = 2^2 × 3^2 × 5\n"
            "Common prime factors = 3^2 × 5\n"
            "GCF = 45"
        ),

        solution_source=(
            "verified_calculation"
        ),

        verification_status=(
            "verified"
        )
    )

    db.add(solution)
    db.commit()

    print(
        f"Solution ID: {solution.id}"
    )


finally:

    db.close()