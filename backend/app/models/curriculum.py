from datetime import datetime

from pgvector.sqlalchemy import VECTOR

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.db.database import Base



class Curriculum(Base):
    __tablename__ = "curricula"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    education_system: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    grade: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    subject: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    term: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    academic_year: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    documents = relationship(
        "CurriculumDocument",
        back_populates="curriculum",
        cascade="all, delete-orphan"
    )


class CurriculumDocument(Base):
    __tablename__ = "curriculum_documents"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curricula.id"),
        nullable=False,
        index=True
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    page_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        default="pending",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    curriculum = relationship(
        "Curriculum",
        back_populates="documents"
    )

    pages = relationship(
        "CurriculumPage",
        back_populates="document",
        cascade="all, delete-orphan"
    )


class CurriculumPage(Base):
    __tablename__ = "curriculum_pages"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    document_id: Mapped[int] = mapped_column(
        ForeignKey("curriculum_documents.id"),
        nullable=False,
        index=True
    )

    page_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    page_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    lesson_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    lesson_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    raw_extracted_content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    document = relationship(
        "CurriculumDocument",
        back_populates="pages"
    )

    sections = relationship(
        "CurriculumSection",
        back_populates="page",
        cascade="all, delete-orphan"
    )


class CurriculumSection(Base):    
    __tablename__ = "curriculum_sections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    page_id: Mapped[int] = mapped_column(
        ForeignKey("curriculum_pages.id"),
        nullable=False,
        index=True
    )

    section_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    page = relationship(
        "CurriculumPage",
        back_populates="sections"
    )

class CurriculumChunk(Base):
    __tablename__ = "curriculum_chunks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    page_id: Mapped[int] = mapped_column(
        ForeignKey("curriculum_pages.id"),
        nullable=False,
        index=True
    )

    section_id: Mapped[int | None] = mapped_column(
        ForeignKey("curriculum_sections.id"),
        nullable=True,
        index=True
    )

    chunk_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    embedding: Mapped[list[float] | None] = mapped_column(
        VECTOR(),
        nullable=True
    )

    embedding_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    embedding_dimensions: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    question_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    lesson_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    lesson_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    sequence: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )    

    embedded_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

class CurriculumQuestionSolution(Base):
    __tablename__ = "curriculum_question_solutions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    chunk_id: Mapped[int] = mapped_column(
        ForeignKey("curriculum_chunks.id"),
        nullable=False,
        unique=True,
        index=True
    )

    final_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    solution_steps: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    solution_source: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    verification_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    display_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class PracticeAttempt(Base):

    __tablename__ = "practice_attempts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id"),
        nullable=False,
        index=True
    )

    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curricula.id"),
        nullable=False,
        index=True
    )

    chunk_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "curriculum_chunks.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    question_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    question_content: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    lesson_title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    reference_answer: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    lesson_number: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    student_answer: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    evaluation_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    solution_source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    ai_provider: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    ai_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class CurriculumConcept(Base):
    __tablename__ = "curriculum_concepts"

    __table_args__ = (
        UniqueConstraint(
            "curriculum_id",
            "lesson_number",
            "code",
            name="uq_curriculum_concept_scope"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    curriculum_id: Mapped[int] = mapped_column(
        ForeignKey("curricula.id"),
        nullable=False,
        index=True
    )

    lesson_number: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


class CurriculumChunkConcept(Base):

    __tablename__ = "curriculum_chunk_concepts"

    __table_args__ = (
        UniqueConstraint(
            "chunk_id",
            "concept_id",
            name="uq_curriculum_chunk_concept"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    chunk_id: Mapped[int] = mapped_column(
        ForeignKey(
            "curriculum_chunks.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    concept_id: Mapped[int] = mapped_column(
        ForeignKey(
            "curriculum_concepts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

class PracticeAttemptConcept(Base):
    __tablename__ = "practice_attempt_concepts"

    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "concept_code",
            name="uq_practice_attempt_concept"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    attempt_id: Mapped[int] = mapped_column(
        ForeignKey(
            "practice_attempts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    concept_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "curriculum_concepts.id",
            ondelete="SET NULL"
        ),
        nullable=True,
        index=True
    )

    concept_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    concept_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="question_mapping"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    diagnosis_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    diagnosis_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    diagnosis_source: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    diagnosed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )