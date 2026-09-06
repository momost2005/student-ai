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
from app.repositories.practice_session_repository import (
    PracticeSessionRepository
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
from app.schemas.practice_session import (
    PracticeSessionNextQuestionResponse,
    PracticeSessionResponse,
    PracticeSessionStartRequest
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
from app.services.practice_session_service import (
    PracticeSessionService
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


@lru_cache(maxsize=1)
def get_practice_session_service() -> PracticeSessionService:
    return PracticeSessionService(
        repository=PracticeSessionRepository(),
        practice_service=get_practice_service()
    )


def build_practice_question_response(
    question: dict
) -> PracticeQuestionResponse:
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

    return build_practice_question_response(
        question
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
    ),
    session_service: PracticeSessionService = Depends(
        get_practice_session_service
    )
) -> PracticeAnswerResponse:
    logical_question_key = request.logical_question_key.strip()

    if request.session_id is not None:
        validation_error = (
            session_service.validate_answer_submission(
                db=db,
                session_id=request.session_id,
                student_id=request.student_id,
                curriculum_id=request.curriculum_id,
                logical_question_key=logical_question_key,
                idempotency_key=request.idempotency_key
            )
        )

        if validation_error is not None:
            raise HTTPException(
                status_code=(
                    404
                    if validation_error["status"]
                    in {
                        "session_not_found",
                        "session_question_not_found"
                    }
                    else 409
                ),
                detail=validation_error["feedback"]
            )

    result = service.submit(
        db=db,
        student_id=request.student_id,
        curriculum_id=request.curriculum_id,
        logical_question_key=logical_question_key,
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

    if request.session_id is not None:
        association_error = session_service.attach_attempt(
            db=db,
            session_id=request.session_id,
            student_id=request.student_id,
            curriculum_id=request.curriculum_id,
            logical_question_key=logical_question_key,
            attempt_id=result["attempt_id"]
        )

        if association_error is not None:
            raise HTTPException(
                status_code=409,
                detail=association_error["feedback"]
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
        session_id=request.session_id,
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


@router.post(
    "/sessions",
    response_model=PracticeSessionResponse,
    response_model_exclude_none=True,
    status_code=201
)
def start_practice_session(
    request: PracticeSessionStartRequest,
    db: Session = Depends(get_db),
    service: PracticeSessionService = Depends(
        get_practice_session_service
    )
) -> dict:
    lesson_number = request.lesson_number.strip()

    if not lesson_number:
        raise HTTPException(
            status_code=422,
            detail="lesson_number must not be blank."
        )

    result = service.start_session(
        db=db,
        student_id=request.student_id,
        curriculum_id=request.curriculum_id,
        lesson_number=lesson_number,
        target_question_count=request.target_question_count
    )

    if result.get("status") in {
        "student_not_found",
        "curriculum_not_found"
    }:
        raise HTTPException(
            status_code=404,
            detail=result["feedback"]
        )

    return result


@router.get(
    "/sessions/{session_id}/next-question",
    response_model=PracticeSessionNextQuestionResponse,
    response_model_exclude_none=True
)
def get_session_next_question(
    session_id: int,
    topic: Annotated[
        str | None,
        Query(min_length=1, max_length=500)
    ] = None,
    db: Session = Depends(get_db),
    service: PracticeSessionService = Depends(
        get_practice_session_service
    )
) -> PracticeSessionNextQuestionResponse:
    if session_id <= 0:
        raise HTTPException(
            status_code=422,
            detail="session_id must be greater than zero."
        )

    normalized_topic = topic.strip() if topic else None

    if topic is not None and not normalized_topic:
        raise HTTPException(
            status_code=422,
            detail="topic must not be blank."
        )

    result = service.get_next_question(
        db=db,
        session_id=session_id,
        topic=normalized_topic
    )

    if result.get("status") == "session_not_found":
        raise HTTPException(
            status_code=404,
            detail=result["feedback"]
        )

    public_question = None

    if result.get("question") is not None:
        public_question = build_practice_question_response(
            result["question"]
        )

    return PracticeSessionNextQuestionResponse(
        session_id=result["session_id"],
        student_id=result["student_id"],
        curriculum_id=result["curriculum_id"],
        lesson_number=result["lesson_number"],
        status=result["status"],
        target_question_count=(
            result["target_question_count"]
        ),
        questions_served=result["questions_served"],
        started_at=result["started_at"],
        completed_at=result["completed_at"],
        position=result["position"],
        question=public_question,
        is_replay=result["is_replay"]
    )
