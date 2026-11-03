import sqlite3

import pytest

from registration import RegistrationService, StudentRepository


@pytest.mark.integration
def test_student_registration():
    # Arrange: create a real, temporary in-memory SQLite database.
    db = sqlite3.connect(":memory:")
    try:
        db.execute(
            """
            CREATE TABLE students (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL
            )
            """
        )

        # Use the actual repository and service (no mocks).
        repository = StudentRepository(db)
        service = RegistrationService(repository)

        # Act: register a student through the service.
        result = service.register(101, "John")

        # Assert: verify the record was stored and retrieved.
        assert result == (101, "John")
    finally:
        db.close()
