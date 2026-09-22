"""Mocking UserRepository itself -- per the forward reference in its own
docstring -- instead of a real sqlite3 connection, plus verifying the
welcome-email interaction. Ties Week 4's dependency-injection and
mocking material back into the Week 2 accounts code.

Contrast with tests/accounts/test_user_repository.py, which exercises a
*real* sqlite3 connection via the db_connection fixture: that file tests
UserRepository itself, while this one tests a caller of UserRepository
in isolation from it.
"""

from unittest.mock import MagicMock, create_autospec

import pytest

from app.accounts.registration_service import UserRegistrationService
from app.accounts.user_repository import UserRepository


def test_register_inserts_new_user_and_sends_welcome_email():
    repository = create_autospec(UserRepository, instance=True)
    repository.get_user_by_name.return_value = None
    repository.insert_user.return_value = 42
    email_client = MagicMock()

    service = UserRegistrationService(repository, email_client)
    user_id = service.register("Carol", "carol@example.com")

    assert user_id == 42
    repository.insert_user.assert_called_once_with("Carol")
    email_client.send.assert_called_once_with("carol@example.com", "Welcome, Carol!")


def test_register_rejects_a_duplicate_name_without_emailing():
    repository = create_autospec(UserRepository, instance=True)
    repository.get_user_by_name.return_value = (1, "Carol")
    email_client = MagicMock()

    service = UserRegistrationService(repository, email_client)

    with pytest.raises(ValueError):
        service.register("Carol", "carol@example.com")

    repository.insert_user.assert_not_called()
    email_client.send.assert_not_called()


def test_autospec_repository_catches_a_typoed_method_name():
    """Same 'mocks that lie' point as
    tests/notifications/test_password_reset_service.py, this time
    against UserRepository: create_autospec constrains the double to
    UserRepository's real interface, so a typo'd method name raises
    instead of silently returning a fresh, obliging MagicMock."""
    repository = create_autospec(UserRepository, instance=True)

    with pytest.raises(AttributeError):
        repository.get_user_by_nmae("Carol")  # typo of get_user_by_name
