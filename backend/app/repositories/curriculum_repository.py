from sqlalchemy import delete, select, func
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.curriculum import (
    CurriculumDocument,
    CurriculumPage
)

from app.models.curriculum import (
    CurriculumDocument,
    CurriculumPage,
    CurriculumSection
)

from app.models.curriculum import (
    CurriculumChunk,
    CurriculumDocument,
    CurriculumPage,
    CurriculumSection,
    CurriculumQuestionSolution,
    PracticeAttempt,
    CurriculumConcept,
    CurriculumChunkConcept,
    PracticeAttempt,
    PracticeAttemptConcept
)

class CurriculumRepository:

    def replace_sections(
        self,
        db: Session,
        page: CurriculumPage,
        sections
    ) -> None:

        # Chunks are derived from sections.
        # Delete old chunks before deleting/replacing sections.
        db.execute(
            delete(
                CurriculumChunk
            ).where(
                CurriculumChunk.page_id == page.id
            )
        )

        db.flush()

        # Remove old sections
        page.sections.clear()

        db.flush()

        # Create the newly extracted sections
        for index, section in enumerate(
            sections
        ):

            content_parts = []

            if section.content:
                content_parts.append(
                    section.content
                )

            for question in section.questions:

                question_text = (
                    question.text
                )

                if question.math_expression:
                    question_text += (
                        "\n"
                        + question.math_expression
                    )

                content_parts.append(
                    question_text
                )

            content = "\n\n".join(
                content_parts
            ).strip()

            db_section = CurriculumSection(
                page_id=page.id,
                section_type=section.section_type,
                title=section.title,
                content=content,
                sequence=index
            )

            db.add(
                db_section
            )

        db.commit()

    def get_document(
        self,
        db: Session,
        document_id: int
    ) -> CurriculumDocument | None:

        statement = select(
            CurriculumDocument
        ).where(
            CurriculumDocument.id == document_id
        )

        return db.execute(
            statement
        ).scalar_one_or_none()


    def save_page(
        self,
        db: Session,
        document_id: int,
        page_number: int,
        page_type: str | None,
        raw_extracted_content: str
    ) -> CurriculumPage:


        statement = select(
            CurriculumPage
        ).where(
            CurriculumPage.document_id == document_id,
            CurriculumPage.page_number == page_number
        )

        page = db.execute(
            statement
        ).scalar_one_or_none()

        if page:
            page.page_type = page_type
            page.raw_extracted_content = (
                raw_extracted_content
            )

        else:
            page = CurriculumPage(
                document_id=document_id,
                page_number=page_number,
                page_type=page_type,
                raw_extracted_content=(
                    raw_extracted_content
                )
            )

            db.add(page)

        db.commit()
        db.refresh(page)

        return page

    def get_page(
        self,
        db: Session,
        document_id: int,
        page_number: int
    ) -> CurriculumPage | None:

        statement = select(
            CurriculumPage
        ).where(
            CurriculumPage.document_id == document_id,
            CurriculumPage.page_number == page_number
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    def replace_chunks(
        self,
        db: Session,
        page_id: int,
        chunks: list[dict]
    ) -> list[CurriculumChunk]:

        db.execute(
            delete(
                CurriculumChunk
            ).where(
                CurriculumChunk.page_id == page_id
            )
        )

        created_chunks = []

        for chunk_data in chunks:

            chunk = CurriculumChunk(
                page_id=page_id,
                section_id=chunk_data[
                    "section_id"
                ],
                chunk_type=chunk_data[
                    "chunk_type"
                ],
                content=chunk_data[
                    "content"
                ],
                question_number=chunk_data[
                    "question_number"
                ],
                lesson_number=chunk_data[
                    "lesson_number"
                ],
                lesson_title=chunk_data[
                    "lesson_title"
                ],
                sequence=chunk_data[
                    "sequence"
                ]
            )

            db.add(chunk)

            created_chunks.append(
                chunk
            )

        db.commit()

        for chunk in created_chunks:
            db.refresh(chunk)

        return created_chunks 

    def get_chunks_without_embeddings(
        self,
        db: Session
    ) -> list[CurriculumChunk]:

        statement = (
            select(CurriculumChunk)
            .where(
                CurriculumChunk.embedding.is_(None)
            )
            .order_by(
                CurriculumChunk.id
            )
        )

        return list(
            db.execute(
                statement
            ).scalars().all()
        )
    
    def save_chunk_embeddings(
        self,
        db: Session,
        chunks: list[CurriculumChunk],
        embeddings: list[list[float]],
        provider_name: str,
        model_name: str,
        dimensions: int
    ) -> None:

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks count does not match "
                "embeddings count"
            )

        from datetime import datetime

        embedded_at = datetime.utcnow()

        for chunk, embedding in zip(
            chunks,
            embeddings
        ):

            chunk.embedding = embedding

            chunk.embedding_provider = (
                provider_name
            )

            chunk.embedding_model = (
                model_name
            )

            chunk.embedding_dimensions = (
                dimensions
            )

            chunk.embedded_at = embedded_at

        db.commit()

    def search_similar_chunks(
        self,
        db: Session,
        query_embedding: list[float],
        provider_name: str,
        model_name: str,
        dimensions: int,
        curriculum_id: int,
        lesson_number: str | None = None,
        chunk_types: list[str] | None = None,
        limit: int = 5
    ):

        distance = (
            CurriculumChunk.embedding
            .cosine_distance(
                query_embedding
            )
        )

        conditions = [
            CurriculumDocument.curriculum_id
            == curriculum_id,

            CurriculumChunk.embedding
            .is_not(None),

            CurriculumChunk.embedding_provider
            == provider_name,

            CurriculumChunk.embedding_model
            == model_name,

            CurriculumChunk.embedding_dimensions
            == dimensions
        ]


        if lesson_number:

            conditions.append(
                CurriculumChunk.lesson_number
                == lesson_number
            )

        if chunk_types:

            conditions.append(
                CurriculumChunk.chunk_type.in_(
                    chunk_types
                )
            )

        statement = (
            select(
                CurriculumChunk,
                distance.label(
                    "distance"
                )
            )
            .join(
                CurriculumPage,
                CurriculumChunk.page_id
                == CurriculumPage.id
            )
            .join(
                CurriculumDocument,
                CurriculumPage.document_id
                == CurriculumDocument.id
            )
            .where(
                *conditions
            )
            .order_by(
                distance
            )
            .limit(
                limit
            )
        )


        return db.execute(
            statement
        ).all()

    def get_verified_solution(
        self,
        db: Session,
        chunk_id: int
    ) -> CurriculumQuestionSolution | None:

        statement = (
            select(
                CurriculumQuestionSolution
            )
            .where(
                CurriculumQuestionSolution.chunk_id
                == chunk_id,

                CurriculumQuestionSolution.verification_status
                == "verified"
            )
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    def get_chunk_for_curriculum(
        self,
        db: Session,
        chunk_id: int,
        curriculum_id: int
    ) -> CurriculumChunk | None:

        statement = (
            select(
                CurriculumChunk
            )
            .join(
                CurriculumPage,
                CurriculumChunk.page_id
                == CurriculumPage.id
            )
            .join(
                CurriculumDocument,
                CurriculumPage.document_id
                == CurriculumDocument.id
            )
            .where(
                CurriculumChunk.id
                == chunk_id,

                CurriculumDocument.curriculum_id
                == curriculum_id
            )
        )

        return db.execute(
            statement
        ).scalar_one_or_none()

    def save_practice_attempt(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        chunk: CurriculumChunk,
        student_answer: str,
        reference_answer: str | None,
        evaluation_status: str,
        feedback: str | None,
        solution_source: str | None,
        ai_provider: str | None,
        ai_model: str | None,
        concept_diagnoses: dict[str, dict] | None = None
    ) -> PracticeAttempt:

        attempt = PracticeAttempt(
            student_id=student_id,
            curriculum_id=curriculum_id,

            chunk_id=chunk.id,

            question_number=(
                chunk.question_number
            ),

            question_content=(
                chunk.content
            ),

            lesson_number=(
                chunk.lesson_number
            ),

            lesson_title=(
                chunk.lesson_title
            ),

            student_answer=(
                student_answer
            ),

            reference_answer=(
                reference_answer
            ),

            evaluation_status=(
                evaluation_status
            ),

            feedback=feedback,

            solution_source=(
                solution_source
            ),

            ai_provider=ai_provider,

            ai_model=ai_model
        )

        db.add(attempt)

        # We need the attempt ID before creating
        # the child concept snapshot records.
        db.flush()


        concepts = (
            self.get_chunk_concepts(
                db=db,
                chunk_id=chunk.id
            )
        )


        for concept in concepts:

            diagnosis = None

            if concept_diagnoses:

                diagnosis = (
                    concept_diagnoses.get(
                        concept.code
                    )
                )


            attempt_concept = (
                PracticeAttemptConcept(
                    attempt_id=attempt.id,

                    concept_id=concept.id,

                    concept_code=concept.code,

                    concept_name=concept.name,

                    source="question_mapping",

                    diagnosis_status=(
                        diagnosis["status"]
                        if diagnosis
                        else None
                    ),

                    diagnosis_reason=(
                        diagnosis["reason"]
                        if diagnosis
                        else None
                    ),

                    diagnosis_source=(
                        "ai_evaluation"
                        if diagnosis
                        else None
                    ),

                    diagnosed_at=(
                        datetime.utcnow()
                        if diagnosis
                        else None
                    )
                )
            )

            db.add(attempt_concept)

        db.add(attempt_concept)


        db.commit()

        db.refresh(attempt)

        return attempt

    def get_student_lesson_attempts(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        lesson_number: str
    ) -> list[PracticeAttempt]:

        statement = (
            select(
                PracticeAttempt
            )
            .where(
                PracticeAttempt.student_id
                == student_id,

                PracticeAttempt.curriculum_id
                == curriculum_id,

                PracticeAttempt.lesson_number
                == lesson_number
            )
            .order_by(
                PracticeAttempt.created_at,
                PracticeAttempt.id
            )
        )

        return list(
            db.execute(
                statement
            )
            .scalars()
            .all()
        )

    def count_lesson_practice_questions(
        self,
        db: Session,
        curriculum_id: int,
        lesson_number: str
    ) -> int:

        statement = (
            select(
                func.count(
                    CurriculumChunk.id
                )
            )
            .join(
                CurriculumPage,
                CurriculumChunk.page_id
                == CurriculumPage.id
            )
            .join(
                CurriculumDocument,
                CurriculumPage.document_id
                == CurriculumDocument.id
            )
            .where(
                CurriculumDocument.curriculum_id
                == curriculum_id,

                CurriculumChunk.lesson_number
                == lesson_number,

                CurriculumChunk.chunk_type
                == "practice_question"
            )
        )

        return (
            db.execute(
                statement
            ).scalar_one()
        )

    def get_chunk_concepts(
        self,
        db: Session,
        chunk_id: int
    ) -> list[CurriculumConcept]:

        statement = (
            select(
                CurriculumConcept
            )
            .join(
                CurriculumChunkConcept,
                CurriculumChunkConcept.concept_id
                == CurriculumConcept.id
            )
            .where(
                CurriculumChunkConcept.chunk_id
                == chunk_id
            )
            .order_by(
                CurriculumConcept.id
            )
        )

        return list(
            db.execute(
                statement
            )
            .scalars()
            .all()
        )
    def get_student_lesson_concept_diagnoses(
        self,
        db: Session,
        student_id: int,
        curriculum_id: int,
        lesson_number: str
    ) -> list[tuple[PracticeAttemptConcept, PracticeAttempt]]:

        statement = (
            select(
                PracticeAttemptConcept,
                PracticeAttempt
            )
            .join(
                PracticeAttempt,
                PracticeAttemptConcept.attempt_id
                == PracticeAttempt.id
            )
            .where(
                PracticeAttempt.student_id
                == student_id,

                PracticeAttempt.curriculum_id
                == curriculum_id,

                PracticeAttempt.lesson_number
                == lesson_number
            )
            .order_by(
                PracticeAttempt.created_at,
                PracticeAttempt.id,
                PracticeAttemptConcept.id
            )
        )

        return list(
            db.execute(
                statement
            ).all()
        )