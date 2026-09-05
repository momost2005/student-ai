from pydantic import (
    BaseModel,
    ConfigDict,
    Field
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
