"""Non-functional system tests: many customers at the same time.

These need the shop running as a real, multi-threaded server: Flask's
in-process test client handles one request at a time, so no test in
tests/integration/ can do this. Try

    SHOP_SERVICE=racy pytest tests/integration    # all pass
    SHOP_SERVICE=racy pytest tests/system/test_concurrency_and_performance.py
"""

import statistics
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
import requests

pytestmark = pytest.mark.system


def order_all_at_once(shop, bodies):
    """Send every order at (nearly) the same moment, one thread per
    customer. Returns [(status_code, seconds), ...] in input order."""
    start_line = threading.Barrier(len(bodies))

    def customer(body):
        start_line.wait()                        # everyone starts together
        started = time.perf_counter()
        response = requests.post(f"{shop.url}/orders", json=body, timeout=10,
                                 headers={"X-API-Key": "shop-key"})
        return response.status_code, time.perf_counter() - started

    with ThreadPoolExecutor(max_workers=len(bodies)) as pool:
        return list(pool.map(customer, bodies))


def test_ten_customers_race_for_the_last_five_mugs(shop):
    """SYS-4: exactly 5 orders succeed, 5 are refused, nothing is
    oversold. PayFast takes 0.2 s per charge, as on a slow day."""
    shop.provider(delay=0.2)
    bodies = [{"sku": "MUG", "quantity": 1, "customer_email": f"c{i}@example.com"}
              for i in range(10)]

    statuses = sorted(status for status, _ in order_all_at_once(shop, bodies))

    assert statuses == [201] * 5 + [409] * 5
    assert shop.stock("MUG") == 0
    assert len(shop.charges()) == 5            # 5 mugs, 5 charges


def test_ten_simultaneous_orders_each_answered_within_a_second(shop):
    """NFR-1: 10 customers at once, PayFast answering in 100 ms."""
    shop.provider(delay=0.1)
    bodies = [{"sku": "STICKER", "quantity": 1, "customer_email": f"c{i}@example.com"}
              for i in range(10)]

    results = order_all_at_once(shop, bodies)
    seconds = sorted(t for _, t in results)

    print(f"\nlatency: median {statistics.median(seconds):.3f} s, "
          f"max {seconds[-1]:.3f} s")
    assert all(status == 201 for status, _ in results)
    assert seconds[-1] < 1.0
