from app.embeddings.base import (
    EmbeddingProvider
)

from app.embeddings.providers.openai_provider import (
    OpenAIEmbeddingProvider
)


class EmbeddingProviderRegistry:

    def __init__(self):

        self.providers: dict[
            str,
            EmbeddingProvider
        ] = {
            "openai": OpenAIEmbeddingProvider()
        }


    def get(
        self,
        provider_name: str
    ) -> EmbeddingProvider:

        provider = self.providers.get(
            provider_name
        )

        if not provider:

            raise ValueError(
                f"Embedding provider "
                f"'{provider_name}' "
                f"is not registered"
            )

        return provider