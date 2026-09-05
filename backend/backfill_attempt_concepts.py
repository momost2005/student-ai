from sqlalchemy import select

from app.db.database import SessionLocal

from app.models.curriculum import (
    PracticeAttempt,
    PracticeAttemptConcept,
    CurriculumConcept,
    CurriculumChunkConcept
)


db = SessionLocal()


try:

    attempts = (
        db.execute(
            select(
                PracticeAttempt
            )
            .where(
                PracticeAttempt.chunk_id
                .is_not(None)
            )
            .order_by(
                PracticeAttempt.id
            )
        )
        .scalars()
        .all()
    )


    created_count = 0


    for attempt in attempts:

        concepts = (
            db.execute(
                select(
                    CurriculumConcept
                )
                .join(
                    CurriculumChunkConcept,
                    CurriculumChunkConcept.concept_id
                    == CurriculumConcept.id
                )
                .where(
                    CurriculumChunkConcept.chunk_id
                    == attempt.chunk_id
                )
            )
            .scalars()
            .all()
        )


        for concept in concepts:

            existing = (
                db.execute(
                    select(
                        PracticeAttemptConcept
                    )
                    .where(
                        PracticeAttemptConcept.attempt_id
                        == attempt.id,

                        PracticeAttemptConcept.concept_code
                        == concept.code
                    )
                )
                .scalar_one_or_none()
            )


            if existing:
                continue


            snapshot = (
                PracticeAttemptConcept(
                    attempt_id=attempt.id,
                    concept_id=concept.id,
                    concept_code=concept.code,
                    concept_name=concept.name,
                    source="question_mapping"
                )
            )

            db.add(snapshot)

            created_count += 1


    db.commit()


    print()
    print("=" * 80)
    print("ATTEMPT CONCEPT BACKFILL")
    print("=" * 80)

    print(
        f"Snapshots created: "
        f"{created_count}"
    )


finally:

    db.close()