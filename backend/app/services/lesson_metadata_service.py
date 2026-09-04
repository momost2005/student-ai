import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.curriculum import (
    CurriculumPage
)


class LessonMetadataService:

    def propagate_range(
        self,
        db: Session,
        document_id: int,
        start_page: int,
        end_page: int
    ) -> int:

        statement = (
            select(CurriculumPage)
            .where(
                CurriculumPage.document_id
                == document_id,

                CurriculumPage.page_number
                >= start_page,

                CurriculumPage.page_number
                <= end_page
            )
            .order_by(
                CurriculumPage.page_number
            )
        )

        pages = list(
            db.execute(
                statement
            ).scalars().all()
        )

        if not pages:
            raise ValueError(
                "No curriculum pages found "
                "in the requested range"
            )


        current_lesson_number = None
        current_lesson_title = None

        updated_count = 0


        for page in pages:

            extracted_data = {}

            if page.raw_extracted_content:

                extracted_data = json.loads(
                    page.raw_extracted_content
                )


            extracted_lesson_number = (
                extracted_data.get(
                    "lesson_number"
                )
            )

            extracted_lesson_title = (
                extracted_data.get(
                    "lesson_title"
                )
            )


            if extracted_lesson_number:

                current_lesson_number = (
                    extracted_lesson_number
                )


            if extracted_lesson_title:

                current_lesson_title = (
                    extracted_lesson_title
                )


            if current_lesson_number:

                page.lesson_number = (
                    current_lesson_number
                )


            if current_lesson_title:

                page.lesson_title = (
                    current_lesson_title
                )


            updated_count += 1


        db.commit()

        return updated_count