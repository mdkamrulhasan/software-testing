"""A one-test All-Defs set that leaves a branch untested.

Run from demo-testing-suite/:

    pytest demos/data_flow/test_receipt.py \
        --cov=receipt --cov-branch --cov-report=term-missing

The single test below satisfies All-Defs for total_with_tax() (see
receipt.py's docstring for the def/use table), yet the report shows a
branch gap: 75% overall, BrPart 1 (the `if` only ever went one way),
and line 33 -- the print() on the True branch -- in the Missing
column. All-Defs did not force it.

To reach All-Uses (and, with it, 100% branch coverage), add the test
in the comment at the bottom and re-run.
"""

import pytest

from receipt import total_with_tax


def test_total_without_breakdown():
    assert total_with_tax(100, False) == pytest.approx(106.0)


# All-Uses also needs the pairs amount -> print, tax -> print, and
# show_breakdown -> `if` (true). One more test covers all three:
#
# def test_total_with_breakdown(capsys):
#     assert total_with_tax(100, True) == pytest.approx(106.0)
#     assert capsys.readouterr().out == "subtotal=100.00 tax=6.00\n"
