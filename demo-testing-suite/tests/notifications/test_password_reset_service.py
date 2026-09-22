"""Test doubles for PasswordResetService: dummy, stub, fake, spy, mock.

Real, runnable versions of the Week 4 reading's "The Test Double
Taxonomy" code samples, run against
app/notifications/password_reset.py instead of a slide. Organized in
the same order as the reading -- dummy, stub, fake, spy, mock -- and
closing with the "Mocks that lie" pitfall from Common Pitfalls.
"""

from unittest.mock import MagicMock, create_autospec

import pytest

from app.notifications.password_reset import EmailClient, PasswordResetService


# ---------------------------------------------------------------------
# The five double implementations, defined once and reused below --
# same shapes as the reading, one class each.
# ---------------------------------------------------------------------
class DummyLogger:
    """Dummy: poisoned on purpose, so any accidental use fails loudly
    instead of silently doing nothing. send_reset_email() never calls
    `logger`, so a correct test never triggers this."""

    def log(self, message):
        raise AssertionError("DummyLogger should never be called in this test")


class StubEmailClient:
    """Stub: always gives the same canned answer. No test below inspects
    it afterward or asserts how it was called."""

    def send(self, to, message):
        return True


class FakeEmailClient:
    """Fake: a lightweight but genuinely working implementation (an
    in-memory 'sent mail' list) -- good enough for tests, not fit for
    production."""

    def __init__(self):
        self.sent_emails = []

    def send(self, to, message):
        self.sent_emails.append((to, message))
        return True


class SpyEmailClient:
    """Spy: records every call so the test can inspect it afterward."""

    def __init__(self):
        self.calls = []

    def send(self, to, message):
        self.calls.append((to, message))
        return True


# ---------------------------------------------------------------------
# Dummy -- supplied only because the constructor requires it; the test
# below never actually needs it.
# ---------------------------------------------------------------------
def test_reset_email_is_sent_to_the_right_address():
    email_client = FakeEmailClient()
    dummy_logger = DummyLogger()  # required by the constructor, never used here

    service = PasswordResetService(email_client, dummy_logger)
    service.send_reset_email("alice@example.com", "123456")

    to, _ = email_client.sent_emails[0]
    assert to == "alice@example.com"


# ---------------------------------------------------------------------
# Stub -- a canned answer, with no expectations about how it is used.
# ---------------------------------------------------------------------
def test_send_reset_email_completes_without_error():
    service = PasswordResetService(StubEmailClient(), DummyLogger())
    service.send_reset_email("alice@example.com", "123456")  # runs to completion; nothing asserted on the stub


# ---------------------------------------------------------------------
# Fake -- verified via STATE VERIFICATION: the resulting state of the
# fake, after the action.
# ---------------------------------------------------------------------
def test_reset_email_is_recorded_by_the_fake():
    email_client = FakeEmailClient()
    service = PasswordResetService(email_client, DummyLogger())
    service.send_reset_email("alice@example.com", "123456")

    assert len(email_client.sent_emails) == 1
    to, message = email_client.sent_emails[0]
    assert to == "alice@example.com"
    assert "123456" in message


# ---------------------------------------------------------------------
# Spy -- records calls for the test to inspect afterward.
# ---------------------------------------------------------------------
def test_email_client_is_called_exactly_once():
    spy = SpyEmailClient()
    service = PasswordResetService(spy, DummyLogger())
    service.send_reset_email("alice@example.com", "123456")

    assert len(spy.calls) == 1


# ---------------------------------------------------------------------
# Mock -- verified via BEHAVIOR VERIFICATION: the interaction itself,
# checked directly against the mock's own expectations.
# ---------------------------------------------------------------------
def test_email_client_called_with_correct_message():
    mock_client = MagicMock()
    service = PasswordResetService(mock_client, DummyLogger())
    service.send_reset_email("alice@example.com", "123456")

    mock_client.send.assert_called_once_with(
        "alice@example.com",
        "Subject: Password Reset\n\nYour reset code is 123456",
    )


# ---------------------------------------------------------------------
# Common Pitfalls: "Mocks that lie." A bare MagicMock() accepts ANY
# attribute access, so a typo'd method name doesn't fail the way the
# real EmailClient interface would. Constraining the double to that
# interface with create_autospec catches the mismatch instead.
# ---------------------------------------------------------------------
def test_bare_mock_lets_a_typoed_method_through_silently():
    loose_mock = MagicMock()

    loose_mock.sedn("alice@example.com", "oops")  # typo of "send"

    loose_mock.sedn.assert_called_once()  # MagicMock happily obliges


def test_autospec_mock_catches_the_same_typo():
    strict_mock = create_autospec(EmailClient, instance=True)

    with pytest.raises(AttributeError):
        strict_mock.sedn("alice@example.com", "oops")
