"""IP1-IP6: the fully assembled shop, driven through its HTTP API.

Everything is real except PayFast, which is the fake, over real HTTP.
These are the shop's end-to-end integration tests: few, and each one
crosses every integration point. When one fails, it says *that*
something is wrong, not *where* -- try

    SHOP_PAYMENTS=v1 pytest tests/test_api.py

and then ask which of the six integration points is to blame.
"""

HEADERS = {"X-API-Key": "shop-key"}
ORDER = {"sku": "MUG", "quantity": 2, "customer_email": "ana@example.com"}


def test_place_an_order_and_fetch_it_back(client):
    response = client.post("/orders", json=ORDER, headers=HEADERS)

    assert response.status_code == 201
    assert response.headers["Location"] == "/orders/1"
    assert response.get_json() == {
        "id": 1, "sku": "MUG", "quantity": 2, "total_cents": 2500,
        "customer_email": "ana@example.com", "status": "paid", "charge_id": "ch_1",
    }
    fetched = client.get(response.headers["Location"], headers=HEADERS)
    assert fetched.status_code == 200
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


def test_provider_outage_is_503_with_retry_after(client, provider, stock):
    provider.config["MODE"] = "unavailable"
    response = client.post("/orders", json=ORDER, headers=HEADERS)
    assert response.status_code == 503
    assert response.headers["Retry-After"] == "30"
    assert stock("MUG") == 5


def test_wrong_provider_key_is_502_not_503(client, payments, monkeypatch, stock):
    """R8: deployed with the wrong PayFast key. That is our fault, and
    "try again in 30 seconds" would be the wrong advice."""
    monkeypatch.setattr(payments, "api_key", "sk_wrong_key")
    response = client.post("/orders", json=ORDER, headers=HEADERS)
    assert response.status_code == 502
    assert stock("MUG") == 5
