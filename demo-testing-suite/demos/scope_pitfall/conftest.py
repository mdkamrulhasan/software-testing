"""Deliberately-broken demo for "Common Pitfall: Wide Scope + Mutable
State = Flaky Tests".

Do not copy this fixture's scope choice into real code -- that is the
entire point. Run this folder on its own, separately from the main
suite (pytest.ini excludes demos/ from the default `pytest` run):

    pytest demos/scope_pitfall -v

Then, live, change scope="session" below to scope="function", rerun,
and show both tests now pass regardless of order.
"""

import pytest


@pytest.fixture(scope="session")
def shared_pending_orders():
    """A single mutable list, shared by EVERY test in the whole run
    because scope="session". This is the anti-pattern: a session-scoped
    fixture that returns something mutable, which more than one test
    then mutates.
    """
    return []
