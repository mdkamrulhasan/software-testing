"""Reproduces the Week 5 reading's "Measuring Coverage in Practice" report.

myapp.py is a line-for-line copy of apply_membership_discount (no
docstring on purpose, so its line numbers match the reading: line 2 is
the `if`, line 4 is the `return`). This file deliberately tests only
the member branch. Run it from demo-testing-suite/:

    pytest demos/coverage_gaps/test_myapp.py \
        --cov=myapp --cov-branch --cov-report=term-missing

and the report shows 100% of statements but 83% overall, with `2->4`
in the Missing column: the False edge from line 2 straight to line 4
was never taken. Drop --cov-branch and the same run reports 100%, the
"deceptively complete" number the reading warns about.

The real, fully covered suite for this function lives in
tests/pricing/test_membership.py.
"""

import pytest

from myapp import apply_membership_discount


def test_member_gets_ten_percent_off():
    assert apply_membership_discount(100, True) == pytest.approx(90)
