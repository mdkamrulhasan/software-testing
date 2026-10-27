"""IP6: PaymentClient against the fake PayFast, over real HTTP.

The fake (fakes/payment_provider.py) runs on a local port and enforces
the provider's contract. This is the same client code as in
test_payments_stubbed.py, but the other side now *checks* what it
receives, the way PayFast would.

    SHOP_PAYMENTS=v1 pytest tests/test_payments_live.py
"""

import pytest

from shop.errors import PaymentDeclined, PaymentError, PaymentUnavailable
from tests.variants import PaymentClient


def test_charge_succeeds_in_integer_cents(payments, provider):
    """R1: the provider receives 1250 (cents), not "12.50"."""
    assert payments.charge(1250, reference="order-1") == "ch_1"
    assert provider.charges == [
        {"id": "ch_1", "amount": 1250, "currency": "USD", "status": "succeeded"}
    ]


def test_declined_card(payments, provider):
    provider.config["MODE"] = "decline"
    with pytest.raises(PaymentDeclined, match="card_declined"):
        payments.charge(1250, reference="order-1")
    assert provider.charges == []


def test_wrong_api_key_is_our_error_and_is_not_retried(provider):
    """R8: a 401 means the shop is misconfigured. Retrying cannot help."""
    misconfigured = PaymentClient(provider.url, "sk_wrong_key", timeout=1.0)
    with pytest.raises(PaymentError, match="401") as caught:
        misconfigured.charge(1250, reference="order-1")
    assert type(caught.value) is PaymentError   # not PaymentUnavailable
    assert len(provider.requests) == 1


def test_outage_is_retried_then_reported_as_unavailable(payments, provider):
    """R5: the 503 body is an HTML page; the client must not try to
    parse it as JSON."""
    provider.config["MODE"] = "unavailable"
    with pytest.raises(PaymentUnavailable, match="503"):
        payments.charge(1250, reference="order-1")
    assert len(provider.requests) == 2


def test_slow_provider_times_out(provider):
    """R7: without a timeout, this call would wait as long as PayFast does."""
    provider.config["DELAY"] = 0.5
    impatient = PaymentClient(provider.url, "sk_test_123", timeout=0.2)
    with pytest.raises(PaymentUnavailable, match="ReadTimeout"):
        impatient.charge(1250, reference="order-1")


def test_same_reference_is_charged_only_once(payments, provider):
    """R6: what makes the client's retries safe."""
    first = payments.charge(1250, reference="order-1")
    second = payments.charge(1250, reference="order-1")
    assert first == second
    assert len(provider.charges) == 1
