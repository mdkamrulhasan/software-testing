import pytest

HEADERS = {"X-API-Key": "shop-key"}


def order_body(sku="MUG", quantity=1, email="customer@example.com", coupon=None):
    body = {"sku": sku, "quantity": quantity, "customer_email": email}
    if coupon is not None:
        body["coupon"] = coupon
    return body


def post_order(client, **kwargs):
    return client.post("/orders", json=order_body(**kwargs), headers=HEADERS)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

def test_health_returns_ok_without_api_key(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_health_ignores_wrong_api_key(client):
    response = client.get("/health", headers={"X-API-Key": "wrong"})
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("method, path", [
    ("get", "/products"),
    ("post", "/orders"),
    ("get", "/orders/1"),
])
def test_missing_api_key_is_rejected(client, method, path):
    response = getattr(client, method)(path)
    assert response.status_code == 401
    assert response.get_json() == {"error": "missing or invalid API key"}


def test_wrong_api_key_is_rejected(client):
    response = client.get("/products", headers={"X-API-Key": "nope"})
    assert response.status_code == 401


# ---------------------------------------------------------------------------
# Products
# ---------------------------------------------------------------------------

def test_list_products_returns_all_products_sorted_by_sku(client):
    response = client.get("/products", headers=HEADERS)
    assert response.status_code == 200
    products = response.get_json()
    assert [p["sku"] for p in products] == ["MUG", "STICKER", "TEE"]
    mug = products[0]
    assert mug == {"sku": "MUG", "name": "Coffee mug", "price_cents": 1250, "stock": 5}


def test_list_products_reflects_stock_after_order(client):
    post_order(client, sku="MUG", quantity=2)
    products = client.get("/products", headers=HEADERS).get_json()
    mug = next(p for p in products if p["sku"] == "MUG")
    assert mug["stock"] == 3


# ---------------------------------------------------------------------------
# Placing orders: success
# ---------------------------------------------------------------------------

def test_place_order_success(client, provider, stock):
    response = post_order(client, sku="MUG", quantity=2)
    assert response.status_code == 201
    order = response.get_json()
    assert order["sku"] == "MUG"
    assert order["quantity"] == 2
    assert order["subtotal_cents"] == 2500
    assert order["discount_cents"] == 0
    assert order["total_cents"] == 2500
    assert order["coupon"] is None
    assert order["status"] == "paid"
    assert order["charge_id"] == "ch_1"
    assert order["customer_email"] == "customer@example.com"
    assert response.headers["Location"] == f"/orders/{order['id']}"
    assert stock("MUG") == 3
    assert len(provider.charges) == 1
    assert provider.charges[0]["amount"] == 2500


def test_order_can_be_fetched_by_id(client):
    created = post_order(client, sku="STICKER", quantity=4).get_json()
    response = client.get(f"/orders/{created['id']}", headers=HEADERS)
    assert response.status_code == 200
    assert response.get_json() == created


def test_order_ids_increase(client):
    first = post_order(client).get_json()
    second = post_order(client).get_json()
    assert second["id"] == first["id"] + 1


def test_ordering_entire_stock_is_allowed(client, stock):
    response = post_order(client, sku="MUG", quantity=5)
    assert response.status_code == 201
    assert stock("MUG") == 0


def test_maximum_quantity_is_accepted(client):
    response = post_order(client, sku="STICKER", quantity=100)
    assert response.status_code == 201
    assert response.get_json()["total_cents"] == 30000


# ---------------------------------------------------------------------------
# Coupons
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sku, quantity, coupon, subtotal, discount, total", [
    ("MUG", 1, "SAVE10", 1250, 125, 1125),
    ("MUG", 2, "SAVE10", 2500, 250, 2250),
    ("STICKER", 3, "SAVE10", 900, 90, 810),
    ("MUG", 1, "FLAT5", 1250, 500, 750),
    ("MUG", 2, "FLAT5", 2500, 1000, 1500),
    ("MUG", 1, "save10", 1250, 125, 1125),
    ("MUG", 1, "flat5", 1250, 500, 750),
])
def test_coupon_pricing(client, provider, sku, quantity, coupon, subtotal, discount, total):
    response = post_order(client, sku=sku, quantity=quantity, coupon=coupon)
    assert response.status_code == 201
    order = response.get_json()
    assert order["subtotal_cents"] == subtotal
    assert order["discount_cents"] == discount
    assert order["total_cents"] == total
    assert order["coupon"] == coupon.upper()
    assert provider.charges[-1]["amount"] == total


def test_flat5_rejected_for_cheap_item(client, provider, stock):
    response = post_order(client, sku="STICKER", quantity=4, coupon="FLAT5")
    assert response.status_code == 400
    assert response.get_json() == {"error": "FLAT5 requires an order of at least $10.00"}
    assert provider.charges == []
    assert stock("STICKER") == 100


def test_unknown_coupon_is_rejected(client, provider, stock):
    response = post_order(client, sku="MUG", quantity=1, coupon="BOGUS")
    assert response.status_code == 400
    assert response.get_json() == {"error": "unknown coupon code: BOGUS"}
    assert provider.charges == []
    assert stock("MUG") == 5


# ---------------------------------------------------------------------------
# Placing orders: validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("body, message", [
    (None, "request body must be a JSON object"),
    ([1, 2], "request body must be a JSON object"),
    ({"quantity": 1, "customer_email": "a@b.c"}, "missing field(s): sku"),
    ({"sku": "MUG"}, "missing field(s): quantity, customer_email"),
    ({"sku": 5, "quantity": 1, "customer_email": "a@b.c"}, "sku must be a string"),
    ({"sku": "MUG", "quantity": 0, "customer_email": "a@b.c"},
     "quantity must be an integer from 1 to 100"),
    ({"sku": "MUG", "quantity": 101, "customer_email": "a@b.c"},
     "quantity must be an integer from 1 to 100"),
    ({"sku": "MUG", "quantity": "2", "customer_email": "a@b.c"},
     "quantity must be an integer from 1 to 100"),
    ({"sku": "MUG", "quantity": True, "customer_email": "a@b.c"},
     "quantity must be an integer from 1 to 100"),
    ({"sku": "MUG", "quantity": 1, "customer_email": "not-an-email"},
     "customer_email must be an email address"),
    ({"sku": "MUG", "quantity": 1, "customer_email": "a@b.c", "coupon": 10},
     "coupon must be a string"),
])
def test_invalid_order_bodies_are_rejected(client, provider, body, message):
    if body is None:
        response = client.post("/orders", data="not json", headers=HEADERS)
    else:
        response = client.post("/orders", json=body, headers=HEADERS)
    assert response.status_code == 400
    assert response.get_json() == {"error": message}
    assert provider.charges == []


# ---------------------------------------------------------------------------
# Placing orders: failures
# ---------------------------------------------------------------------------

def test_unknown_product_is_404(client, provider):
    response = post_order(client, sku="NOPE")
    assert response.status_code == 404
    assert response.get_json() == {"error": "unknown sku: NOPE"}
    assert provider.charges == []


def test_out_of_stock_is_409(client, provider, stock):
    response = post_order(client, sku="TEE")
    assert response.status_code == 409
    assert response.get_json() == {"error": "insufficient stock"}
    assert provider.charges == []
    assert stock("TEE") == 0


def test_more_than_stock_is_409(client, stock):
    response = post_order(client, sku="MUG", quantity=6)
    assert response.status_code == 409
    assert stock("MUG") == 5


def test_declined_payment_is_402_and_stock_released(client, provider, stock):
    provider.config["MODE"] = "decline"
    response = post_order(client, sku="MUG", quantity=2)
    assert response.status_code == 402
    assert response.get_json() == {"error": "payment declined"}
    assert stock("MUG") == 5
    order = client.get("/orders/1", headers=HEADERS).get_json()
    assert order["status"] == "payment_failed"
    assert order["charge_id"] is None


def test_provider_unavailable_is_503_with_retry_after(client, provider, stock):
    provider.config["MODE"] = "unavailable"
    response = post_order(client, sku="MUG", quantity=1)
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "30"
    assert response.get_json() == {"error": "payment provider unavailable"}
    assert stock("MUG") == 5
    order = client.get("/orders/1", headers=HEADERS).get_json()
    assert order["status"] == "payment_failed"


# ---------------------------------------------------------------------------
# Fetching orders
# ---------------------------------------------------------------------------

def test_unknown_order_is_404(client):
    response = client.get("/orders/999", headers=HEADERS)
    assert response.status_code == 404
    assert response.get_json() == {"error": "order not found"}


def test_unknown_route_returns_json_404(client):
    response = client.get("/does-not-exist", headers=HEADERS)
    assert response.status_code == 404
    assert response.get_json() == {"error": "not found"}


def test_wrong_method_returns_json_405(client):
    response = client.delete("/products", headers=HEADERS)
    assert response.status_code == 405
    assert response.get_json() == {"error": "method not allowed"}
