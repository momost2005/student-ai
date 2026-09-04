from sqlalchemy.orm import Session

from app.ai.gateway import AIGateway

from app.services.curriculum_search_service import (
    CurriculumSearchService
)


class CurriculumTutorService:

    def __init__(
        self,
        search_service: CurriculumSearchService,
        ai_gateway: AIGateway
    ):

        self.search_service = search_service
        self.ai_gateway = ai_gateway


    def answer(
        self,
        db: Session,
        curriculum_id: int,
        question: str,
        lesson_number: str | None = None,
        chunk_types: list[str] | None = None,
        top_k: int = 4
    ) -> dict:

        # -------------------------------------------------
        # 1. Retrieve relevant curriculum chunks
        # -------------------------------------------------

        search_results = (
            self.search_service.search(
                db=db,
                query=question,
                curriculum_id=curriculum_id,
                lesson_number=lesson_number,
                chunk_types=chunk_types,
                limit=top_k
            )
        )


        # -------------------------------------------------
        # 2. Stop if no relevant curriculum content exists
        # -------------------------------------------------

        if not search_results:

            return {
                "answer": (
                    "I could not find relevant "
                    "curriculum content."
                ),
                "sources": []
            }


        # -------------------------------------------------
        # 3. Build curriculum context
        # -------------------------------------------------

        context_parts = []

        for index, result in enumerate(
            search_results,
            start=1
        ):

            context_parts.append(
                f"""
SOURCE {index}

Chunk Type:
{result["chunk_type"]}

Lesson:
{result["lesson_title"]}

Similarity:
{result["similarity"]:.4f}

Content:
{result["content"]}
"""
            )


        curriculum_context = "\n\n".join(
            context_parts
        )


        # -------------------------------------------------
        # 4. Add lesson awareness
        # -------------------------------------------------

        lesson_context = ""

        if lesson_number:

            lesson_context = (
                f"The student is currently "
                f"studying Lesson "
                f"{lesson_number}."
            )


        # -------------------------------------------------
        # 5. Build grounded tutor prompt
        # -------------------------------------------------

        prompt = f"""
You are an AI mathematics tutor.

{lesson_context}

Your job is to answer the student's question
using the supplied curriculum context.

STUDENT QUESTION:
{question}

CURRICULUM CONTEXT:
{curriculum_context}

IMPORTANT RULES:

1. Base your answer primarily on the curriculum
   context supplied above.

2. Do not invent curriculum facts that are not
   supported by the supplied context.

3. Explain the concept clearly and at the level
   of the student.

4. Show mathematical steps when they help
   understanding.

5. Do not mention embeddings, vectors,
   databases, chunks, retrieval, or internal
   system architecture.

6. Do not tell the student that you are reading
   SOURCE 1, SOURCE 2, etc.

7. If the supplied curriculum context is not
   sufficient to answer the question reliably,
   say that the available lesson material does
   not contain enough information.

8. Do not introduce unrelated topics.

Answer the student directly.
"""


        # -------------------------------------------------
        # 6. Generate grounded answer
        # -------------------------------------------------

        (
            provider_name,
            model_name,
            answer
        ) = self.ai_gateway.generate(
            db=db,
            prompt=prompt
        )


        # -------------------------------------------------
        # 7. Return sources for debugging / UI
        # -------------------------------------------------

        sources = []

        for result in search_results:

            sources.append(
                {
                    "chunk_id":
                        result["chunk_id"],

                    "chunk_type":
                        result["chunk_type"],

                    "lesson_number":
                        result["lesson_number"],

                    "lesson_title":
                        result["lesson_title"],

                    "similarity":
                        result["similarity"]
                }
            )


        return {
            "answer": answer,
            "provider": provider_name,
            "model": model_name,
            "sources": sources
        }