"""Collaborators for the Week 4 reading's "Test Double Taxonomy" section.

The reading illustrates all five test doubles with "a single running
example: an order_service that, when placing an order, normally has to
interact with three external collaborators -- a payment service, a
database, and an email service." Transcribed here as three module-level
functions, matching the reading exactly, so its dummy/stub/fake/spy/mock
examples can run against real code instead of a slide. See
tests/orders/test_order_service.py.

Note: the reading's own code samples for this section are a few small,
mostly independent functions rather than methods on one OrderService
class -- calculate_total() and place_order() are order-related, while
register_user() (used for the Spy example) is about welcoming a new
user by email. All three are kept together in this one file because the
reading introduces and uses them as one running example.

Contrast with app/notifications/password_reset.py, which is the
reading's separate "Dependency Isolation and Seams" worked example.
"""


def calculate_total(price, logger):
    """Return `price` with 6% tax applied.

    `logger` is accepted but never used -- see the Dummy tests in
    test_order_service.py.
    """
    return price * 1.06


def place_order(payment_service):
    """Ask `payment_service` to process a $100 payment and report the
    outcome. Used by both the Stub and Mock examples."""
    if payment_service.process_payment(100):
        return "Order confirmed"
    return "Payment failed"


def register_user(email_service):
    """Welcome a new user by email. Used by the Spy example."""
    email_service.send_email("alice@example.com")
