"""Placing an order -- "take the stock only once the money is in".

KNOWN DEFECT (deliberate, for the system testing demo): to avoid
holding stock for payments that fail, this version checks the stock,
charges the card, and only then writes the new stock -- computed from
the value it read *before* the charge. One customer at a time, that is
correct, and every integration test passes (tests/integration/). With
several customers at once, they all read the same stock while their
charges are in flight, and each writes back "stock minus my quantity":
the shop sells units it does not have and loses track of the rest.
Only a test that drives the running system concurrently can see it.
See tests/system/test_concurrency_and_performance.py.
"""

from shop.errors import OutOfStock, PaymentError, UnknownProduct
from shop.pricing import price_order


class OrderService:
    def __init__(self, connection, repository, payments, *, pricing=price_order):
        self.connection = connection
        self.repository = repository
        self.payments = payments
        self.pricing = pricing

    def place_order(self, sku, quantity, customer_email, coupon=None):
        product = self.repository.get_product(sku)
        if product is None:
            raise UnknownProduct(sku)
        if product["stock"] < quantity:                 # check...
            raise OutOfStock(sku)
        subtotal, discount, total = self.pricing(
            product["price_cents"], quantity, coupon
        )

        with self.connection:
            order_id = self.repository.create_order(
                sku, quantity, customer_email,
                subtotal_cents=subtotal, discount_cents=discount,
                total_cents=total, coupon=coupon.upper() if coupon else None,
            )

        # Nothing to give back if the charge fails: no stock is held yet.
        try:
            charge_id = self.payments.charge(total, reference=f"order-{order_id}")
        except PaymentError:
            with self.connection:
                self.repository.update_order(order_id, "payment_failed")
            raise

        with self.connection:                            # ...then act, on a stale value
            self.repository.set_stock(sku, product["stock"] - quantity)  # KNOWN DEFECT
            self.repository.update_order(order_id, "paid", charge_id)
        return self.repository.get_order(order_id)

    def get_order(self, order_id):
        return self.repository.get_order(order_id)

    def list_products(self):
        return self.repository.list_products()

    def health(self):
        self.connection.execute("SELECT 1").fetchone()
        return True
