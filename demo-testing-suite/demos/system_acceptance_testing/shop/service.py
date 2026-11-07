"""Placing an order: the component that ties pricing, the database, and
the payment provider together."""

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
        subtotal, discount, total = self.pricing(
            product["price_cents"], quantity, coupon
        )  # raises InvalidCoupon before anything is reserved or charged

        # One transaction: the stock and the pending order are saved
        # together, or (if anything raises) not at all.
        with self.connection:
            if not self.repository.reserve_stock(sku, quantity):
                raise OutOfStock(sku)
            order_id = self.repository.create_order(
                sku, quantity, customer_email,
                subtotal_cents=subtotal, discount_cents=discount,
                total_cents=total, coupon=coupon.upper() if coupon else None,
            )

        # The charge cannot join a database transaction: it happens in
        # someone else's system. If it fails, undo our side by hand.
        try:
            charge_id = self.payments.charge(total, reference=f"order-{order_id}")
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

    def list_products(self):
        return self.repository.list_products()

    def health(self):
        """True if the database answers a query."""
        self.connection.execute("SELECT 1").fetchone()
        return True
