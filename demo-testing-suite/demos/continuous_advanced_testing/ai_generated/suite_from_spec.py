"""Tests for the shop's HTTP API, derived from specs/shop_api.md,
specs/user_stories.md (US-1 to US-3), and specs/system_requirements.md."""

import pytest

HEADERS = {"X-API-Key": "shop-key"}


def place(client, sku="MUG", quantity=1, coupon=None, email="ana@example.com"):
    body = {"sku": sku, "quantity": quantity, "customer_email": email}
    if coupon is not None:
        body["coupon"] = coupon
    return client.post("/orders", json=body, headers=HEADERS)


def assert_json_error(response, status):
    assert response.status_code == status
    assert response.is_json
    body = response.get_json()
    assert isinstance(body, dict) and isinstance(body.get("error"), str)


# --- GET /health (NFR-3, SYS-6) ----------------------------------------------

def test_health_needs_no_api_key(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_stays_ok_when_the_provider_is_down(client, provider):
    provider.config["MODE"] = "unavailable"
    assert client.get("/health").get_json() == {"status": "ok"}


# --- API key (SYS-6) -----------------------------------------------------------

@pytest.mark.parametrize("method, path", [
    ("GET", "/products"), ("POST", "/orders"), ("GET", "/orders/1"),
])
@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "wrong-key"}])
def test_every_endpoint_but_health_requires_the_key(client, provider, method, path, headers):
    response = client.open(path, method=method, headers=headers,
                           json={"sku": "MUG", "quantity": 1, "customer_email": "a@b.c"})
    assert_json_error(response, 401)
    assert provider.charges == []


# --- GET /products (SYS-1, US-1) ----------------------------------------------

def test_products_are_listed_by_sku_with_name_price_and_stock(client):
    response = client.get("/products", headers=HEADERS)
    assert response.status_code == 200
    assert response.get_json() == [
        {"sku": "MUG", "name": "Coffee mug", "price_cents": 1250, "stock": 5},
        {"sku": "STICKER", "name": "Laptop sticker", "price_cents": 300, "stock": 100},
        {"sku": "TEE", "name": "T-shirt", "price_cents": 2000, "stock": 0},
    ]


def test_buying_reduces_the_stock_shown(client):
    place(client, "MUG", 2)
    products = {p["sku"]: p for p in client.get("/products", headers=HEADERS).get_json()}
    assert products["MUG"]["stock"] == 3


# --- POST /orders, success (SYS-2, US-2) ---------------------------------------

def test_an_order_is_paid_charged_and_can_be_fetched(client, provider, stock):
    response = place(client, "MUG", 2)

    assert response.status_code == 201
    order = response.get_json()
    assert order == {
        "id": order["id"], "sku": "MUG", "quantity": 2, "subtotal_cents": 2500,
        "discount_cents": 0, "total_cents": 2500, "coupon": None,
        "customer_email": "ana@example.com", "status": "paid",
        "charge_id": order["charge_id"],
    }
    assert isinstance(order["charge_id"], str) and order["charge_id"]
    assert response.headers["Location"] == f"/orders/{order['id']}"
    assert [c["amount"] for c in provider.charges] == [2500]
    assert stock("MUG") == 3

    fetched = client.get(response.headers["Location"], headers=HEADERS)
    assert fetched.status_code == 200
    assert fetched.get_json() == order


@pytest.mark.parametrize("quantity", [1, 100])
def test_quantity_boundaries_are_accepted(client, quantity):
    response = place(client, "STICKER", quantity)
    assert response.status_code == 201
    assert response.get_json()["total_cents"] == 300 * quantity


def test_the_whole_stock_can_be_bought(client, stock):
    assert place(client, "MUG", 5).status_code == 201
    assert stock("MUG") == 0


# --- Coupons (SYS-9, US-3) -------------------------------------------------------

@pytest.mark.parametrize("sku, quantity, code, subtotal, discount, total", [
    ("MUG", 1, "SAVE10", 1250, 125, 1125),      # US-3.1
    ("MUG", 3, "SAVE10", 3750, 375, 3375),      # US-3.1, whole order
    ("MUG", 1, "FLAT5", 1250, 500, 750),        # US-3.2
    ("MUG", 2, "FLAT5", 2500, 500, 2000),       # US-3.2: once per order, not per unit
    ("STICKER", 4, "FLAT5", 1200, 500, 700),    # US-3.3: the order's $12 qualifies
    ("MUG", 1, "save10", 1250, 125, 1125),      # US-3.4
    ("MUG", 1, "Flat5", 1250, 500, 750),        # US-3.4
])
def test_a_valid_coupon_reduces_the_amount_charged(client, provider, sku, quantity, code,
                                                   subtotal, discount, total):
    response = place(client, sku, quantity, coupon=code)

    assert response.status_code == 201
    order = response.get_json()
    assert (order["subtotal_cents"], order["discount_cents"], order["total_cents"]) == (
        subtotal, discount, total)                                      # US-3.6
    assert order["coupon"] == code.upper()
    assert [c["amount"] for c in provider.charges] == [total]


def test_save10_rounds_the_discount_down(client, connection, provider):
    with connection:
        connection.execute(
            "INSERT INTO products (sku, name, price_cents, stock) VALUES ('PEN', 'Gel pen', 199, 50)")
    order = place(client, "PEN", 1, coupon="SAVE10").get_json()
    assert (order["discount_cents"], order["total_cents"]) == (19, 180)  # US-3.1 example
    assert [c["amount"] for c in provider.charges] == [180]


@pytest.mark.parametrize("sku, quantity", [("STICKER", 3), ("MUG", 0 + 0 or 0) if False else ("STICKER", 1)])
def test_flat5_needs_an_order_of_at_least_ten_dollars(client, provider, stock, sku, quantity):
    response = place(client, sku, quantity, coupon="FLAT5")
    assert_json_error(response, 400)                                    # US-3.3
    assert provider.charges == []
    assert stock(sku) == 100


def test_flat5_works_at_exactly_ten_dollars(client, connection, provider):
    with connection:
        connection.execute(
            "INSERT INTO products (sku, name, price_cents, stock) VALUES ('BOOK', 'Notebook', 500, 10)")
    order = place(client, "BOOK", 2, coupon="FLAT5").get_json()
    assert (order["subtotal_cents"], order["total_cents"]) == (1000, 500)


def test_an_unknown_coupon_is_rejected_and_nothing_is_charged(client, provider, stock):
    response = place(client, "MUG", 1, coupon="FREESTUFF")
    assert_json_error(response, 400)                                    # US-3.5
    assert "FREESTUFF" in response.get_json()["error"]
    assert provider.charges == []
    assert stock("MUG") == 5


# --- POST /orders, rejected requests (shop_api.md, SYS-7) --------------------------

@pytest.mark.parametrize("body", [
    {"quantity": 1, "customer_email": "a@b.c"},
    {"sku": "MUG", "customer_email": "a@b.c"},
    {"sku": "MUG", "quantity": 1},
    {"sku": "MUG", "quantity": 0, "customer_email": "a@b.c"},
    {"sku": "MUG", "quantity": 101, "customer_email": "a@b.c"},
    {"sku": "MUG", "quantity": 1.5, "customer_email": "a@b.c"},
    {"sku": "MUG", "quantity": "1", "customer_email": "a@b.c"},
    {"sku": ["MUG"], "quantity": 1, "customer_email": "a@b.c"},
    {"sku": "MUG", "quantity": 1, "customer_email": "no-at-sign"},
    {"sku": "MUG", "quantity": 1, "customer_email": "a@b.c", "coupon": 5},
    ["not", "an", "object"],
])
def test_a_body_that_breaks_a_rule_is_400_and_nothing_is_charged(client, provider, stock, body):
    response = client.post("/orders", json=body, headers=HEADERS)
    assert_json_error(response, 400)
    assert provider.charges == []
    assert stock("MUG") == 5


def test_a_body_that_is_not_json_is_400(client):
    response = client.post("/orders", data="sku=MUG", headers=HEADERS,
                           content_type="text/plain")
    assert_json_error(response, 400)


def test_an_unknown_sku_is_404(client, provider):
    assert_json_error(place(client, "NOPE"), 404)
    assert provider.charges == []


@pytest.mark.parametrize("sku, quantity", [("TEE", 1), ("MUG", 6)])
def test_not_enough_stock_is_409_and_nothing_is_charged(client, provider, stock, sku, quantity):
    before = stock(sku)
    assert_json_error(place(client, sku, quantity), 409)               # US-2.3
    assert provider.charges == []
    assert stock(sku) == before


# --- POST /orders, payment failures (SYS-5, US-2.4) --------------------------------

def test_a_declined_card_is_402_not_charged_and_the_stock_is_released(client, provider, stock):
    provider.config["MODE"] = "decline"
    response = place(client, "MUG", 2)
    assert_json_error(response, 402)
    assert provider.charges == []
    assert stock("MUG") == 5
    assert client.get("/orders/1", headers=HEADERS).get_json()["status"] == "payment_failed"


def test_a_provider_outage_is_503_with_retry_after_and_the_stock_is_released(client, provider, stock):
    provider.config["MODE"] = "unavailable"
    response = place(client, "MUG", 2)
    assert_json_error(response, 503)
    assert response.headers["Retry-After"] == "30"
    assert provider.charges == []
    assert stock("MUG") == 5


def test_orders_work_again_after_the_provider_recovers(client, provider, stock):
    provider.config["MODE"] = "unavailable"
    place(client, "MUG", 1)
    provider.config["MODE"] = "normal"
    assert place(client, "MUG", 1).status_code == 201                  # NFR-2
    assert stock("MUG") == 4


# --- GET /orders/<id> (SYS-3) and unknown routes (SYS-7) ---------------------------

def test_an_unknown_order_is_404(client):
    assert_json_error(client.get("/orders/12345", headers=HEADERS), 404)


def test_an_unknown_route_is_a_json_404(client):
    assert_json_error(client.get("/no/such/route", headers=HEADERS), 404)
