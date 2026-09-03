from enum import Enum

from pydantic import BaseModel


class PageType(str, Enum):
    COURSE_OVERVIEW = "course_overview"
    LESSON = "lesson"
    PRACTICE = "practice"
    REVIEW = "review"
    ASSESSMENT = "assessment"
    REFERENCE = "reference"
    ANSWER_KEY = "answer_key"
    OTHER = "other"


class SectionType(str, Enum):
    INFORMATIONAL = "informational"
    WARM_UP = "warm_up"
    MINI_LESSON = "mini_lesson"
    EXAMPLE = "example"
    PRACTICE = "practice"
    REVIEW = "review"
    ASSESSMENT = "assessment"
    REFERENCE = "reference"
    OTHER = "other"


class ExtractedQuestion(BaseModel):
    number: str | None
    text: str
    math_expression: str | None


class ExtractedSection(BaseModel):
    section_type: SectionType
    title: str | None
    content: str | None
    questions: list[ExtractedQuestion]


class ExtractedPage(BaseModel):
    page_number: int
    page_type: PageType
    title: str | None
    lesson_number: str | None
    lesson_title: str | None
    sections: list[ExtractedSection]