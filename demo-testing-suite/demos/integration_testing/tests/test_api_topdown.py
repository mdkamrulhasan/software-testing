"""IP1 + IP2: the real HTTP API on top of a *stub* OrderService.

Top-down integration, step 1. The top layer is real (Flask routing,
validation, JSON, status codes); everything below it is replaced by a
stub with canned answers. This checks the API's half of each contract
in specs/shop_api.md before a database or payment provider exists.
"""

import pytest

from shop.api import create_app
from shop.errors import (
    OutOfStock, PaymentDeclined, PaymentError, PaymentUnavailable, UnknownProduct,
)

HEADERS = {"X-API-Key": "shop-key"}
GOOD_ORDER = {"sku": "MUG", "quantity": 2, "customer_email": "ana@example.com"}


class StubOrderService:
    """Stands in for OrderService: no database, no provider. Returns a
    canned order, or raises the exception it was given."""

    def __init__(self, raises=None):
        self.raises = raises
        self.calls = []

    def place_order(self, sku, quantity, customer_email):
        self.calls.append((sku, quantity, customer_email))
        if self.raises:
            raise self.raises
        return {"id": 7, "sku": sku, "quantity": quantity, "total_cents": 2500,
                "customer_email": customer_email, "status": "paid", "charge_id": "ch_1"}

    def get_order(self, order_id):
        return None


def api(stub):
    return create_app(stub, api_key="shop-key").test_client()


def test_success_is_201_with_a_location_header():
    response = api(StubOrderService()).post("/orders", json=GOOD_ORDER, headers=HEADERS)
    assert response.status_code == 201
    assert response.headers["Location"] == "/orders/7"


@pytest.mark.parametrize("raised, status", [
    pytest.param(UnknownProduct("MUG"), 404, id="unknown-sku"),
    pytest.param(OutOfStock("MUG"), 409, id="out-of-stock"),
    pytest.param(PaymentDeclined("card_declined"), 402, id="declined"),
    pytest.param(PaymentUnavailable("provider returned 503"), 503, id="provider-down"),
    pytest.param(PaymentError("provider rejected the request: 401"), 502, id="our-bug"),
])
def test_service_errors_map_to_the_documented_status(raised, status):
    """R9: every failure the service can raise has a documented status,
    and the body is always JSON."""
    response = api(StubOrderService(raises=raised)).post(
        "/orders", json=GOOD_ORDER, headers=HEADERS)
    assert response.status_code == status
    assert response.is_json and "error" in response.get_json()


def test_provider_outage_tells_the_client_when_to_retry():
    stub = StubOrderService(raises=PaymentUnavailable("provider returned 503"))
    response = api(stub).post("/orders", json=GOOD_ORDER, headers=HEADERS)
    assert response.headers["Retry-After"] == "30"


@pytest.mark.parametrize("body, message", [
    pytest.param(["MUG", 2], "must be a JSON object", id="not-an-object"),
    pytest.param({"sku": "MUG", "quantity": 2}, "missing field(s): customer_email", id="missing"),
    pytest.param({**GOOD_ORDER, "quantity": 0}, "positive integer", id="zero"),
    pytest.param({**GOOD_ORDER, "quantity": "2"}, "positive integer", id="string-quantity"),
    pytest.param({**GOOD_ORDER, "customer_email": "ana"}, "email address", id="bad-email"),
])
def test_invalid_bodies_never_reach_the_service(body, message):
    """R11: validate at the boundary."""
    stub = StubOrderService()
    response = api(stub).post("/orders", json=body, headers=HEADERS)
    assert response.status_code == 400
    assert message in response.get_json()["error"]
    assert stub.calls == []


def test_missing_api_key_never_reaches_the_service():
    """R8."""
    stub = StubOrderService()
    response = api(stub).post("/orders", json=GOOD_ORDER)
    assert response.status_code == 401
    assert stub.calls == []


def test_unknown_route_answers_in_json_not_html():
    """R9."""
    response = api(StubOrderService()).get("/order/1", headers=HEADERS)
    assert response.status_code == 404
    assert response.is_json
