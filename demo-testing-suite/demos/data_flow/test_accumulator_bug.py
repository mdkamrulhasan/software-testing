"""All-Defs + 100% branch coverage, and the bug survives.

Run from demo-testing-suite/:

    pytest demos/data_flow/test_accumulator_bug.py -v \
        --cov=accumulator_bug --cov-branch --cov-report=term-missing

The two ``all-defs`` tests are the reading's All-Defs set ([-1] and
[3]). They pass, and coverage.py reports 100% statement and branch
coverage. The ``all-uses`` test -- the one that exercises the
loop-carried pair #3 -- is the only one that fails, because it is the
only test in which a running total has to survive into a later
iteration.

That is the reading's warning made concrete: "100% branch coverage on
a function with an accumulator ... says nothing about whether the
accumulated value was ever actually checked after more than one
update."

The FAIL is intentional. demos/ is not part of a plain `pytest` run
(pytest.ini sets testpaths = tests), so this cannot affect the main
suite's baseline.
"""

import pytest

from accumulator_bug import sum_positive


@pytest.mark.parametrize(
    "numbers, expected",
    [
        pytest.param([-1], 0, id="all-defs:credit-only"),
        pytest.param([3], 3, id="all-defs:one-charge"),
    ],
)
def test_all_defs_set_passes(numbers, expected):
    assert sum_positive(numbers) == expected


def test_all_uses_two_charges_exposes_the_bug():
    # Pair #3: the running total from the first charge must reach S4
    # again on the second iteration. With the bug it never does.
    assert sum_positive([3, 5]) == 8
