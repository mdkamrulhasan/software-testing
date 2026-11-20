"""FLAKY ON PURPOSE (Week 13): a timing assumption with no headroom.

PayFast is set to take 0.10 s per charge, and the test allows the whole
order 0.11 s. On an idle laptop the shop's own work (about 8 ms) fits
in the other 0.01 s most of the time; on a busy CI runner, or with
other tests running in parallel, it often does not. The code is not wrong; the test
is. Run it many times to see:

    python tools/rerun.py 20 flaky_examples/flaky_timing.py                   # idle
    python tools/rerun.py 10 flaky_examples/flaky_timing.py tests/system -n 2 # busy

Not collected by a plain `pytest` (its name does not start with test_).
"""

import time


def test_an_order_takes_about_a_tenth_of_a_second(shop):
    shop.provider(delay=0.10)
    started = time.perf_counter()
    assert shop.order("MUG", 1).status_code == 201
    assert time.perf_counter() - started < 0.11      # no headroom: flaky
