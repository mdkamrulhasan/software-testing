"""IP6 with PayFast replaced by a stub at the HTTP layer (`responses`).

`responses` intercepts every call the `requests` library makes, so the
real PaymentClient code runs (building the request, handling status
codes, retrying), but nothing leaves the machine. A stub, though, only
knows what its author wrote into it. Compare the first two tests:

    SHOP_PAYMENTS=v1 pytest tests/test_payments_stubbed.py

The loose stub passes for the outdated client that sends dollars; the
contract check catches it.
"""

import json

import pytest
import requests
import responses

from shop.errors import PaymentError, PaymentUnavailable
from tests.variants import PaymentClient

BASE_URL = "https://api.payfast.test"
CHARGES = f"{BASE_URL}/v1/charges"


@pytest.fixture
def client():
    return PaymentClient(BASE_URL, "sk_test_123")


@responses.activate
def test_loose_stub_only_checks_the_return_value(client):
    """The usual first attempt. It cannot fail on a wrong request."""
    responses.post(CHARGES, json={"id": "ch_1", "status": "succeeded"}, status=201)
    assert client.charge(1250, reference="order-1") == "ch_1"


@responses.activate
def test_request_matches_the_provider_contract(client):
    """R1, R6, R8: the request itself, checked against
    specs/payment_provider_api.md -- integer cents, Bearer auth, and an
    Idempotency-Key."""
    responses.post(CHARGES, json={"id": "ch_1", "status": "succeeded"}, status=201)
    client.charge(1250, reference="order-1")

    sent = responses.calls[0].request
    assert json.loads(sent.body) == {
        "amount": 1250, "currency": "USD", "reference": "order-1",
    }
    assert sent.headers["Authorization"] == "Bearer sk_test_123"
    assert sent.headers["Idempotency-Key"] == "order-1"


@responses.activate
def test_retry_after_an_html_503_reuses_the_idempotency_key(client):
    """R5, R6: a 5xx body may not be JSON, and the retry must be safe."""
    responses.post(CHARGES, body="<html>503 Service Unavailable</html>",
                   status=503, content_type="text/html")
    responses.post(CHARGES, json={"id": "ch_1", "status": "succeeded"}, status=201)

    assert client.charge(1250, reference="order-1") == "ch_1"
    keys = [call.request.headers["Idempotency-Key"] for call in responses.calls]
    assert keys == ["order-1", "order-1"]


@responses.activate
def test_network_failure_is_reported_as_unavailable(client):
    responses.post(CHARGES, body=requests.ConnectionError("connection refused"))
    with pytest.raises(PaymentUnavailable, match="ConnectionError"):
        client.charge(1250, reference="order-1")
    assert len(responses.calls) == 2  # first try + one retry


@responses.activate
def test_a_400_is_our_bug_and_is_not_retried(client):
    responses.post(CHARGES, json={"error": "unsupported currency"}, status=400)
    with pytest.raises(PaymentError, match="400"):
        client.charge(1250, reference="order-1")
    assert len(responses.calls) == 1
