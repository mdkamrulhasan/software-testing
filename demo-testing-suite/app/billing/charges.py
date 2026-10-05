"""Statement charges -- the data-flow testing worked example.

Week 6 reading: *Data-Flow Testing and Coverage Concepts*.

sum_positive() is the reading's worked example, transcribed verbatim
(including its S1-S5 statement labels), so students can trace
definitions, uses, and def-use (DU) pairs on real code. In billing
terms: a statement's line items are charges (positive) and
credits/refunds (zero or negative); only the charges are summed.

Def/use events (reading, "Definitions and Uses"):

    S1  total = 0              def total (D1)
    S2  for n in numbers:      def n (fresh each iteration)
    S3  if n > 0:              p-use n
    S4  total = total + n      c-use total, c-use n; def total (D2)
    S5  return total           c-use total

The seven DU pairs, and the tests that cover each, are listed in
tests/billing/test_charges.py. The interesting one is pair #3: D2 at
S4 reaches the *same* statement S4 on a later loop iteration (a
loop-carried pair), so no single-pass test can exercise it.
"""


def sum_positive(numbers):
    total = 0                  # S1
    for n in numbers:          # S2
        if n > 0:              # S3
            total = total + n  # S4
    return total               # S5
