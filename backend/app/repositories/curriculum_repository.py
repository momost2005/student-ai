from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.curriculum import (
    CurriculumDocument,
    CurriculumPage
)

from app.models.curriculum import (
    CurriculumDocument,
    CurriculumPage,
    CurriculumSection
)

from app.models.curriculum import (
    CurriculumChunk,
    CurriculumDocument,
    CurriculumPage,
    CurriculumSection
)

class CurriculumRepository:

    def replace_sections(
        self,
        db: Session,
        page: CurriculumPage,
        sections
    ) -> None:

        # Remove existing sections for this page
        page.sections.clear()

        db.flush()

        for index, section in enumerate(sections):

            content_parts = []

            if section.content:
                content_parts.append(
                    section.content
                )

            for question in section.questions:

                question_text = question.text

                if question.math_expression:
                    question_text += (
                        "\n"
                        + question.math_expression
                    )

                content_parts.append(
                    question_text
                )

            content = "\n\n".join(
                content_parts
            ).strip()

            db_section = CurriculumSection(
                page_id=page.id,
                section_type=section.section_type,
                title=section.title,
                content=content,
                sequence=index
            )

            db.add(db_section)

        db.commit()

    def get_document(
        self,
        db: Session,
        document_id: int
    ) -> CurriculumDocument | None:

        statement = select(
            CurriculumDocument
        ).where(
            CurriculumDocument.id == document_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()


    def save_page(
        self,
        db: Session,
        document_id: int,
        page_number: int,
        page_type: str | None,
        raw_extracted_content: str
    ) -> CurriculumPage:


        statement = select(
            CurriculumPage
        ).where(
            CurriculumPage.document_id == document_id,
            CurriculumPage.page_number == page_number
        )

        page = db.execute(
            statement
        ).scalar_one_or_none()

        if page:
            page.page_type = page_type
            page.raw_extracted_content = (
                raw_extracted_content
            )

        else:
            page = CurriculumPage(
                document_id=document_id,
                page_number=page_number,
                page_type=page_type,
                raw_extracted_content=(
                    raw_extracted_content
                )
            )

            db.add(page)

        db.commit()
        db.refresh(page)

        return page

    def get_page(
        self,
        db: Session,
        document_id: int,
        page_number: int
    ) -> CurriculumPage | None:

        statement = select(
            CurriculumPage
        ).where(
            CurriculumPage.document_id == document_id,
            CurriculumPage.page_number == page_number
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    def replace_chunks(
        self,
        db: Session,
        page_id: int,
        chunks: list[dict]
    ) -> list[CurriculumChunk]:

        db.execute(
            delete(
                CurriculumChunk
            ).where(
                CurriculumChunk.page_id == page_id
            )
        )

        created_chunks = []

        for chunk_data in chunks:

            chunk = CurriculumChunk(
                page_id=page_id,
                section_id=chunk_data[
                    "section_id"
                ],
                chunk_type=chunk_data[
                    "chunk_type"
                ],
                content=chunk_data[
                    "content"
                ],
                question_number=chunk_data[
                    "question_number"
                ],
                lesson_number=chunk_data[
                    "lesson_number"
                ],
                lesson_title=chunk_data[
                    "lesson_title"
                ],
                sequence=chunk_data[
                    "sequence"
                ]
            )

            db.add(chunk)

            created_chunks.append(
                chunk
            )

        db.commit()

        for chunk in created_chunks:
            db.refresh(chunk)

        return created_chunks        