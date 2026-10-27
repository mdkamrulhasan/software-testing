"""Placing an order -- with a transaction bug.

KNOWN BUG (deliberate, for the "database inconsistency" demo): the
stock reservation and the order insert are committed in two separate
transactions. If the insert fails (here: the database rejects a NULL
customer_email), the stock stays reserved for an order that does not
exist. A unit test with a mocked repository cannot see this: mocks have
no transactions and no NOT NULL constraints. See
tests/test_order_service.py.
"""

from shop.errors import OutOfStock, PaymentError, UnknownProduct


class OrderService:
    def __init__(self, connection, repository, payments):
        self.connection = connection
        self.repository = repository
        self.payments = payments

    def place_order(self, sku, quantity, customer_email):
        product = self.repository.get_product(sku)
        if product is None:
            raise UnknownProduct(sku)
        total_cents = product["price_cents"] * quantity

        with self.connection:  # KNOWN BUG: commits the stock on its own...
            if not self.repository.reserve_stock(sku, quantity):
                raise OutOfStock(sku)
        with self.connection:  # ...before the order insert can fail
            order_id = self.repository.create_order(
                sku, quantity, total_cents, customer_email
            )

        # The charge cannot join a database transaction: it happens in
        # someone else's system. If it fails, undo our side by hand.
        try:
            charge_id = self.payments.charge(total_cents, reference=f"order-{order_id}")
        except PaymentError:
            with self.connection:
                self.repository.release_stock(sku, quantity)
                self.repository.update_order(order_id, "payment_failed")
            raise

        with self.connection:
            self.repository.update_order(order_id, "paid", charge_id)
        return self.repository.get_order(order_id)

    def get_order(self, order_id):
        return self.repository.get_order(order_id)
