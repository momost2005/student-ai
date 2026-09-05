from sqlalchemy import select

from app.db.database import (
    SessionLocal
)

from app.models.curriculum import (
    PracticeAttempt
)

from app.repositories.practice_attempt_question_repository import (
    PracticeAttemptQuestionRepository
)


db = SessionLocal()


try:

    repository = (
        PracticeAttemptQuestionRepository()
    )


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


    processed = 0


    for attempt in attempts:

        repository.save_identity(
            db=db,
            attempt_id=attempt.id,
            chunk_id=attempt.chunk_id
        )

        processed += 1


    print()
    print("=" * 80)
    print(
        "ATTEMPT LOGICAL QUESTION BACKFILL"
    )
    print("=" * 80)


    print(
        f"Attempts processed: "
        f"{processed}"
    )


finally:

    db.close()