import os

from dotenv import load_dotenv
from openai import OpenAI

from app.embeddings.base import EmbeddingProvider


load_dotenv()


class OpenAIEmbeddingProvider(
    EmbeddingProvider
):

    def __init__(self):

        api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY is not configured"
            )

        self.client = OpenAI(
            api_key=api_key
        )


    def embed_many(
        self,
        texts: list[str],
        model: str,
        dimensions: int | None = None
    ) -> list[list[float]]:

        if not texts:
            return []

        request = {
            "model": model,
            "input": texts,
            "encoding_format": "float"
        }

        if dimensions is not None:
            request["dimensions"] = dimensions

        response = (
            self.client.embeddings.create(
                **request
            )
        )

        return [
            item.embedding
            for item in response.data
        ]