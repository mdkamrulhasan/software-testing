"""OrderService as a *unit*: every collaborator is a mock.

This is the Week 4 style of test, and it is a good one: fast, focused,
and it pins down the service's own decisions (charge only after stock
is reserved; release the stock if the charge fails). But mocks have no
transactions, no constraints, and no wire format. Run

    SHOP_SERVICE=buggy  pytest tests/test_order_service_unit.py
    SHOP_PAYMENTS=v1    pytest tests/test_order_service_unit.py

Both still pass. The defects live *between* components, so only the
integration tests in the other files can see them.
"""

from unittest.mock import MagicMock, create_autospec

import pytest

from shop.errors import OutOfStock, PaymentDeclined
from shop.repository import OrderRepository
from tests.variants import OrderService, PaymentClient


@pytest.fixture
def repository():
    repository = create_autospec(OrderRepository, instance=True)
    repository.get_product.return_value = {"sku": "MUG", "price_cents": 1250}
    repository.reserve_stock.return_value = True
    repository.create_order.return_value = 1
    return repository


@pytest.fixture
def payments():
    return create_autospec(PaymentClient, instance=True)


@pytest.fixture
def service(repository, payments):
    return OrderService(MagicMock(), repository, payments)  # MagicMock: supports `with`


def test_charges_the_total_after_reserving_stock(service, repository, payments):
    payments.charge.return_value = "ch_1"
    service.place_order("MUG", 2, "ana@example.com")
    repository.reserve_stock.assert_called_once_with("MUG", 2)
    payments.charge.assert_called_once_with(2500, reference="order-1")
    repository.update_order.assert_called_with(1, "paid", "ch_1")


def test_out_of_stock_never_charges(service, repository, payments):
    repository.reserve_stock.return_value = False
    with pytest.raises(OutOfStock):
        service.place_order("MUG", 2, "ana@example.com")
    payments.charge.assert_not_called()


def test_declined_charge_releases_the_stock(service, repository, payments):
    payments.charge.side_effect = PaymentDeclined("card_declined")
    with pytest.raises(PaymentDeclined):
        service.place_order("MUG", 2, "ana@example.com")
    repository.release_stock.assert_called_once_with("MUG", 2)
    repository.update_order.assert_called_with(1, "payment_failed")
