from sqlalchemy.orm import Session

from app.repositories.question_group_repository import (
    QuestionGroupRepository
)

from app.services.curriculum_search_service import (
    CurriculumSearchService
)


class CurriculumPracticeService:

    def __init__(
        self,
        search_service: CurriculumSearchService,
        question_group_repository: QuestionGroupRepository
    ):

        self.search_service = search_service

        self.question_group_repository = (
            question_group_repository
        )


    def _clean_standard_question_content(
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


    def _clean_group_member_content(
        self,
        content: str,
        instructions: str | None
    ) -> str:

        lines = content.splitlines()

        cleaned_lines = []


        for line in lines:

            stripped = line.strip()


            if not stripped:
                continue


            if stripped.startswith(
                "Lesson:"
            ):
                continue


            if stripped.startswith(
                "Section:"
            ):
                continue


            if stripped.startswith(
                "Instructions:"
            ):
                continue


            if (
                instructions
                and
                stripped == instructions.strip()
            ):
                continue


            cleaned_lines.append(
                stripped
            )


        return "\n".join(
            cleaned_lines
        ).strip()


    def _build_group_question(
        self,
        db: Session,
        group,
        selected_chunk_id: int,
        similarity: float
    ) -> dict:

        rows = (
            self.question_group_repository
            .get_group_chunks(
                db=db,
                question_group_id=group.id
            )
        )


        options = []

        sub_questions = []


        for (
            mapping,
            chunk
        ) in rows:

            member_content = (
                self._clean_group_member_content(
                    content=chunk.content,
                    instructions=group.instructions
                )
            )


            member = {
                "chunk_id":
                    chunk.id,

                "sequence":
                    mapping.sequence,

                "content":
                    member_content
            }


            if mapping.role == "option":

                options.append(
                    member
                )


            elif (
                mapping.role
                == "sub_question"
            ):

                sub_questions.append(
                    member
                )


        return {
            "logical_question_key":
                f"group:{group.id}",

            "question_group_id":
                group.id,

            "selected_chunk_id":
                selected_chunk_id,

            "question_type":
                group.question_type,

            "lesson_number":
                group.lesson_number,

            "question_number":
                group.question_number,

            "instructions":
                group.instructions,

            "content":
                group.instructions,

            "options":
                options,

            "sub_questions":
                sub_questions,

            "similarity":
                similarity
        }


    def get_question(
        self,
        db: Session,
        curriculum_id: int,
        lesson_number: str,
        topic: str | None = None
    ) -> dict | None:

        # -------------------------------------------------
        # 1. Semantic query
        # -------------------------------------------------

        query = (
            topic
            or
            "Practice question from this lesson"
        )


        results = (
            self.search_service.search(
                db=db,
                query=query,
                curriculum_id=curriculum_id,
                lesson_number=lesson_number,
                chunk_types=[
                    "practice_question"
                ],
                limit=5
            )
        )


        if not results:

            return None


        # -------------------------------------------------
        # 2. Take best semantic result
        # -------------------------------------------------

        selected = results[0]


        selected_chunk_id = (
            selected["chunk_id"]
        )


        # -------------------------------------------------
        # 3. Determine whether this chunk belongs to a
        #    logical question group.
        # -------------------------------------------------

        group = (
            self.question_group_repository
            .get_group_for_chunk(
                db=db,
                chunk_id=selected_chunk_id
            )
        )


        # -------------------------------------------------
        # 4. Grouped logical question
        # -------------------------------------------------

        if group:

            return (
                self._build_group_question(
                    db=db,
                    group=group,
                    selected_chunk_id=(
                        selected_chunk_id
                    ),
                    similarity=(
                        selected["similarity"]
                    )
                )
            )


        # -------------------------------------------------
        # 5. Standard ungrouped question
        # -------------------------------------------------

        display_content = (
            self._clean_standard_question_content(
                selected["content"]
            )
        )


        return {
            "logical_question_key":
                f"chunk:{selected_chunk_id}",

            "question_group_id":
                None,

            "selected_chunk_id":
                selected_chunk_id,

            "question_type":
                "standard",

            "lesson_number":
                selected["lesson_number"],

            "lesson_title":
                selected["lesson_title"],

            "question_number":
                selected["question_number"],

            "instructions":
                None,

            "content":
                display_content,

            "options":
                [],

            "sub_questions":
                [],

            "similarity":
                selected["similarity"]
        }