"""FLAKY ON PURPOSE (Week 13): one test depends on another having run first.

To save time, the two tests share one shop (a module-scoped fixture),
and the second test looks up the order the first one placed. Run the
file and both pass. Run the second test alone -- or let pytest-xdist
send the two tests to different workers, each with its own shop -- and
it fails, although nothing in the shop changed:

    pytest flaky_examples/flaky_order.py                         # 2 passed
    pytest flaky_examples/flaky_order.py -k look_the_order_up    # 1 failed: 404
    pytest flaky_examples/flaky_order.py -n 2                    # 1 failed: 404

The test passed for months, until the pipeline started running tests in
parallel. The fix is not `--dist loadfile` (which keeps the file on one
worker and hides the problem); it is a test that places its own order.

Not collected by a plain `pytest` (its name does not start with test_).
"""

import pytest

from tests.conftest import _start


@pytest.fixture(scope="module")
def one_shop(tmp_path_factory):
    """One shop for the whole module: faster, and the cause of the problem."""
    tmp = tmp_path_factory.mktemp("one_shop")
    shop = _start(tmp, tmp / "shop.db")
    yield shop
    shop.stop()


def test_place_an_order(one_shop):
    assert one_shop.order("MUG", 2).status_code == 201


def test_look_the_order_up(one_shop):
    order = one_shop.get("/orders/1")            # placed by the test above... if it ran
    assert order.status_code == 200
    assert order.json()["quantity"] == 2
