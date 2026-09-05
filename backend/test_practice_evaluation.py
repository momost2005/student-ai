from app.ai.gateway import AIGateway
from app.ai.registry import AIProviderRegistry
from app.ai.settings import AISettings

from app.db.database import SessionLocal

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

from app.services.practice_evaluation_service import (
    PracticeEvaluationService
)


db = SessionLocal()


try:

    system_repository = (
        SystemSettingsRepository()
    )

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

    curriculum_repository = (
        CurriculumRepository()
    )

    evaluation_service = (
        PracticeEvaluationService(
            repository=curriculum_repository,
            ai_gateway=ai_gateway
        )
    )


    student_answer = """
GCF = 15
"""


    result = evaluation_service.evaluate(
        db=db,

        student_id=1,

        curriculum_id=1,

        chunk_id=160,

        student_answer=student_answer
    )


    print()
    print("=" * 80)
    print("EVALUATION")
    print("=" * 80)

    print(result)


finally:

    db.close()