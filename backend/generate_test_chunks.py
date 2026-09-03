import sys

from app.db.database import SessionLocal

from app.services.curriculum_chunking_service import (
    CurriculumChunkingService
)


if len(sys.argv) < 2:

    print(
        "Usage: "
        "python generate_test_chunks.py "
        "<page_number>"
    )

    sys.exit(1)


page_number = int(
    sys.argv[1]
)


db = SessionLocal()


try:

    service = CurriculumChunkingService()

    chunks = service.generate_chunks(
        db=db,
        document_id=1,
        page_number=page_number
    )


    print()
    print("=" * 80)

    print(
        f"Generated chunks: "
        f"{len(chunks)}"
    )

    print("=" * 80)


    for chunk in chunks:

        print()

        print("-" * 80)

        print(
            f"Chunk ID: "
            f"{chunk.id}"
        )

        print(
            f"Type: "
            f"{chunk.chunk_type}"
        )

        print(
            f"Question: "
            f"{chunk.question_number}"
        )

        print()

        print(
            chunk.content[:1000]
        )


finally:

    db.close()