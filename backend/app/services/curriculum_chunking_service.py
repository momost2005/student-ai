import json

from sqlalchemy.orm import Session

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

QUESTION_BASED_SECTION_TYPES = {
    "practice",
    "review",
    "assessment"
}

class CurriculumChunkingService:

    def __init__(self):

        self.repository = (
            CurriculumRepository()
        )


    def generate_chunks(
        self,
        db: Session,
        document_id: int,
        page_number: int
    ):

        page = self.repository.get_page(
            db=db,
            document_id=document_id,
            page_number=page_number
        )

        if not page:
            raise ValueError(
                f"Page {page_number} "
                f"was not found"
            )

        if not page.raw_extracted_content:
            raise ValueError(
                f"Page {page_number} "
                f"has no extracted content"
            )

        extracted_page = json.loads(
            page.raw_extracted_content
        )

        lesson_number = (
            extracted_page.get(
                "lesson_number"
            )
        )

        lesson_title = (
            extracted_page.get(
                "lesson_title"
            )
        )

        sections = extracted_page.get(
            "sections",
            []
        )


        database_sections = {
            section.sequence: section
            for section in page.sections
        }


        chunks = []

        chunk_sequence = 0


        for section_index, section in enumerate(
            sections
        ):

            section_type = section.get(
                "section_type",
                "other"
            )

            section_title = section.get(
                "title"
            )

            section_content = (
                section.get(
                    "content"
                )
                or ""
            ).strip()

            questions = section.get(
                "questions",
                []
            )


            database_section = (
                database_sections.get(
                    section_index
                )
            )

            section_id = (
                database_section.id
                if database_section
                else None
            )


            if (
                questions
                and section_type
                in QUESTION_BASED_SECTION_TYPES
            ):

                for question in questions:

                    question_number = (
                        question.get(
                            "number"
                        )
                    )

                    question_text = (
                        question.get(
                            "text"
                        )
                        or ""
                    ).strip()

                    math_expression = (
                        question.get(
                            "math_expression"
                        )
                        or ""
                    ).strip()


                    content_parts = []


                    if lesson_title:

                        content_parts.append(
                            f"Lesson: "
                            f"{lesson_title}"
                        )


                    if section_title:

                        content_parts.append(
                            f"Section: "
                            f"{section_title}"
                        )


                    if section_content:

                        content_parts.append(
                            f"Instructions: "
                            f"{section_content}"
                        )


                    if question_text:

                        content_parts.append(
                            question_text
                        )


                    if math_expression:

                        content_parts.append(
                            math_expression
                        )


                    chunk_content = "\n\n".join(
                        content_parts
                    )


                    chunks.append(
                        {
                            "section_id":
                                section_id,

                            "chunk_type":
                                f"{section_type}_question",

                            "content":
                                chunk_content,

                            "question_number":
                                question_number,

                            "lesson_number":
                                lesson_number,

                            "lesson_title":
                                lesson_title,

                            "sequence":
                                chunk_sequence
                        }
                    )


                    chunk_sequence += 1


            else:

                if not (
                    section_content
                    or section_title
                    or questions
                ):
                    continue


                content_parts = []


                if lesson_title:

                    content_parts.append(
                        f"Lesson: "
                        f"{lesson_title}"
                    )


                if section_title:

                    content_parts.append(
                        f"Section: "
                        f"{section_title}"
                    )


                if section_content:

                    content_parts.append(
                        section_content
                    )


                for question in questions:

                    question_text = (
                        question.get(
                            "text"
                        )
                        or ""
                    ).strip()

                    math_expression = (
                        question.get(
                            "math_expression"
                        )
                        or ""
                    ).strip()


                    if question_text:

                        content_parts.append(
                            question_text
                        )


                    if math_expression:

                        content_parts.append(
                            math_expression
                        )


                chunk_content = "\n\n".join(
                    content_parts
                )


                chunks.append(
                    {
                        "section_id":
                            section_id,

                        "chunk_type":
                            section_type,

                        "content":
                            chunk_content,

                        "question_number":
                            None,

                        "lesson_number":
                            lesson_number,

                        "lesson_title":
                            lesson_title,

                        "sequence":
                            chunk_sequence
                    }
                )


                chunk_sequence += 1


        return self.repository.replace_chunks(
            db=db,
            page_id=page.id,
            chunks=chunks
        )