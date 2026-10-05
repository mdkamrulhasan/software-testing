"""Data-flow anomalies found by static analysis, before any test runs.

Week 6 reading: *Data-Flow Testing and Coverage Concepts*, "Why
Data-Flow Testing Matters" (use before def, dead definitions) and
"Data-Flow Testing in Practice" (static analyzers perform def-use
analysis internally).

Run from demo-testing-suite/:

    pylint demos/data_flow/anomalies.py --disable=all \
        --enable=possibly-used-before-assignment,unused-variable

pylint flags both functions below without executing anything. Then
see test_anomalies.py for what the tests and the coverage report say.

KNOWN BUGS (deliberate):

1. describe_balance() -- USE BEFORE DEF. ``status`` is defined on the
   balance > 0 and balance < 0 paths only. On the balance == 0 path
   the return statement reads it before any definition, and Python
   raises UnboundLocalError. (In some languages this silently returns
   garbage or a stale value instead -- the reading's point.)

2. apply_payment() -- DEAD DEFINITION. ``remaining`` is computed and
   never read; the function returns the wrong variable. The
   assignment exists because the author meant it to matter, and the
   fact that nothing reads it is the signal that something is missing.
"""


def describe_balance(balance):
    if balance > 0:
        status = "credit"
    elif balance < 0:
        status = "owing"
    return f"Account is {status}"  # KNOWN BUG -- status undefined when balance == 0


def apply_payment(balance, payment):
    remaining = balance - payment  # KNOWN BUG -- dead definition: never read
    return balance
