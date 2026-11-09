"""OrderService with a real database and the fake PayFast (Week 10's
bottom-up step 2), carried over and extended for coupons.

All of these pass with SHOP_SERVICE=racy too: they place one order at a
time, and one at a time the racy service is correct.

    SHOP_SERVICE=racy pytest tests/integration
"""

import sqlite3

import pytest

from shop.errors import InvalidCoupon, OutOfStock, PaymentDeclined, PaymentUnavailable


def test_successful_order_charges_exactly_the_order_total(service, provider, stock):
    order = service.place_order("MUG", 2, "ana@example.com")

    assert order["status"] == "paid"
    assert order["total_cents"] == 2500
    assert provider.charges[0]["amount"] == order["total_cents"]
    assert stock("MUG") == 3


def test_coupon_discount_is_what_reaches_the_provider(service, provider):
    order = service.place_order("MUG", 1, "ana@example.com", coupon="SAVE10")

    assert (order["subtotal_cents"], order["discount_cents"]) == (1250, 125)
    assert provider.charges[0]["amount"] == order["total_cents"] == 1125


def test_invalid_coupon_reserves_and_charges_nothing(service, provider, stock):
    with pytest.raises(InvalidCoupon):
        service.place_order("MUG", 1, "ana@example.com", coupon="BOGUS")
    assert stock("MUG") == 5
    assert provider.requests == []


def test_out_of_stock_charges_nothing(service, provider, connection):
    with pytest.raises(OutOfStock):
        service.place_order("TEE", 1, "ana@example.com")
    assert provider.requests == []
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_declined_payment_gives_the_stock_back(service, provider, stock):
    provider.config["MODE"] = "decline"
    with pytest.raises(PaymentDeclined):
        service.place_order("MUG", 2, "ana@example.com")
    assert stock("MUG") == 5
    assert service.get_order(1)["status"] == "payment_failed"


def test_provider_outage_gives_the_stock_back(service, provider, stock):
    provider.config["MODE"] = "unavailable"
    with pytest.raises(PaymentUnavailable):
        service.place_order("MUG", 2, "ana@example.com")
    assert stock("MUG") == 5


def test_order_the_database_rejects_leaves_stock_untouched(service, provider, stock):
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        service.place_order("MUG", 2, customer_email=None)
    assert stock("MUG") == 5
    assert provider.requests == []


def test_two_orders_one_after_the_other_keep_stock_right(service, stock):
    """Sequential orders: the racy service passes this too."""
    service.place_order("MUG", 2, "ana@example.com")
    service.place_order("MUG", 2, "ben@example.com")
    assert stock("MUG") == 1
