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

from app.services.curriculum_practice_service import (
    CurriculumPracticeService
)

from app.services.curriculum_search_service import (
    CurriculumSearchService
)

from app.services.retrieval_settings import (
    RetrievalSettings
)


db = SessionLocal()


try:

    system_repository = (
        SystemSettingsRepository()
    )

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

    retrieval_settings = (
        RetrievalSettings(
            system_repository
        )
    )

    search_service = (
        CurriculumSearchService(
            gateway=embedding_gateway,
            repository=curriculum_repository,
            retrieval_settings=retrieval_settings
        )
    )

    practice_service = (
        CurriculumPracticeService(
            search_service=search_service
        )
    )

    question = (
        practice_service.get_question(
            db=db,
            curriculum_id=1,
            lesson_number="3",
            topic="greatest common factors"
        )
    )


    if not question:

        print(
            "No suitable practice question found."
        )

    else:

        print()
        print("=" * 80)
        print("PRACTICE QUESTION")
        print("=" * 80)

        print(
            f"Chunk ID: "
            f"{question['chunk_id']}"
        )

        print(
            f"Lesson: "
            f"{question['lesson_title']}"
        )

        print(
            f"Question Number: "
            f"{question['question_number']}"
        )

        print()

        print(
            question["content"]
        )


finally:

    db.close()