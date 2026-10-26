import pytest
from shop.shipping import shipping_fee

@pytest.mark.parametrize("amount, is_member, express, expected", [
    pytest.param(20.0, True,  True,  10.0, id="R1-member-express"),
    pytest.param(20.0, False, True,  15.0, id="R2-guest-express"),
    pytest.param(20.0, True,  False,  0.0, id="R3-member-standard"),
    pytest.param(80.0, False, False,  0.0, id="R4-guest-standard-50plus"),
    pytest.param(20.0, False, False, 7.99, id="R5-guest-standard-under50"),
])
def test_shipping_decision_table(amount, is_member, express, expected):
    assert shipping_fee(amount, is_member, express) == expected
