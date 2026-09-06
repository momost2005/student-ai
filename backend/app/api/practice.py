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
from app.ai.gateway import AIGateway
from app.ai.registry import AIProviderRegistry
from app.ai.settings import AISettings
from app.embeddings.gateway import EmbeddingGateway
from app.embeddings.registry import EmbeddingProviderRegistry
from app.embeddings.settings import EmbeddingSettings
from app.repositories.curriculum_repository import (
    CurriculumRepository
)
from app.repositories.practice_attempt_question_repository import (
    PracticeAttemptQuestionRepository
)
from app.repositories.practice_attempt_repository import (
    PracticeAttemptRepository
)
from app.repositories.question_group_attempt_repository import (
    QuestionGroupAttemptRepository
)
from app.repositories.question_group_repository import (
    QuestionGroupRepository
)
from app.repositories.system_settings_repository import (
    SystemSettingsRepository
)
from app.schemas.practice import (
    PracticeAnswerRequest,
    PracticeAnswerResponse,
    PracticeConceptResult,
    PracticeQuestionOption,
    PracticeQuestionResponse
)
from app.services.curriculum_practice_service import (
    CurriculumPracticeService
)
from app.services.curriculum_search_service import (
    CurriculumSearchService
)
from app.services.practice_evaluation_service import (
    PracticeEvaluationService
)
from app.services.practice_submission_service import (
    PracticeSubmissionService
)
from app.services.question_group_evaluation_service import (
    QuestionGroupEvaluationService
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


@lru_cache(maxsize=1)
def get_practice_submission_service() -> PracticeSubmissionService:
    settings_repository = SystemSettingsRepository()

    standard_evaluation_service = PracticeEvaluationService(
        repository=CurriculumRepository(),
        ai_gateway=AIGateway(
            registry=AIProviderRegistry(),
            settings=AISettings(
                repository=settings_repository
            )
        ),
        question_identity_repository=(
            PracticeAttemptQuestionRepository()
        )
    )

    group_evaluation_service = QuestionGroupEvaluationService(
        repository=QuestionGroupRepository(),
        attempt_repository=QuestionGroupAttemptRepository()
    )

    return PracticeSubmissionService(
        attempt_repository=PracticeAttemptRepository(),
        standard_evaluation_service=standard_evaluation_service,
        group_evaluation_service=group_evaluation_service
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


@router.post(
    "/answer",
    response_model=PracticeAnswerResponse,
    response_model_exclude_none=True
)
def submit_practice_answer(
    request: PracticeAnswerRequest,
    db: Session = Depends(get_db),
    service: PracticeSubmissionService = Depends(
        get_practice_submission_service
    )
) -> PracticeAnswerResponse:
    result = service.submit(
        db=db,
        student_id=request.student_id,
        curriculum_id=request.curriculum_id,
        logical_question_key=request.logical_question_key,
        answer=request.answer,
        idempotency_key=request.idempotency_key
    )

    status = result.get("status")

    error_status_codes = {
        "question_not_found": 404,
        "idempotency_conflict": 409,
        "invalid_question_key": 422,
        "invalid_answer": 422,
        "invalid_submission": 422,
        "unsupported_question_type": 422
    }

    if status in error_status_codes:
        raise HTTPException(
            status_code=error_status_codes[status],
            detail=result.get(
                "feedback",
                "The practice answer could not be submitted."
            )
        )

    if not result.get("attempt_id"):
        raise HTTPException(
            status_code=409,
            detail=result.get(
                "feedback",
                "The practice answer could not be evaluated."
            )
        )

    logical_question_key = (
        result.get("logical_question_key")
        or request.logical_question_key.strip()
    )

    question_type = result.get("question_type")

    if not question_type:
        question_type = (
            "multi_select"
            if logical_question_key.startswith("group:")
            else "standard"
        )

    concept_diagnoses = result.get(
        "concept_diagnoses",
        {}
    )

    concepts = [
        PracticeConceptResult(
            code=concept_code,
            status=diagnosis.get("status"),
            reason=diagnosis.get("reason")
        )
        for concept_code, diagnosis in sorted(
            concept_diagnoses.items()
        )
    ]

    return PracticeAnswerResponse(
        attempt_id=result["attempt_id"],
        logical_question_key=logical_question_key,
        question_type=question_type,
        status=status,
        feedback=result.get("feedback") or "",
        concepts=concepts,
        idempotent_replay=result.get(
            "idempotent_replay",
            False
        )
    )
