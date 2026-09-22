"""Tests for PasswordResetService -- the Week 4 reading's "Dependency
Isolation and Seams" worked example.

The reading's dedicated Test Double Taxonomy walkthrough uses a
different running example (order_service) -- see
tests/orders/test_order_service.py for the full dummy/stub/fake/spy/mock
tour. This file keeps only:
  - one test proving the injected `email_client` seam works with any
    object that has a `.send(to, message)` method (the reading's own
    description of what a test may supply), and
  - the "Mocks that lie" pitfall from Common Pitfalls, demonstrated
    against this module's EmailClient interface.
"""

from unittest.mock import Mock, create_autospec

import pytest

from app.notifications.password_reset import EmailClient, PasswordResetService


class RecordingEmailClient:
    """Any object with a .send(to, message) method works as the seam's
    test-side implementation -- this one just records what it was asked
    to send."""

    def __init__(self):
        self.sent = []

    def send(self, to, message):
        self.sent.append((to, message))


def test_send_reset_email_uses_the_injected_client():
    email_client = RecordingEmailClient()
    service = PasswordResetService(email_client, logger=None)

    service.send_reset_email("alice@example.com", "123456")

    to, message = email_client.sent[0]
    assert to == "alice@example.com"
    assert "123456" in message


# ---------------------------------------------------------------------
# Common Pitfalls: "Mocks that lie." A bare Mock() accepts ANY attribute
# access, so a typo'd method name doesn't fail the way the real
# EmailClient interface would. Constraining the double to that interface
# with create_autospec catches the mismatch instead.
# ---------------------------------------------------------------------
def test_bare_mock_lets_a_typoed_method_through_silently():
    loose_mock = Mock()

    loose_mock.sedn("alice@example.com", "oops")  # typo of "send"

    loose_mock.sedn.assert_called_once()  # Mock happily obliges


def test_autospec_mock_catches_the_same_typo():
    strict_mock = create_autospec(EmailClient, instance=True)

    with pytest.raises(AttributeError):
        strict_mock.sedn("alice@example.com", "oops")
