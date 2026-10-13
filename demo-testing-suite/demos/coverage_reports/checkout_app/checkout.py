"""A small checkout module used in the Week 7 coverage examples."""


def subtotal(items):
    total = 0.0
    for price, qty in items:
        if qty < 0:
            raise ValueError("quantity cannot be negative")
        total += price * qty
    return total


def apply_coupon(amount, code):
    if code == "SAVE10":
        amount = amount * 0.90
    elif code == "FLAT5":
        amount = max(amount - 5, 0)
    return round(amount, 2)


def shipping_fee(amount, is_member):
    if is_member or amount >= 50:
        return 0.0
    return 7.99


def format_receipt(amount):
    return f"Total due: ${amount:.2f}"
