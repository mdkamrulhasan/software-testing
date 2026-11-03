import sqlite3


class StudentRepository:
    """Data-access layer that uses SQLite to store student records."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def add_student(self, student_id: int, name: str) -> None:
        self.db.execute(
            "INSERT INTO students (id, name) VALUES (?, ?)",
            (student_id, name),
        )
        self.db.commit()

    def get_student(self, student_id: int):
        return self.db.execute(
            "SELECT id, name FROM students WHERE id = ?",
            (student_id,),
        ).fetchone()


class RegistrationService:
    """Business-logic layer for student registration."""

    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def register(self, student_id: int, name: str):
        self.repository.add_student(student_id, name)
        return self.repository.get_student(student_id)
