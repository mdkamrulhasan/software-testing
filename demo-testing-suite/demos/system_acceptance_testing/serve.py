"""Run the whole shop as one system: the shop's API, its SQLite
database, and the fake PayFast, each a real server.

    python serve.py                          # shop on :8000, fake PayFast on :8001
    python serve.py --port 0                 # any free ports (the system tests do this)
    python serve.py --db shop.db             # keep the database between runs
    python serve.py --seed catalog.json      # start with these products
    python serve.py --provider-mode decline  # or: unavailable; --provider-delay 0.2

When both servers are listening it prints one line,

    READY shop=http://127.0.0.1:8000 provider=http://127.0.0.1:8001

which is what tests/conftest.py waits for. A new database is seeded
from --seed (default: MUG $12.50 x5, STICKER $3.00 x100, TEE $20.00
sold out); an existing one is never re-seeded, so stock survives a
restart (SYS-8). Stop with Ctrl-C. See README.md for curl commands.
"""

import argparse
import json
import logging
import sys
import tempfile
import threading
from pathlib import Path

from werkzeug.serving import make_server

from fakes.payment_provider import create_provider
from shop import db
from shop.api import create_app
from shop.payments import PaymentClient
from shop.repository import OrderRepository
from variants import OrderService, price_order

PROVIDER_SECRET = "sk_test_123"
SHOP_API_KEY = "shop-key"
DEFAULT_CATALOG = [
    {"sku": "MUG", "name": "Coffee mug", "price_cents": 1250, "stock": 5},
    {"sku": "STICKER", "name": "Laptop sticker", "price_cents": 300, "stock": 100},
    {"sku": "TEE", "name": "T-shirt", "price_cents": 2000, "stock": 0},
]


def prepare_database(path, catalog):
    """Create the schema; seed `catalog` only if there are no products yet."""
    connection = db.connect(path)
    try:
        db.create_schema(connection)
        repository = OrderRepository(connection)
        if not repository.list_products():
            with connection:
                for product in catalog:
                    repository.add_product(**product)
    finally:
        connection.close()


class PerRequestService:
    """sqlite3 connections belong to one thread, and the server handles
    each request on its own thread: so every call opens a fresh
    connection, builds the real service on it, and closes it after."""

    def __init__(self, path, provider_url):
        self.path = path
        self.provider_url = provider_url

    def _call(self, method, *args):
        connection = db.connect(self.path)
        try:
            payments = PaymentClient(self.provider_url, PROVIDER_SECRET, timeout=5.0)
            service = OrderService(connection, OrderRepository(connection), payments,
                                   pricing=price_order)
            return getattr(service, method)(*args)
        finally:
            connection.close()

    def place_order(self, *args):
        return self._call("place_order", *args)

    def get_order(self, order_id):
        return self._call("get_order", order_id)

    def list_products(self):
        return self._call("list_products")

    def health(self):
        return self._call("health")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000,
                        help="shop port; PayFast gets the next one (0: any free ports)")
    parser.add_argument("--db", help="database file (default: a new temporary one)")
    parser.add_argument("--seed", help="JSON list of products for a new database")
    parser.add_argument("--provider-mode", default="normal",
                        choices=["normal", "decline", "unavailable"])
    parser.add_argument("--provider-delay", type=float, default=0.0)
    args = parser.parse_args()
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    provider = create_provider(secret=PROVIDER_SECRET)
    provider.config.update(MODE=args.provider_mode, DELAY=args.provider_delay)
    provider_port = args.port + 1 if args.port else 0
    provider_server = make_server("127.0.0.1", provider_port, provider, threaded=True)
    threading.Thread(target=provider_server.serve_forever, daemon=True).start()
    provider_url = f"http://127.0.0.1:{provider_server.port}"

    path = Path(args.db) if args.db else Path(tempfile.mkdtemp()) / "shop.db"
    catalog = json.loads(Path(args.seed).read_text()) if args.seed else DEFAULT_CATALOG
    prepare_database(path, catalog)

    shop = create_app(PerRequestService(path, provider_url), api_key=SHOP_API_KEY)
    shop_server = make_server("127.0.0.1", args.port, shop, threaded=True)
    print(f"READY shop=http://127.0.0.1:{shop_server.port} provider={provider_url}",
          flush=True)
    print(f"      X-API-Key: {SHOP_API_KEY}   database: {path}", file=sys.stderr,
          flush=True)
    try:
        shop_server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
