"""A broken loop-carried DU pair that branch coverage cannot see.

Week 6 reading: *Data-Flow Testing and Coverage Concepts*, pair #3 of
the sum_positive() worked example (D2 at S4 reaching S4 again on a
later iteration).

KNOWN BUG (deliberate, for the "killed definition" pattern):
    S4 should read ``total = total + n``. The ``0 +`` means the value
    D2 stored on the previous iteration is never read: each charge
    overwrites (kills) the running total instead of adding to it. The
    loop-carried DU pair no longer exists, and the function returns
    the *last* positive charge instead of the sum.

Every statement and both branch outcomes still execute exactly as
written. See test_accumulator_bug.py: a test set that satisfies
All-Defs reaches 100% branch coverage here and passes; only the
All-Uses test with two positive charges fails.

The correct version lives in app/billing/charges.py.
"""


def sum_positive(numbers):
    total = 0                  # S1
    for n in numbers:          # S2
        if n > 0:              # S3
            total = 0 + n      # S4  KNOWN BUG -- should be total + n
    return total               # S5
