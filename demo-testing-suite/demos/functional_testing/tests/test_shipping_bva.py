import pytest
from shop.shipping import shipping_fee

@pytest.mark.parametrize("amount, expected", [(49.99, 7.99), (50.0, 0.0)])
def test_free_shipping_boundary(amount, expected):
    assert shipping_fee(amount, False, False) == expected
