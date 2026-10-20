def shipping_fee(amount, is_member, express):                         # buggy
    if is_member or amount >= 50:
        return 0.0
    if express:
        return 10.0 if is_member else 15.0
    return 7.99
