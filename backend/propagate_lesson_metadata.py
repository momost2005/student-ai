import sys

from app.db.database import (
    SessionLocal
)

from app.services.lesson_metadata_service import (
    LessonMetadataService
)


if len(sys.argv) < 3:

    print(
        "Usage: "
        "python propagate_lesson_metadata.py "
        "<start_page> <end_page>"
    )

    sys.exit(1)


start_page = int(sys.argv[1])
end_page = int(sys.argv[2])


db = SessionLocal()


try:

    service = LessonMetadataService()

    count = service.propagate_range(
        db=db,
        document_id=1,
        start_page=start_page,
        end_page=end_page
    )

    print(
        f"Updated pages: {count}"
    )


finally:

    db.close()