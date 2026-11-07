"""Functional system tests: end-to-end scenarios against the running shop.

Each test is a short use-case scenario that a customer could actually
perform, checked only through what the system exposes: HTTP responses,
and what PayFast says it charged. No database access, no imports from
shop/. The requirement IDs (specs/system_requirements.md) are in the
test names' docstrings for traceability.
"""

import pytest

pytestmark = pytest.mark.system


def test_browse_order_and_look_the_order_up(shop):
    """SYS-1, SYS-2, SYS-3: the main success scenario."""
    catalog = shop.get("/products").json()
    mug = next(p for p in catalog if p["sku"] == "MUG")
    assert (mug["price_cents"], mug["stock"]) == (1250, 5)

    placed = shop.order("MUG", 2)
    assert placed.status_code == 201
    order = placed.json()
    assert (order["status"], order["total_cents"]) == ("paid", 2500)

    assert shop.get(placed.headers["Location"]).json() == order
    assert shop.stock("MUG") == 3
    assert [c["amount"] for c in shop.charges()] == [2500]


def test_sold_out_product_is_refused_and_nothing_is_charged(shop):
    """SYS-2, SYS-5."""
    response = shop.order("TEE", 1)
    assert response.status_code == 409
    assert shop.charges() == []


def test_declined_card_charges_nothing_and_returns_the_stock(shop):
    """SYS-5: and the failed order is still on record."""
    shop.provider(mode="decline")
    response = shop.order("MUG", 2)

    assert response.status_code == 402
    assert shop.stock("MUG") == 5
    assert shop.charges() == []
    assert shop.get("/orders/1").json()["status"] == "payment_failed"


def test_several_customers_one_after_another(shop):
    """SYS-4, sequentially: stock and charges add up."""
    for email in ["ana@example.com", "ben@example.com", "cy@example.com"]:
        assert shop.order("MUG", 1, email=email).status_code == 201
    assert shop.stock("MUG") == 2
    assert len(shop.charges()) == 3
    assert shop.order("MUG", 3).status_code == 409    # only 2 left
