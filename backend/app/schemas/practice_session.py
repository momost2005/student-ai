from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)

from app.schemas.practice import PracticeQuestionResponse


class PracticeSessionStartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: int = Field(gt=0)
    curriculum_id: int = Field(gt=0)
    lesson_number: str = Field(min_length=1, max_length=50)
    target_question_count: int = Field(default=5, ge=1, le=100)


class PracticeSessionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: int = Field(gt=0)
    student_id: int = Field(gt=0)
    curriculum_id: int = Field(gt=0)
    lesson_number: str = Field(min_length=1)
    status: str = Field(min_length=1)
    target_question_count: int = Field(gt=0)
    questions_served: int = Field(ge=0)
    started_at: datetime
    completed_at: datetime | None = None


class PracticeSessionNextQuestionResponse(
    PracticeSessionResponse
):
    position: int | None = Field(default=None, gt=0)
    question: PracticeQuestionResponse | None = None
    is_replay: bool
