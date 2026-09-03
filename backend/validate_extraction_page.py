import sys
from pathlib import Path

from app.db.database import SessionLocal
from app.services.curriculum_ingestion_service import (
    CurriculumIngestionService
)


if len(sys.argv) < 2:
    print("Usage:")
    print("python validate_extraction_page.py <page_number>")
    sys.exit(1)


page_number = int(sys.argv[1])


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
    / f"page_{page_number}.png"
)


db = SessionLocal()

try:

    service = CurriculumIngestionService()

    page = service.process_page(
        db=db,
        document_id=1,
        pdf_path=str(pdf_path),
        page_number=page_number,
        image_output_path=str(image_output_path),
        extraction_model="gpt-5.6-luna"
    )

    print()
    print("=" * 80)
    print("EXTRACTION RESULT")
    print("=" * 80)

    print(f"Page ID: {page.id}")
    print(f"PDF Page: {page.page_number}")
    print(f"Page Type: {page.page_type}")

    print()
    print("=" * 80)
    print("SECTIONS")
    print("=" * 80)

    for section in page.sections:

        print()
        print("-" * 80)

        print(
            f"Section Type: "
            f"{section.section_type}"
        )

        print(
            f"Title: "
            f"{section.title}"
        )

        print()

        print(
            section.content[:1500]
        )

finally:

    db.close()