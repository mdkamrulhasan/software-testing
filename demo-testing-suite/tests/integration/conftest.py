"""Fixtures for the integration tests: real components, real database.

tests/accounts/test_registration_service.py (Week 4) tests
UserRegistrationService with a *mocked* UserRepository. These fixtures
assemble the same service from real parts instead: the real
UserRepository, on a real SQLite file in tmp_path, created with the
application's own create_schema(). Only email stays a test double -- a
fake that records what it would have sent -- because sending real email
from a test suite is never acceptable.
"""

import sqlite3

import pytest

from app.accounts.registration_service import UserRegistrationService
from app.accounts.user_repository import UserRepository, create_schema


class RecordingEmailClient:
    """A fake email client: works, but only records messages."""

    def __init__(self):
        self.sent = []

    def send(self, to, message):
        self.sent.append((to, message))


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "accounts.db"


@pytest.fixture
def connection(db_path):
    connection = sqlite3.connect(db_path)
    create_schema(connection)
    yield connection
    connection.close()


@pytest.fixture
def email_client():
    return RecordingEmailClient()


@pytest.fixture
def service(connection, email_client):
    return UserRegistrationService(UserRepository(connection), email_client)


@pytest.fixture
def saved_names(db_path):
    """The names committed to the database, read through a new
    connection -- so a test sees only what was really saved."""
    def read():
        fresh = sqlite3.connect(db_path)
        try:
            return [row[0] for row in fresh.execute("SELECT name FROM users ORDER BY id")]
        finally:
            fresh.close()
    return read
