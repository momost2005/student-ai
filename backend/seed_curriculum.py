from app.db.database import SessionLocal
from app.models.curriculum import (
    Curriculum,
    CurriculumDocument
)


db = SessionLocal()

try:

    curriculum = Curriculum(
        country="Egypt",
        education_system="Government",
        grade="Grade 6",
        subject="Mathematics",
        term="Term 1",
        academic_year="2026/2027"
    )

    db.add(curriculum)

    db.flush()

    document = CurriculumDocument(
        curriculum_id=curriculum.id,
        file_name="grade6_math_term1.pdf",
        title="Grade 6 Mathematics - Term 1",
        page_count=258,
        processing_status="testing"
    )

    db.add(document)

    db.commit()

    print(
        f"Curriculum ID: {curriculum.id}"
    )

    print(
        f"Document ID: {document.id}"
    )

finally:
    db.close()