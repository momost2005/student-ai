from sqlalchemy.orm import Session

from app.services.curriculum_search_service import (
    CurriculumSearchService
)


class CurriculumPracticeService:

    def __init__(
        self,
        search_service: CurriculumSearchService
    ):

        self.search_service = search_service


    def _clean_question_content(
        self,
        content: str
    ) -> str:

        lines = content.splitlines()

        cleaned_lines = []

        for line in lines:

            stripped = line.strip()

            if stripped.startswith(
                "Lesson:"
            ):
                continue

            if stripped.startswith(
                "Section:"
            ):
                continue

            cleaned_lines.append(
                line
            )

        return "\n".join(
            cleaned_lines
        ).strip()


    def get_question(
        self,
        db: Session,
        curriculum_id: int,
        lesson_number: str,
        topic: str | None = None
    ) -> dict | None:

        query = (
            topic
            or "Practice question from this lesson"
        )

        results = self.search_service.search(
            db=db,
            query=query,
            curriculum_id=curriculum_id,
            lesson_number=lesson_number,
            chunk_types=[
                "practice_question"
            ],
            limit=5
        )

        if not results:
            return None

        selected = results[0]

        display_content = (
            self._clean_question_content(
                selected["content"]
            )
        )

        return {
            "chunk_id":
                selected["chunk_id"],

            "lesson_number":
                lesson_number,

            "lesson_title":
                selected["lesson_title"],

            "question_number":
                selected["question_number"],

            "content":
                display_content,

            "similarity":
                selected["similarity"]
        }