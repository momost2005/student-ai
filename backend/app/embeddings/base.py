from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):

    def embed(
        self,
        text: str,
        model: str,
        dimensions: int | None = None
    ) -> list[float]:

        embeddings = self.embed_many(
            texts=[text],
            model=model,
            dimensions=dimensions
        )

        return embeddings[0]


    @abstractmethod
    def embed_many(
        self,
        texts: list[str],
        model: str,
        dimensions: int | None = None
    ) -> list[list[float]]:
        pass