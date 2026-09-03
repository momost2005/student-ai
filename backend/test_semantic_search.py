import sys

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

from app.services.curriculum_search_service import (
    CurriculumSearchService
)


if len(sys.argv) > 1:

    query = " ".join(
        sys.argv[1:]
    )

else:

    query = (
        "How do I simplify a fraction "
        "using the greatest common factor?"
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

    search_service = (
        CurriculumSearchService(
            gateway=gateway,
            repository=curriculum_repository
        )
    )


    results = search_service.search(
        db=db,
        query=query,
        limit=5
    )


    print()
    print("=" * 80)

    print(
        f"QUERY: {query}"
    )

    print("=" * 80)


    for index, result in enumerate(
        results,
        start=1
    ):

        print()
        print(
            "=" * 80
        )

        print(
            f"RESULT {index}"
        )

        print(
            f"Similarity: "
            f"{result['similarity']:.4f}"
        )

        print(
            f"Chunk ID: "
            f"{result['chunk_id']}"
        )

        print(
            f"Type: "
            f"{result['chunk_type']}"
        )

        print(
            f"Lesson: "
            f"{result['lesson_title']}"
        )

        print()

        print(
            result["content"][:1500]
        )


finally:

    db.close()