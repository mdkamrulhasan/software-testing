"""Exceptions shared by the shop's components.

Every component that raises one of these, and every component that
catches one, depends on this file: it is part of the interface between
them, not an implementation detail of either.
"""


class UnknownProduct(Exception):
    """No product has the requested SKU."""


class OutOfStock(Exception):
    """Not enough stock to reserve the requested quantity."""


class PaymentError(Exception):
    """The provider rejected the request: our bug or misconfiguration."""


class PaymentDeclined(PaymentError):
    """The provider declined the card."""


class PaymentUnavailable(PaymentError):
    """The provider is down, timed out, or unreachable."""
