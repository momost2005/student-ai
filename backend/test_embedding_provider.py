from app.embeddings.providers.openai_provider import (
    OpenAIEmbeddingProvider
)


provider = OpenAIEmbeddingProvider()


text = """
Find the greatest common factor of
30 and 42 using prime factorization.
"""


embedding = provider.embed(
    text=text,
    model="text-embedding-3-small"
)


print(
    f"Embedding dimensions: "
    f"{len(embedding)}"
)


print(
    "First 5 values:"
)


for value in embedding[:5]:
    print(value)