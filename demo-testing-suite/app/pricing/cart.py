"""Shopping-cart total calculation.

Paired with the fixtures in tests/pricing/conftest.py (sample_cart,
empty_cart, cart_with_one_item) to demonstrate basic fixtures and
fixtures that depend on other fixtures.
"""


def cart_total(cart):
    """Return the total price of every line item in ``cart``.

    Args:
        cart: A dict shaped like
            {"items": [{"name": str, "price": float, "quantity": int}, ...]}

    Returns:
        The sum of price * quantity across every item in the cart.
    """
    return sum(item["price"] * item["quantity"] for item in cart["items"])
