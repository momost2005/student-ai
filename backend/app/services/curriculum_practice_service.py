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
        topic: str | None = None,
        excluded_question_keys: set[str] | None = None
    ) -> dict | None:

        # -------------------------------------------------
        # 1. Semantic query
        # -------------------------------------------------

        query = (
            topic
            or
            "Practice question from this lesson"
        )


        excluded_question_keys = (
            excluded_question_keys
            or set()
        )


        search_limit = (
            5
            if not excluded_question_keys
            else min(
                100,
                max(
                    20,
                    len(excluded_question_keys) + 10
                )
            )
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
                limit=search_limit
            )
        )


        if not results:

            return None


        # -------------------------------------------------
        # 2. Return the best unused LOGICAL question.
        #
        # Several search results can belong to one group,
        # so exclusion must happen after logical identity
        # resolution rather than by raw chunk ID.
        # -------------------------------------------------

        for selected in results:

            selected_chunk_id = (
                selected["chunk_id"]
            )


            group = (
                self.question_group_repository
                .get_group_for_chunk(
                    db=db,
                    chunk_id=selected_chunk_id
                )
            )


            logical_question_key = (
                f"group:{group.id}"
                if group
                else f"chunk:{selected_chunk_id}"
            )


            if (
                logical_question_key
                in excluded_question_keys
            ):

                continue


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


            display_content = (
                self._clean_standard_question_content(
                    selected["content"]
                )
            )


            return {
                "logical_question_key":
                    logical_question_key,

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


        return None
