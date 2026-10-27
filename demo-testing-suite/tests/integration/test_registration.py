"""UserRegistrationService + the real UserRepository + real SQLite.

Week 10 (integration testing). The Week 4 unit tests in
tests/accounts/test_registration_service.py check the service's own
decisions with a mocked repository. These check what only the
assembled parts can show: that data is really committed, that the
database's constraints back up the service's rules, and what state is
left behind when a dependency fails part-way through.

Run only these with `pytest -m integration`, or skip them with
`pytest -m "not integration"`.
"""

import sqlite3

import pytest

from app.accounts.registration_service import UserRegistrationService
from app.accounts.user_repository import UserRepository

pytestmark = pytest.mark.integration


def test_registered_user_is_committed_to_the_database(service, email_client, saved_names):
    user_id = service.register("Carol", "carol@example.com")

    assert user_id == 1
    assert saved_names() == ["Carol"]  # visible from another connection
    assert email_client.sent == [("carol@example.com", "Welcome, Carol!")]


def test_duplicate_name_is_rejected_and_not_emailed_twice(service, email_client, saved_names):
    service.register("Carol", "carol@example.com")
    with pytest.raises(ValueError, match="already exists"):
        service.register("Carol", "carol2@example.com")

    assert saved_names() == ["Carol"]
    assert len(email_client.sent) == 1


def test_database_enforces_unique_names_even_without_the_service(connection):
    """Code that bypasses UserRegistrationService (a script, an admin
    tool, a future endpoint) still cannot create a duplicate."""
    repository = UserRepository(connection)
    repository.insert_user("Carol")
    with pytest.raises(sqlite3.IntegrityError, match="UNIQUE"):
        repository.insert_user("Carol")


class FailingEmailClient:
    def send(self, to, message):
        raise ConnectionError("SMTP server unreachable")


@pytest.mark.xfail(
    strict=True,
    reason="KNOWN ISSUE (Week 10): register() commits the user before sending "
           "the welcome email, with no compensation if the email fails. The "
           "user is left registered but never welcomed, and cannot retry: a "
           "second register() is rejected as a duplicate. Found by this "
           "integration test; a mocked repository has no committed state to "
           "leave behind. Documented, not fixed -- see the Week 10 demo guide.",
)
def test_failed_welcome_email_does_not_leave_a_half_registered_user(connection, saved_names):
    service = UserRegistrationService(UserRepository(connection), FailingEmailClient())
    with pytest.raises(ConnectionError):
        service.register("Carol", "carol@example.com")

    assert saved_names() == []
