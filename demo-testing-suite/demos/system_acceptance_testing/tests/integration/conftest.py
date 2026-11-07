"""Fixtures that assemble the shop from real parts *inside the test
process* -- Week 10's integration-level harness, carried over.

Every test gets its own SQLite file and its own fake PayFast server on a
free local port. Compare tests/conftest.py, which runs the shop as a
separate process for the system and acceptance tests.
"""

import logging
import threading

import pytest
from werkzeug.serving import make_server

from fakes.payment_provider import create_provider
from shop import db
from shop.api import create_app
from shop.payments import PaymentClient
from shop.repository import OrderRepository
from variants import OrderService, price_order

PROVIDER_SECRET = "sk_test_123"
SHOP_API_KEY = "shop-key"

logging.getLogger("werkzeug").setLevel(logging.ERROR)


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "shop.db"


@pytest.fixture
def connection(db_path):
    connection = db.connect(db_path)
    db.create_schema(connection)
    repository = OrderRepository(connection)
    with connection:
        repository.add_product("MUG", "Coffee mug", price_cents=1250, stock=5)
        repository.add_product("STICKER", "Laptop sticker", price_cents=300, stock=100)
        repository.add_product("TEE", "T-shirt", price_cents=2000, stock=0)
    yield connection
    connection.close()


@pytest.fixture
def repository(connection):
    return OrderRepository(connection)


@pytest.fixture
def stock(db_path):
    """Read a product's stock through a *new* connection: this sees only
    what was committed."""
    def read(sku):
        fresh = db.connect(db_path)
        try:
            return fresh.execute(
                "SELECT stock FROM products WHERE sku = ?", (sku,)
            ).fetchone()["stock"]
        finally:
            fresh.close()
    return read


@pytest.fixture
def provider():
    """The fake PayFast, served over real HTTP on a free port."""
    app = create_provider(secret=PROVIDER_SECRET)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(
        target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
    )
    thread.start()
    app.url = f"http://127.0.0.1:{server.port}"
    yield app
    server.shutdown()
    thread.join()


@pytest.fixture
def payments(provider):
    return PaymentClient(provider.url, PROVIDER_SECRET, timeout=1.0)


@pytest.fixture
def service(connection, repository, payments):
    return OrderService(connection, repository, payments, pricing=price_order)


@pytest.fixture
def client(service):
    """An in-process HTTP client (Flask's test client) for the assembled shop."""
    return create_app(service, api_key=SHOP_API_KEY).test_client()
