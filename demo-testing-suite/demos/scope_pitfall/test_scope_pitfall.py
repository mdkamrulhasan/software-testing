"""Run me on my own: pytest demos/scope_pitfall -v

test_first_order_is_recorded passes by itself. test_second_order_sees_
only_its_own_order was written by someone who assumed a fresh, empty
list -- true under the default scope="function", but false here, since
conftest.py in this folder deliberately uses scope="session". Run in
file order, the second test fails because "order-1" from the first test
is still sitting in the shared list. That order-dependence is exactly
what "flaky" means: whether this test passes can depend on what ran
before it, not on whether the code under test is correct.

Fix: open conftest.py in this folder, change scope="session" to
scope="function", and rerun -- both tests now pass regardless of order,
because each gets its own fresh empty list.
"""


def test_first_order_is_recorded(shared_pending_orders):
    shared_pending_orders.append("order-1")
    assert "order-1" in shared_pending_orders


def test_second_order_sees_only_its_own_order(shared_pending_orders):
    shared_pending_orders.append("order-2")
    assert shared_pending_orders == ["order-2"]
