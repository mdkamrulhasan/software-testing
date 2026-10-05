"""What tests and coverage say about anomalies.py.

Run from demo-testing-suite/:

    pytest demos/data_flow/test_anomalies.py -v \
        --cov=anomalies --cov-branch --cov-report=term-missing

All three tests pass, and statement coverage is 100%: every line,
including both buggy ones, executed. The defects are about which
values reach which uses, not which lines run.

- describe_balance(): branch coverage does show a gap (the elif's
  False edge, i.e. balance == 0, is never taken), but only as a
  missing *edge*. Adding the test at the bottom turns that gap into
  an UnboundLocalError. pylint reports the same defect statically,
  without needing that test.
- apply_payment(): the only test checks a case where the bug is
  invisible (payment == 0). Coverage is 100% statement and branch;
  only pylint's unused-variable warning points at the dead
  definition. A test with a non-zero payment would expose it.
"""

from anomalies import apply_payment, describe_balance


def test_positive_balance_is_credit():
    assert describe_balance(25) == "Account is credit"


def test_negative_balance_is_owing():
    assert describe_balance(-25) == "Account is owing"


def test_zero_payment_leaves_balance_unchanged():
    assert apply_payment(100, 0) == 100


# The missing boundary test. Uncomment it to watch it fail with
# UnboundLocalError:
#
# def test_zero_balance():
#     assert describe_balance(0) == "Account is settled"
