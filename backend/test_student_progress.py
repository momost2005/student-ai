from app.db.database import (
    SessionLocal
)

from app.repositories.curriculum_repository import (
    CurriculumRepository
)

from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)

from app.services.logical_question_service import (
    LogicalQuestionService
)

from app.services.mastery_settings import (
    MasterySettings
)

from app.services.student_progress_service import (
    StudentProgressService
)


db = SessionLocal()


try:

    curriculum_repository = (
        CurriculumRepository()
    )


    system_repository = (
        SystemSettingsRepository()
    )


    mastery_settings = (
        MasterySettings(
            repository=system_repository
        )
    )


    logical_question_service = (
        LogicalQuestionService()
    )


    progress_service = (
        StudentProgressService(
            repository=(
                curriculum_repository
            ),
            mastery_settings=(
                mastery_settings
            ),
            logical_question_service=(
                logical_question_service
            )
        )
    )


    progress = (
        progress_service
        .get_lesson_progress(
            db=db,
            student_id=1,
            curriculum_id=1,
            lesson_number="3"
        )
    )


    print()
    print("=" * 80)
    print("LESSON PROGRESS")
    print("=" * 80)


    for key, value in progress.items():

        print(
            f"{key}: {value}"
        )


finally:

    db.close()