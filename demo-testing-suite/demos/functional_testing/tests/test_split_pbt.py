from hypothesis import given, strategies as st
from shop.split import split_bill

@given(
    total_cents=st.integers(min_value=0, max_value=100_000),
    people=st.integers(min_value=1, max_value=10),
)
def test_shares_add_up_to_total(total_cents, people):
    total = total_cents / 100
    shares = split_bill(total, people)
    assert len(shares) == people
    assert round(sum(shares), 2) == total
