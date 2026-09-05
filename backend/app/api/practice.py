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
from app.embeddings.gateway import EmbeddingGateway
from app.embeddings.registry import EmbeddingProviderRegistry
from app.embeddings.settings import EmbeddingSettings
from app.repositories.curriculum_repository import (
    CurriculumRepository
)
from app.repositories.question_group_repository import (
    QuestionGroupRepository
)
from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)
from app.schemas.practice import (
    PracticeQuestionOption,
    PracticeQuestionResponse
)
from app.services.curriculum_practice_service import (
    CurriculumPracticeService
)
from app.services.curriculum_search_service import (
    CurriculumSearchService
)
from app.services.retrieval_settings import RetrievalSettings


router = APIRouter(
    prefix="/api/practice",
    tags=["practice"]
)


@lru_cache(maxsize=1)
def get_practice_service() -> CurriculumPracticeService:
    settings_repository = SystemSettingsRepository()
    embedding_settings = EmbeddingSettings(
        repository=settings_repository
    )
    embedding_gateway = EmbeddingGateway(
        settings=embedding_settings,
        registry=EmbeddingProviderRegistry()
    )
    search_service = CurriculumSearchService(
        gateway=embedding_gateway,
        repository=CurriculumRepository(),
        retrieval_settings=RetrievalSettings(
            repository=settings_repository
        )
    )

    return CurriculumPracticeService(
        search_service=search_service,
        question_group_repository=QuestionGroupRepository()
    )


@router.get(
    "/question",
    response_model=PracticeQuestionResponse,
    response_model_exclude_none=True
)
def get_practice_question(
    curriculum_id: Annotated[int, Query(gt=0)],
    lesson_number: Annotated[
        str,
        Query(min_length=1, max_length=50)
    ],
    topic: Annotated[
        str | None,
        Query(min_length=1, max_length=500)
    ] = None,
    db: Session = Depends(get_db),
    service: CurriculumPracticeService = Depends(
        get_practice_service
    )
) -> PracticeQuestionResponse:
    lesson_number = lesson_number.strip()

    if not lesson_number:
        raise HTTPException(
            status_code=422,
            detail="lesson_number must not be blank."
        )

    normalized_topic = topic.strip() if topic else None

    if topic is not None and not normalized_topic:
        raise HTTPException(
            status_code=422,
            detail="topic must not be blank."
        )

    question = service.get_question(
        db=db,
        curriculum_id=curriculum_id,
        lesson_number=lesson_number,
        topic=normalized_topic
    )

    if question is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No practice question was found for the "
                "requested curriculum and lesson."
            )
        )

    prompt = question.get("content")

    if not isinstance(prompt, str) or not prompt.strip():
        raise HTTPException(
            status_code=500,
            detail="The selected practice question has no prompt."
        )

    options = [
        PracticeQuestionOption(
            id=option["sequence"],
            text=option["content"]
        )
        for option in question.get("options", [])
    ]

    return PracticeQuestionResponse(
        logical_question_key=question["logical_question_key"],
        question_type=question["question_type"],
        lesson_number=question["lesson_number"],
        question_number=question.get("question_number"),
        prompt=prompt,
        options=options
    )
