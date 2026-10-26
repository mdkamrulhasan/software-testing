"""The reading's pairwise rows, plugged into pytest (Section 8.2).

The reading leaves this test's body as ``...``. Run as written, all ten
rows would PASS without checking anything -- Week 7's "100% coverage,
zero assertions" trap. There is no checkout() function to call yet, and
each row still needs an expected result from the specification (Section
8.3, "It does not supply expected results"), so every row is skipped
with that reason instead. ``pytest --collect-only`` shows the 10 cases.
"""
import pytest
from allpairspy import AllPairs

from pairwise import params


@pytest.mark.parametrize("payment, delivery, customer, coupon",
                         [tuple(r) for r in AllPairs(params)])
def test_checkout_pairwise(payment, delivery, customer, coupon):
    pytest.skip("no oracle yet: each pairwise row still needs an expected "
                "result from the specification (reading, Section 8.3)")
