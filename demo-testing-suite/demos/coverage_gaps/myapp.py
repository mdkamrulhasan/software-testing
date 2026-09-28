def apply_membership_discount(price, is_member):
    if is_member:
        price = price * 0.9
    return price
