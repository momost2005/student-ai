import sys

from app.ai.gateway import (
    AIGateway
)

from app.ai.registry import (
    AIProviderRegistry
)

from app.ai.settings import (
    AISettings
)

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

from app.services.curriculum_tutor_service import (
    CurriculumTutorService
)

from app.services.retrieval_settings import (
    RetrievalSettings
)


if len(sys.argv) > 1:

    question = " ".join(
        sys.argv[1:]
    )

else:

    question = (
        "How do I simplify a fraction "
        "using the greatest common factor?"
    )


db = SessionLocal()


try:

    system_repository = (
        SystemSettingsRepository()
    )

    retrieval_settings = (
        RetrievalSettings(
            system_repository
        )
    )

    # -------------------------
    # Embedding side
    # -------------------------

    embedding_settings = (
        EmbeddingSettings(
            system_repository
        )
    )

    embedding_registry = (
        EmbeddingProviderRegistry()
    )

    embedding_gateway = (
        EmbeddingGateway(
            settings=embedding_settings,
            registry=embedding_registry
        )
    )


    curriculum_repository = (
        CurriculumRepository()
    )


    search_service = (
        CurriculumSearchService(
            gateway=embedding_gateway,
            repository=curriculum_repository,
            retrieval_settings=retrieval_settings
        )
    )


    # -------------------------
    # Chat AI side
    # -------------------------

    ai_settings = AISettings(
        system_repository
    )

    ai_registry = (
        AIProviderRegistry()
    )

    ai_gateway = AIGateway(
        settings=ai_settings,
        registry=ai_registry
    )


    # -------------------------
    # Tutor
    # -------------------------

    tutor = CurriculumTutorService(
        search_service=search_service,
        ai_gateway=ai_gateway
    )


    result = tutor.answer(
        db=db,
        question=question,
        top_k=4
    )


    print()
    print("=" * 80)
    print("STUDENT QUESTION")
    print("=" * 80)

    print(question)


    print()
    print("=" * 80)
    print("TUTOR ANSWER")
    print("=" * 80)

    print(
        result["answer"]
    )


    print()
    print("=" * 80)
    print("RETRIEVED SOURCES")
    print("=" * 80)


    for source in result["sources"]:

        print()

        print(
            f"Chunk: "
            f"{source['chunk_id']}"
        )

        print(
            f"Type: "
            f"{source['chunk_type']}"
        )

        print(
            f"Lesson: "
            f"{source['lesson_title']}"
        )

        print(
            f"Similarity: "
            f"{source['similarity']:.4f}"
        )


finally:

    db.close()