import sys
from pathlib import Path

from app.db.database import SessionLocal

from app.services.curriculum_ingestion_service import (
    CurriculumIngestionService
)

from app.services.curriculum_chunking_service import (
    CurriculumChunkingService
)


if len(sys.argv) < 3:
    print(
        "Usage: "
        "python ingest_page_range.py "
        "<start_page> <end_page>"
    )
    sys.exit(1)


start_page = int(sys.argv[1])
end_page = int(sys.argv[2])


if start_page > end_page:
    raise ValueError(
        "start_page cannot be greater "
        "than end_page"
    )


project_root = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


pdf_path = (
    project_root
    / "curriculum"
    / "samples"
    / "grade6_math_term1.pdf"
)


processed_folder = (
    project_root
    / "curriculum"
    / "processed"
)


db = SessionLocal()


try:

    ingestion_service = (
        CurriculumIngestionService()
    )

    chunking_service = (
        CurriculumChunkingService()
    )


    for page_number in range(
        start_page,
        end_page + 1
    ):

        print()
        print("=" * 80)
        print(
            f"Processing PDF page "
            f"{page_number}"
        )
        print("=" * 80)


        image_output_path = (
            processed_folder
            / f"page_{page_number}.png"
        )


        page = ingestion_service.process_page(
            db=db,
            document_id=1,
            pdf_path=str(pdf_path),
            page_number=page_number,
            image_output_path=str(
                image_output_path
            ),
            extraction_model="gpt-5.6-luna"
        )


        print(
            f"Saved page ID: {page.id}"
        )

        print(
            f"Page type: {page.page_type}"
        )


        chunks = (
            chunking_service
            .generate_chunks(
                db=db,
                document_id=1,
                page_number=page_number
            )
        )


        print(
            f"Generated chunks: "
            f"{len(chunks)}"
        )


    print()
    print("=" * 80)
    print("PAGE RANGE COMPLETED")
    print("=" * 80)

    print(
        f"Processed pages: "
        f"{start_page} - {end_page}"
    )


finally:

    db.close()