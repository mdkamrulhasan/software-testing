"""Test doubles for order_service: dummy, stub, fake, spy, mock.

Real, runnable versions of the Week 4 reading's "The Test Double
Taxonomy" examples, run against app/orders/order_service.py instead of
a slide. Organized in the reading's own order.
"""

from unittest.mock import Mock

from app.orders.order_service import calculate_total, place_order, register_user


# ---------------------------------------------------------------------
# Dummy -- supplied only because calculate_total() requires a `logger`
# argument; the function never actually uses it.
# ---------------------------------------------------------------------
class DummyLogger:
    pass


def test_calculate_total_applies_six_percent_tax():
    dummy_logger = DummyLogger()

    assert calculate_total(100, dummy_logger) == 106


class PoisonedDummyLogger:
    """A dummy poisoned on purpose, per the reading's second Dummy tip
    box: any accidental use fails loudly instead of silently doing
    nothing."""

    def log(self, message):
        raise AssertionError("PoisonedDummyLogger should never be called in this test")


def test_calculate_total_never_touches_the_logger():
    assert calculate_total(100, PoisonedDummyLogger()) == 106


# ---------------------------------------------------------------------
# Stub -- a canned answer, with no expectations about how it is used.
# ---------------------------------------------------------------------
class PaymentStub:
    """A stub: always gives the same canned answer, so the code under
    test has something to work with."""

    def process_payment(self, amount):
        return True


def test_place_order_confirms_when_payment_succeeds():
    payment_stub = PaymentStub()

    assert place_order(payment_stub) == "Order confirmed"


# ---------------------------------------------------------------------
# Fake -- a lightweight, genuinely working implementation; verified via
# STATE VERIFICATION.
# ---------------------------------------------------------------------
class FakeDatabase:
    """A fake: a real, working implementation good enough for tests (an
    in-memory dictionary), but not fit for production."""

    def __init__(self):
        self.users = {}

    def save_user(self, user_id, name):
        self.users[user_id] = name

    def get_user(self, user_id):
        return self.users.get(user_id)


def test_fake_database_stores_and_retrieves_a_user():
    fake_db = FakeDatabase()
    fake_db.save_user(1, "Alice")

    assert fake_db.get_user(1) == "Alice"


# ---------------------------------------------------------------------
# Spy -- records calls for the test to inspect afterward.
# ---------------------------------------------------------------------
class EmailSpy:
    """A spy: records every call so the test can inspect it later."""

    def __init__(self):
        self.sent_to = []

    def send_email(self, address):
        self.sent_to.append(address)


def test_register_user_sends_a_welcome_email():
    email_spy = EmailSpy()

    register_user(email_spy)

    assert "alice@example.com" in email_spy.sent_to


# ---------------------------------------------------------------------
# Mock -- verified via BEHAVIOR VERIFICATION: the interaction itself,
# checked directly against the mock's own expectations.
# ---------------------------------------------------------------------
def test_place_order_calls_process_payment_with_the_order_total():
    payment_mock = Mock()
    payment_mock.process_payment.return_value = True

    place_order(payment_mock)

    payment_mock.process_payment.assert_called_once_with(100)
