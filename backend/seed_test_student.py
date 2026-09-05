from sqlalchemy import select

from app.db.database import SessionLocal
from app.models.curriculum import Student


db = SessionLocal()


try:

    statement = select(
        Student
    ).where(
        Student.display_name
        == "Prototype Student"
    )

    student = db.execute(
        statement
    ).scalar_one_or_none()


    if not student:

        student = Student(
            display_name="Prototype Student"
        )

        db.add(student)
        db.commit()
        db.refresh(student)


    print(
        f"Student ID: {student.id}"
    )

    print(
        f"Student Name: "
        f"{student.display_name}"
    )


finally:

    db.close()