"""Data-flow-driven tests for app/billing/charges.py.

Follows the Week 6 reading (*Data-Flow Testing and Coverage Concepts*).
Each test id names the coverage criterion it contributes to and the
def-use (DU) pairs it newly covers, numbered as in the reading's table:

    #  var    def      use              covered by
    1  total  D1 (S1)  S4 (c-use)       all-defs:one-charge
    2  total  D1 (S1)  S5 (c-use)       all-defs:credit-only
    3  total  D2 (S4)  S4 (c-use)       all-uses:two-charges  (loop-carried)
    4  total  D2 (S4)  S5 (c-use)       all-defs:one-charge
    5  n      S2       S3 true (p-use)  all-defs:one-charge
    6  n      S2       S3 false (p-use) all-defs:credit-only
    7  n      S2       S4 (c-use)       all-defs:one-charge

- The two ``all-defs`` cases alone satisfy All-Defs (every definition
  reaches at least one use) -- and, in this small function, 100%
  branch coverage too. They still miss pair #3.
- ``all-uses:two-charges`` adds pair #3, completing All-Uses: D2 from
  one iteration reaches S4 again on the next.
- ``du-path:loop-carried-via-credit`` exercises pair #3 along a
  *different* def-clear path: the back edge from S3's false outcome
  (a skipped credit between two charges). It adds no new DU pair, so
  All-Uses does not require it; it is the kind of extra path
  All-DU-Paths asks for (see the reading's All-DU-Paths warning box).

Why pair #3 matters: demos/data_flow/accumulator_bug.py breaks exactly
that pair. The two all-defs tests still pass against it, with 100%
branch coverage; only the two-charge test fails.
"""

import pytest

from app.billing.charges import sum_positive


@pytest.mark.parametrize(
    "numbers, expected",
    [
        pytest.param([-1], 0, id="all-defs:credit-only"),
        pytest.param([3], 3, id="all-defs:one-charge"),
        pytest.param([3, 5], 8, id="all-uses:two-charges"),
        pytest.param([3, -2, 5], 8, id="du-path:loop-carried-via-credit"),
    ],
)
def test_sum_positive_du_pairs(numbers, expected):
    assert sum_positive(numbers) == expected
