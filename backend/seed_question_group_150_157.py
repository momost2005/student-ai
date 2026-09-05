from sqlalchemy import select

from app.db.database import (
    SessionLocal
)

from app.models.curriculum import (
    CurriculumChunk,
    CurriculumPage
)

from app.models.question_group import (
    CurriculumQuestionGroup,
    CurriculumQuestionGroupChunk
)


db = SessionLocal()


try:

    # -------------------------------------------------
    # 1. The extracted chunks that belong to the same
    #    logical curriculum question.
    # -------------------------------------------------

    chunk_ids = [
        150,
        151,
        152,
        153,
        154,
        155,
        156,
        157
    ]


    chunks = []


    for chunk_id in chunk_ids:

        chunk = db.get(
            CurriculumChunk,
            chunk_id
        )


        if not chunk:

            raise RuntimeError(
                f"Chunk not found: {chunk_id}"
            )


        chunks.append(
            chunk
        )


    # -------------------------------------------------
    # 2. Validate that all chunks are on the same page.
    # -------------------------------------------------

    page_ids = {
        chunk.page_id
        for chunk in chunks
    }


    if len(page_ids) != 1:

        raise RuntimeError(
            "The selected chunks do not belong "
            "to the same curriculum page."
        )


    page_id = next(
        iter(page_ids)
    )


    page = db.get(
        CurriculumPage,
        page_id
    )


    if not page:

        raise RuntimeError(
            f"Curriculum page not found: "
            f"{page_id}"
        )


    # -------------------------------------------------
    # 3. Validate lesson metadata.
    # -------------------------------------------------

    lesson_numbers = {
        chunk.lesson_number
        for chunk in chunks
    }


    if len(lesson_numbers) != 1:

        raise RuntimeError(
            "The selected chunks do not have "
            "the same lesson number."
        )


    lesson_number = next(
        iter(lesson_numbers)
    )


    # -------------------------------------------------
    # 4. Define the logical question group.
    # -------------------------------------------------

    group_key = (
        "question_1_gcf_of_1_pairs"
    )


    instructions = (
        "Circle the pair of numbers that has "
        "a greatest common factor (GCF) of 1."
    )


    # -------------------------------------------------
    # 5. Find or create group.
    # -------------------------------------------------

    statement = (
        select(
            CurriculumQuestionGroup
        )
        .where(
            CurriculumQuestionGroup.document_id
            == page.document_id,

            CurriculumQuestionGroup.page_number
            == page.page_number,

            CurriculumQuestionGroup.group_key
            == group_key
        )
    )


    group = (
        db.execute(
            statement
        )
        .scalar_one_or_none()
    )


    group_created = False


    if not group:

        group = CurriculumQuestionGroup(
            document_id=page.document_id,
            page_number=page.page_number,
            lesson_number=lesson_number,
            group_key=group_key,
            question_number="1",
            question_type="multi_select",
            instructions=instructions
        )


        db.add(
            group
        )


        # We need the generated group ID before
        # inserting the child chunk mappings.
        db.flush()


        group_created = True


    else:

        # Keep metadata synchronized when the seed
        # script is executed again.
        group.lesson_number = (
            lesson_number
        )

        group.question_number = "1"

        group.question_type = (
            "multi_select"
        )

        group.instructions = (
            instructions
        )


    # -------------------------------------------------
    # 6. Link the extracted chunks as options.
    # -------------------------------------------------

    mappings_created = 0


    for sequence, chunk in enumerate(
        chunks,
        start=1
    ):

        statement = (
            select(
                CurriculumQuestionGroupChunk
            )
            .where(
                CurriculumQuestionGroupChunk.question_group_id
                == group.id,

                CurriculumQuestionGroupChunk.chunk_id
                == chunk.id
            )
        )


        mapping = (
            db.execute(
                statement
            )
            .scalar_one_or_none()
        )


        if not mapping:

            mapping = (
                CurriculumQuestionGroupChunk(
                    question_group_id=group.id,
                    chunk_id=chunk.id,
                    role="option",
                    sequence=sequence
                )
            )


            db.add(
                mapping
            )


            mappings_created += 1


        else:

            mapping.role = "option"
            mapping.sequence = sequence


    db.commit()

    db.refresh(
        group
    )


    # -------------------------------------------------
    # 7. Output
    # -------------------------------------------------

    print()
    print("=" * 80)
    print("QUESTION GROUP CREATED")
    print("=" * 80)


    print(
        f"Group ID: "
        f"{group.id}"
    )

    print(
        f"Created Now: "
        f"{group_created}"
    )

    print(
        f"Document ID: "
        f"{group.document_id}"
    )

    print(
        f"Page Number: "
        f"{group.page_number}"
    )

    print(
        f"Lesson Number: "
        f"{group.lesson_number}"
    )

    print(
        f"Question Number: "
        f"{group.question_number}"
    )

    print(
        f"Question Type: "
        f"{group.question_type}"
    )

    print(
        f"Group Key: "
        f"{group.group_key}"
    )

    print(
        f"Mappings Created: "
        f"{mappings_created}"
    )


    print()
    print("Instructions:")

    print(
        group.instructions
    )


    print()
    print("Group Members:")


    for sequence, chunk in enumerate(
        chunks,
        start=1
    ):

        print(
            f"{sequence}. "
            f"Chunk {chunk.id}"
        )


finally:

    db.close()