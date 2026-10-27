"""IP3 + IP5: OrderService with a real database and the fake PayFast.

Bottom-up integration, step 2: the repository and the payment client
have each been tested on their own; now the service that coordinates
them. The checks look at *both* sides of every interaction -- what the
database committed and what the provider charged -- because the
interesting failures are disagreements between the two.

    SHOP_SERVICE=buggy pytest tests/test_order_service.py
"""

import sqlite3

import pytest

from shop.errors import OutOfStock, PaymentDeclined, PaymentUnavailable


def test_successful_order_charges_exactly_the_order_total(service, provider, stock):
    """R2: the amount that flows to PayFast is the amount we recorded."""
    order = service.place_order("MUG", 2, "ana@example.com")

    assert order["status"] == "paid"
    assert order["charge_id"] == "ch_1"
    assert order["total_cents"] == 2500
    assert provider.charges[0]["amount"] == order["total_cents"]
    assert stock("MUG") == 3


def test_out_of_stock_charges_nothing(service, provider, connection):
    with pytest.raises(OutOfStock):
        service.place_order("TEE", 1, "ana@example.com")
    assert provider.requests == []
    assert connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0] == 0


def test_declined_payment_gives_the_stock_back(service, provider, stock):
    """R4: the charge failed after the stock was committed; the service
    must undo its own side by hand."""
    provider.config["MODE"] = "decline"
    with pytest.raises(PaymentDeclined):
        service.place_order("MUG", 2, "ana@example.com")
    assert stock("MUG") == 5
    assert service.get_order(1)["status"] == "payment_failed"


def test_provider_outage_gives_the_stock_back(service, provider, stock):
    """R4."""
    provider.config["MODE"] = "unavailable"
    with pytest.raises(PaymentUnavailable):
        service.place_order("MUG", 2, "ana@example.com")
    assert stock("MUG") == 5
    assert service.get_order(1)["status"] == "payment_failed"


def test_order_the_database_rejects_leaves_stock_untouched(service, provider, stock):
    """R3: the database refuses the order (NOT NULL customer_email), so
    the stock reservation in the same transaction must be undone too."""
    with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
        service.place_order("MUG", 2, customer_email=None)
    assert stock("MUG") == 5
    assert provider.requests == []
