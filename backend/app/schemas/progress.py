from pydantic import (
    BaseModel,
    ConfigDict,
    Field
)


class MasteryEvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    minimum_unique_questions: int = Field(ge=0)
    minimum_coverage_percent: float = Field(ge=0)
    has_enough_evidence: bool


class LessonProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    student_id: int = Field(gt=0)
    curriculum_id: int = Field(gt=0)
    lesson_number: str = Field(min_length=1)
    total_attempts: int = Field(ge=0)
    assessed_attempts: int = Field(ge=0)
    correct_attempts: int = Field(ge=0)
    partial_attempts: int = Field(ge=0)
    incorrect_attempts: int = Field(ge=0)
    attempt_accuracy_percent: float = Field(ge=0)
    unique_questions_attempted: int = Field(ge=0)
    total_practice_questions: int = Field(ge=0)
    coverage_percent: float = Field(ge=0)
    current_correct: int = Field(ge=0)
    current_partial: int = Field(ge=0)
    current_incorrect: int = Field(ge=0)
    current_accuracy_percent: float = Field(ge=0)
    observed_performance_percent: float = Field(ge=0)
    mastery_status: str = Field(min_length=1)
    mastery_reason: str = Field(min_length=1)
    mastery_evidence: MasteryEvidenceResponse


class ConceptProgressResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    concept_code: str = Field(min_length=1)
    concept_name: str = Field(min_length=1)
    total_occurrences: int = Field(ge=0)
    unique_questions_seen: int = Field(ge=0)
    historical_demonstrated_count: int = Field(ge=0)
    historical_needs_review_count: int = Field(ge=0)
    historical_insufficient_evidence_count: int = Field(ge=0)
    historical_unassessed_count: int = Field(ge=0)
    historical_evidence_count: int = Field(ge=0)
    unique_assessed_questions: int = Field(ge=0)
    current_demonstrated: int = Field(ge=0)
    current_needs_review: int = Field(ge=0)
    observed_understanding_percent: float = Field(ge=0)
    latest_assessed_status: str | None = None
    latest_assessed_attempt_id: int | None = Field(
        default=None,
        gt=0
    )
    has_enough_evidence: bool
    minimum_unique_assessed_questions: int = Field(ge=0)
    classification: str = Field(min_length=1)
    classification_reason: str = Field(min_length=1)
