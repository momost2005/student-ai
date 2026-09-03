from sqlalchemy.orm import Session

from app.embeddings.gateway import (
    EmbeddingGateway
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)


class CurriculumSearchService:

    def __init__(
        self,
        gateway: EmbeddingGateway,
        repository: CurriculumRepository
    ):

        self.gateway = gateway

        self.repository = repository


    def search(
        self,
        db: Session,
        query: str,
        limit: int = 5
    ) -> list[dict]:

        (
            provider_name,
            model_name,
            dimensions,
            query_embedding
        ) = self.gateway.embed(
            db=db,
            text=query
        )

        rows = (
            self.repository
            .search_similar_chunks(
                db=db,
                query_embedding=query_embedding,
                provider_name=provider_name,
                model_name=model_name,
                dimensions=dimensions,
                limit=limit
            )
        )

        results = []

        for chunk, distance in rows:

            similarity = (
                1.0 - float(distance)
            )

            results.append(
                {
                    "chunk_id":
                        chunk.id,

                    "chunk_type":
                        chunk.chunk_type,

                    "lesson_number":
                        chunk.lesson_number,

                    "lesson_title":
                        chunk.lesson_title,

                    "question_number":
                        chunk.question_number,

                    "similarity":
                        similarity,

                    "content":
                        chunk.content
                }
            )

        return results