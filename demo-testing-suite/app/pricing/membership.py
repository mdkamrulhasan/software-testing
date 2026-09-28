"""Membership discount -- the statement-vs-branch coverage example.

Transcribed from the Week 5 reading's "The Limitation of Statement
Coverage" section. A single test with ``is_member=True`` executes every
statement in this function (100% statement coverage) while never taking
the ``is_member=False`` branch (50% branch coverage).

tests/pricing/test_membership.py covers both branches. For a
reproduction of the reading's partially covered pytest-cov report
(``2->4`` in the Missing column), see demos/coverage_gaps/.
"""


def apply_membership_discount(price, is_member):
    if is_member:
        price = price * 0.9
    return price
