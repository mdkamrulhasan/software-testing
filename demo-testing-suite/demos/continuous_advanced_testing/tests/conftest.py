"""The system test harness: start the shop as a separate process, the
way it is deployed, and talk to it only over HTTP.

Shared by tests/system/ and tests/acceptance/. (tests/integration/ has
its own conftest.py, which assembles components inside the test
process instead.)

Each test gets its own server, database file, and fake PayFast, so
tests can run in any order. Starting a server takes about half a
second; that is the price of testing the real thing.
"""

import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import requests

DEMO_DIR = Path(__file__).resolve().parent.parent
SHOP_API_KEY = "shop-key"
STARTUP_TIMEOUT = 10  # seconds


class RunningShop:
    """A handle on one running shop: its URLs, and a few helpers that
    do nothing a real HTTP client could not do."""

    def __init__(self, process, url, provider_url, db_path, log_path):
        self.process = process
        self.url = url
        self.provider_url = provider_url
        self.db_path = db_path
        self.log_path = log_path
        self.http = requests.Session()
        self.http.headers["X-API-Key"] = SHOP_API_KEY

    # -- the shop's own API ------------------------------------------------
    def get(self, path, **kwargs):
        return self.http.get(self.url + path, timeout=10, **kwargs)

    def post(self, path, **kwargs):
        return self.http.post(self.url + path, timeout=10, **kwargs)

    def order(self, sku, quantity, email="ana@example.com", coupon=None):
        body = {"sku": sku, "quantity": quantity, "customer_email": email}
        if coupon is not None:
            body["coupon"] = coupon
        return self.post("/orders", json=body)

    def stock(self, sku):
        products = self.get("/products").json()
        return next(p["stock"] for p in products if p["sku"] == sku)

    # -- the fake PayFast's test-only controls ------------------------------
    def provider(self, **changes):
        """e.g. shop.provider(mode="decline") or shop.provider(delay=0.2)"""
        requests.post(f"{self.provider_url}/_test/config", json=changes, timeout=5)

    def charges(self):
        """What PayFast actually charged -- the customer's side of the story."""
        return requests.get(f"{self.provider_url}/_test/charges", timeout=5).json()

    # -- the process -------------------------------------------------------
    def stop(self):
        self.http.close()
        self.process.terminate()
        self.process.wait(timeout=5)


def _start(tmp_path, db_path, seed=None, extra_args=()):
    """Run serve.py and wait for its READY line."""
    args = [sys.executable, "serve.py", "--port", "0", "--db", str(db_path), *extra_args]
    if seed is not None:
        seed_file = tmp_path / "seed.json"
        seed_file.write_text(json.dumps(seed))
        args += ["--seed", str(seed_file)]
    log_path = tmp_path / "server.log"
    log = open(log_path, "a")
    process = subprocess.Popen(args, cwd=DEMO_DIR, stdout=subprocess.PIPE,
                               stderr=log, text=True)
    log.close()

    lines = queue.Queue()
    threading.Thread(target=lambda: lines.put(process.stdout.readline()),
                     daemon=True).start()
    try:
        line = lines.get(timeout=STARTUP_TIMEOUT)
    except queue.Empty:
        line = ""
    if not line.startswith("READY"):
        process.kill()
        pytest.fail(f"shop did not start; see {log_path}:\n{log_path.read_text()}")
    fields = dict(part.split("=", 1) for part in line.split()[1:])
    shop = RunningShop(process, fields["shop"], fields["provider"], db_path, log_path)
    assert shop.get("/health").status_code == 200  # ready means healthy
    return shop


@pytest.fixture
def start_shop(tmp_path):
    """Factory: start_shop(seed=[...]) starts a shop; every shop started
    is stopped when the test ends. Pass `restart_of=shop` to stop a
    shop and start a new one on the same database (SYS-8)."""
    started = []

    def start(seed=None, restart_of=None, extra_args=()):
        if restart_of is not None:
            restart_of.stop()
            db_path = restart_of.db_path
        else:
            db_path = tmp_path / "shop.db"
        shop = _start(tmp_path, db_path, seed, extra_args)
        started.append(shop)
        return shop

    yield start
    for shop in started:
        if shop.process.poll() is None:
            shop.stop()


@pytest.fixture
def shop(start_shop):
    """The shop, running, with the default catalog:
    MUG $12.50 x5, STICKER $3.00 x100, TEE $20.00 x0."""
    return start_shop()
