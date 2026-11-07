"""IP1-IP6: the assembled shop through Flask's in-process test client
(Week 10's end-to-end integration tests), carried over.

Same requests as a system test would send -- but the shop is not
running as a server, there is one thread, and the test can reach inside
(`stock`, `provider.config`). tests/system/ removes all three.
"""

HEADERS = {"X-API-Key": "shop-key"}
ORDER = {"sku": "MUG", "quantity": 2, "customer_email": "ana@example.com"}


def test_place_an_order_and_fetch_it_back(client):
    response = client.post("/orders", json=ORDER, headers=HEADERS)

    assert response.status_code == 201
    assert response.headers["Location"] == "/orders/1"
    assert response.get_json() == {
        "id": 1, "sku": "MUG", "quantity": 2,
        "subtotal_cents": 2500, "discount_cents": 0, "total_cents": 2500,
        "coupon": None, "customer_email": "ana@example.com",
        "status": "paid", "charge_id": "ch_1",
    }
    fetched = client.get(response.headers["Location"], headers=HEADERS)
    assert fetched.get_json() == response.get_json()


def test_out_of_stock_is_409(client, provider):
    response = client.post("/orders", json={**ORDER, "sku": "TEE"}, headers=HEADERS)
    assert response.status_code == 409
    assert provider.requests == []


def test_declined_card_is_402_and_the_stock_comes_back(client, provider, stock):
    provider.config["MODE"] = "decline"
    response = client.post("/orders", json=ORDER, headers=HEADERS)
    assert response.status_code == 402
    assert stock("MUG") == 5


def test_unknown_coupon_is_400(client, provider):
    response = client.post("/orders", json={**ORDER, "coupon": "BOGUS"}, headers=HEADERS)
    assert response.status_code == 400
    assert response.get_json() == {"error": "unknown coupon code: BOGUS"}
    assert provider.requests == []


def test_health_needs_no_api_key(client):
    assert client.get("/health").get_json() == {"status": "ok"}
