from pathlib import Path

from app.db.database import SessionLocal

from app.services.curriculum_ingestion_service import (
    CurriculumIngestionService
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


image_output_path = (
    project_root
    / "curriculum"
    / "processed"
    / "page_5.png"
)


db = SessionLocal()

try:

    service = CurriculumIngestionService()

    page = service.process_page(
        db=db,
        document_id=1,
        pdf_path=str(pdf_path),
        page_number=5,
        image_output_path=str(
            image_output_path
        ),
        extraction_model="gpt-5.6-luna"
    )

    print(
        f"Saved page ID: {page.id}"
    )

    print(
        f"Page number: {page.page_number}"
    )

    print(
        f"Page type: {page.page_type}"
    )

finally:
    db.close()