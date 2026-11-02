"""All of the shop's SQL, in one place."""


class OrderRepository:
    """Reads and writes products and orders.

    It never commits. The caller (OrderService) decides where each
    transaction starts and ends, with `with connection:` blocks.
    """

    def __init__(self, connection):
        self.connection = connection

    # -- products ---------------------------------------------------------
    def add_product(self, sku, name, price_cents, stock):
        self.connection.execute(
            "INSERT INTO products VALUES (?, ?, ?, ?)",
            (sku, name, price_cents, stock),
        )

    def get_product(self, sku):
        row = self.connection.execute(
            "SELECT * FROM products WHERE sku = ?", (sku,)
        ).fetchone()
        return dict(row) if row else None

    def reserve_stock(self, sku, quantity):
        """Take `quantity` units out of stock. Returns False, and changes
        nothing, if there are not enough."""
        cursor = self.connection.execute(
            "UPDATE products SET stock = stock - ? WHERE sku = ? AND stock >= ?",
            (quantity, sku, quantity),
        )
        return cursor.rowcount == 1

    def release_stock(self, sku, quantity):
        self.connection.execute(
            "UPDATE products SET stock = stock + ? WHERE sku = ?", (quantity, sku)
        )

    # -- orders: create, read, update, delete ------------------------------
    def create_order(self, sku, quantity, total_cents, customer_email):
        cursor = self.connection.execute(
            "INSERT INTO orders (sku, quantity, total_cents, customer_email) "
            "VALUES (?, ?, ?, ?)",
            (sku, quantity, total_cents, customer_email),
        )
        return cursor.lastrowid

    def get_order(self, order_id):
        row = self.connection.execute(
            "SELECT * FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        return dict(row) if row else None

    def update_order(self, order_id, status, charge_id=None):
        self.connection.execute(
            "UPDATE orders SET status = ?, charge_id = ? WHERE id = ?",
            (status, charge_id, order_id),
        )

    def delete_order(self, order_id):
        cursor = self.connection.execute(
            "DELETE FROM orders WHERE id = ?", (order_id,)
        )
        return cursor.rowcount == 1
