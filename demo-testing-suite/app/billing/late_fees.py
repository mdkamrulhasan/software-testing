"""Late-fee calculation for overdue library books.

This is the running example from Lecture 1 (Testing Foundations). It is
carried forward UNCHANGED into this lecture on purpose: the negative-days
bug discovered in Lecture 1 is still here, and this week's tests
(tests/billing/test_late_fees.py) document it with @pytest.mark.xfail
instead of silently fixing it. See the note below for why that matters
pedagogically.
"""


def calculate_late_fee(days_late, daily_rate=1.50, max_fee=25.00):
    """Return the late fee (in dollars) for an overdue library book.

    Args:
        days_late: Number of days the book is overdue. The implementation
            below assumes this is non-negative -- see KNOWN BUG.
        daily_rate: Dollars charged per day late.
        max_fee: The late fee never exceeds this cap.

    Returns:
        The fee as a float, capped at ``max_fee``.

    KNOWN BUG (introduced deliberately in Lecture 1, still present):
        Nothing here validates that ``days_late`` is non-negative. A
        negative value produces a *negative* fee, which makes no business
        sense. The fault has been present since Lecture 1; it only
        produces a visible failure when a test happens to supply a
        negative ``days_late`` -- that gap between "fault exists" and
        "failure observed" is the whole point of Lecture 1's chain-of-
        events discussion.

        Do NOT "fix" this without first reading
        tests/billing/test_late_fees.py -- the xfail case there is
        intentionally testing for this exact (buggy) behavior, and a
        silent fix would turn an expected-failure into a confusing
        "XPASS" the next time someone runs the suite.
    """
    fee = days_late * daily_rate
    if fee > max_fee:
        return max_fee
    return fee
