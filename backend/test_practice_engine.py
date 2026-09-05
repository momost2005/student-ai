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

from app.repositories.question_group_repository import (
    QuestionGroupRepository
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


# -------------------------------------------------
# Optional topic from command line
# -------------------------------------------------

if len(sys.argv) > 1:

    topic = " ".join(
        sys.argv[1:]
    )

else:

    topic = (
        "greatest common factors"
    )


db = SessionLocal()


try:

    # -------------------------------------------------
    # Settings
    # -------------------------------------------------

    system_repository = (
        SystemSettingsRepository()
    )


    embedding_settings = (
        EmbeddingSettings(
            system_repository
        )
    )


    retrieval_settings = (
        RetrievalSettings(
            system_repository
        )
    )


    # -------------------------------------------------
    # Embedding infrastructure
    # -------------------------------------------------

    embedding_registry = (
        EmbeddingProviderRegistry()
    )


    embedding_gateway = (
        EmbeddingGateway(
            settings=embedding_settings,
            registry=embedding_registry
        )
    )


    # -------------------------------------------------
    # Repositories
    # -------------------------------------------------

    curriculum_repository = (
        CurriculumRepository()
    )


    question_group_repository = (
        QuestionGroupRepository()
    )


    # -------------------------------------------------
    # Search
    # -------------------------------------------------

    search_service = (
        CurriculumSearchService(
            gateway=embedding_gateway,
            repository=curriculum_repository,
            retrieval_settings=(
                retrieval_settings
            )
        )
    )


    # -------------------------------------------------
    # Practice engine
    # -------------------------------------------------

    practice_service = (
        CurriculumPracticeService(
            search_service=(
                search_service
            ),
            question_group_repository=(
                question_group_repository
            )
        )
    )


    question = (
        practice_service.get_question(
            db=db,
            curriculum_id=1,
            lesson_number="3",
            topic=topic
        )
    )


    # -------------------------------------------------
    # Output
    # -------------------------------------------------

    print()
    print("=" * 80)
    print("PRACTICE QUESTION")
    print("=" * 80)


    print(
        f"Topic: {topic}"
    )


    if not question:

        print()

        print(
            "No suitable practice question found."
        )


    else:

        print()

        print(
            f"Logical Question Key: "
            f"{question['logical_question_key']}"
        )

        print(
            f"Question Type: "
            f"{question['question_type']}"
        )

        print(
            f"Selected Chunk ID: "
            f"{question['selected_chunk_id']}"
        )

        print(
            f"Question Group ID: "
            f"{question['question_group_id']}"
        )

        print(
            f"Question Number: "
            f"{question['question_number']}"
        )


        print()
        print("--- Question ---")
        print()


        print(
            question["content"]
        )


        options = (
            question.get(
                "options",
                []
            )
        )


        if options:

            print()
            print("--- Options ---")


            for option in options:

                print()

                print(
                    f"{option['sequence']}. "
                    f"{option['content']}"
                )


        sub_questions = (
            question.get(
                "sub_questions",
                []
            )
        )


        if sub_questions:

            print()
            print(
                "--- Sub Questions ---"
            )


            for item in sub_questions:

                print()

                print(
                    f"{item['sequence']}. "
                    f"{item['content']}"
                )


finally:

    db.close()