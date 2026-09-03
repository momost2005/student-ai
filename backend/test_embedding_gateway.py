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

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)


db = SessionLocal()


try:

    repository = (
        SystemSettingsRepository()
    )

    settings = EmbeddingSettings(
        repository
    )

    registry = (
        EmbeddingProviderRegistry()
    )

    gateway = EmbeddingGateway(
        settings=settings,
        registry=registry
    )


    provider_name, \
    model_name, \
    dimensions, \
    embedding = gateway.embed(
        db=db,
        text=(
            "Find the greatest common "
            "factor of 30 and 42."
        )
    )


    print(
        f"Provider: "
        f"{provider_name}"
    )

    print(
        f"Model: "
        f"{model_name}"
    )

    print(
        f"Dimensions: "
        f"{dimensions}"
    )

    print(
        f"First 5 values: "
        f"{embedding[:5]}"
    )


finally:

    db.close()