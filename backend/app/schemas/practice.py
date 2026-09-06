from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    StrictStr
)


class PracticeQuestionOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0)
    text: str = Field(min_length=1)


class PracticeQuestionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    logical_question_key: str = Field(min_length=1)
    question_type: str = Field(min_length=1)
    lesson_number: str = Field(min_length=1)
    question_number: str | None = None
    prompt: str = Field(min_length=1)
    options: list[PracticeQuestionOption] = Field(
        default_factory=list
    )


class PracticeAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: int = Field(gt=0)
    curriculum_id: int = Field(gt=0)
    logical_question_key: str = Field(
        min_length=1,
        max_length=200
    )
    answer: StrictStr | list[StrictInt]
    idempotency_key: str | None = Field(
        default=None,
        min_length=1,
        max_length=200
    )


class PracticeConceptResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str = Field(min_length=1)
    status: str | None = None
    reason: str | None = None


class PracticeAnswerResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    attempt_id: int = Field(gt=0)
    logical_question_key: str = Field(min_length=1)
    question_type: str = Field(min_length=1)
    status: str = Field(min_length=1)
    feedback: str
    concepts: list[PracticeConceptResult] = Field(
        default_factory=list
    )
    idempotent_replay: bool = False
