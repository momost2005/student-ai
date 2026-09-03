from sqlalchemy.orm import Session

from app.embeddings.registry import (
    EmbeddingProviderRegistry
)

from app.embeddings.settings import (
    EmbeddingSettings
)


class EmbeddingGateway:

    def __init__(
        self,
        settings: EmbeddingSettings,
        registry: EmbeddingProviderRegistry
    ):

        self.settings = settings

        self.registry = registry


    def embed(
        self,
        db: Session,
        text: str
    ) -> tuple[
        str,
        str,
        int,
        list[float]
    ]:

        provider_name = (
            self.settings.get_active_provider(
                db
            )
        )

        model_name = (
            self.settings.get_active_model(
                db
            )
        )

        configured_dimensions = (
            self.settings.get_dimensions(
                db
            )
        )


        provider = self.registry.get(
            provider_name
        )


        embedding = provider.embed(
            text=text,
            model=model_name,
            dimensions=configured_dimensions
        )


        actual_dimensions = len(
            embedding
        )


        return (
            provider_name,
            model_name,
            actual_dimensions,
            embedding
        )