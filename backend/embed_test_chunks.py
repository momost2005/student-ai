from app.db.database import (
    SessionLocal
)

from app.embeddings.gateway import (
    EmbeddingGateway
)

from app.embeddings.registry import (
    EmbeddingProviderRegistry
)

from app.embeddings.settings import (
    EmbeddingSettings
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

from app.services.curriculum_embedding_service import (
    CurriculumEmbeddingService
)


db = SessionLocal()


try:

    system_settings_repository = (
        SystemSettingsRepository()
    )

    embedding_settings = (
        EmbeddingSettings(
            system_settings_repository
        )
    )

    registry = (
        EmbeddingProviderRegistry()
    )

    gateway = EmbeddingGateway(
        settings=embedding_settings,
        registry=registry
    )

    curriculum_repository = (
        CurriculumRepository()
    )

    service = CurriculumEmbeddingService(
        gateway=gateway,
        repository=curriculum_repository
    )

    count = service.embed_pending_chunks(
        db=db
    )

    print(
        f"Embedded chunks: {count}"
    )


finally:

    db.close()