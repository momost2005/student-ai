from sqlalchemy.orm import Session

from app.embeddings.gateway import (
    EmbeddingGateway
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)


class CurriculumEmbeddingService:

    def __init__(
        self,
        gateway: EmbeddingGateway,
        repository: CurriculumRepository
    ):

        self.gateway = gateway
        self.repository = repository


    def embed_pending_chunks(
        self,
        db: Session
    ) -> int:

        chunks = (
            self.repository
            .get_chunks_without_embeddings(
                db
            )
        )

        if not chunks:
            return 0

        texts = [
            chunk.content
            for chunk in chunks
        ]

        (
            provider_name,
            model_name,
            dimensions,
            embeddings
        ) = self.gateway.embed_many(
            db=db,
            texts=texts
        )

        self.repository.save_chunk_embeddings(
            db=db,
            chunks=chunks,
            embeddings=embeddings,
            provider_name=provider_name,
            model_name=model_name,
            dimensions=dimensions
        )

        return len(chunks)