from functools import lru_cache
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.curriculum_repository import (
    CurriculumRepository
)
from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)
from app.schemas.progress import (
    ConceptProgressResponse,
    LessonProgressResponse
)
from app.services.concept_progress_settings import (
    ConceptProgressSettings
)
from app.services.logical_question_service import (
    LogicalQuestionService
)
from app.services.mastery_settings import MasterySettings
from app.services.student_concept_progress_service import (
    StudentConceptProgressService
)
from app.services.student_progress_service import (
    StudentProgressService
)


router = APIRouter(
    prefix="/api/progress",
    tags=["progress"]
)


@lru_cache(maxsize=1)
def get_student_progress_service() -> StudentProgressService:
    return StudentProgressService(
        repository=CurriculumRepository(),
        mastery_settings=MasterySettings(
            repository=SystemSettingsRepository()
        ),
        logical_question_service=LogicalQuestionService()
    )


@lru_cache(maxsize=1)
def get_student_concept_progress_service(
) -> StudentConceptProgressService:
    return StudentConceptProgressService(
        repository=CurriculumRepository(),
        settings=ConceptProgressSettings(
            repository=SystemSettingsRepository()
        ),
        logical_question_service=LogicalQuestionService()
    )


def _normalize_lesson_number(lesson_number: str) -> str:
    normalized = lesson_number.strip()

    if not normalized:
        raise HTTPException(
            status_code=422,
            detail="lesson_number must not be blank."
        )

    return normalized


@router.get(
    "/lesson",
    response_model=LessonProgressResponse
)
def get_lesson_progress(
    student_id: Annotated[int, Query(gt=0)],
    curriculum_id: Annotated[int, Query(gt=0)],
    lesson_number: Annotated[
        str,
        Query(min_length=1, max_length=50)
    ],
    db: Session = Depends(get_db),
    service: StudentProgressService = Depends(
        get_student_progress_service
    )
) -> dict:
    return service.get_lesson_progress(
        db=db,
        student_id=student_id,
        curriculum_id=curriculum_id,
        lesson_number=_normalize_lesson_number(
            lesson_number
        )
    )


@router.get(
    "/concepts",
    response_model=list[ConceptProgressResponse]
)
def get_concept_progress(
    student_id: Annotated[int, Query(gt=0)],
    curriculum_id: Annotated[int, Query(gt=0)],
    lesson_number: Annotated[
        str,
        Query(min_length=1, max_length=50)
    ],
    db: Session = Depends(get_db),
    service: StudentConceptProgressService = Depends(
        get_student_concept_progress_service
    )
) -> list[dict]:
    return service.get_lesson_concept_progress(
        db=db,
        student_id=student_id,
        curriculum_id=curriculum_id,
        lesson_number=_normalize_lesson_number(
            lesson_number
        )
    )
