"""Transaction classification -- control-flow-graph examples.

These are the two running examples from the Week 5 reading
*Control-Flow Graphs and Statement, Branch, and Path Coverage*,
transcribed verbatim so students can draw the CFG from real code and
then check their hand-computed coverage against coverage.py. See
tests/payments/test_transactions.py.

  - classify_transaction(): three decisions and no loops. The CFG is a
    tree with exactly four entry-to-exit paths, so V(G) = 3 + 1 = 4 and
    four tests achieve full statement, branch, *and* path coverage.
  - contains_negative(): a loop with an early return. The back edge
    makes the number of paths grow with the input length, so full path
    coverage is infeasible. V(G) = 2 + 1 = 3 basis paths are tested
    instead.
"""


def classify_transaction(amount, is_international):
    if amount < 0:
        return "invalid"
    if is_international:
        if amount > 1000:
            return "flagged"
        else:
            return "international"
    else:
        return "domestic"


def contains_negative(numbers):
    for n in numbers:
        if n < 0:
            return True
    return False
