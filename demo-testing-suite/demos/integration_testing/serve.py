"""Run the whole shop locally, for trying the API by hand with curl.

    python serve.py                         # shop on :8000, fake PayFast on :8001
    python serve.py --provider-mode decline  # or: unavailable

The database is a fresh temporary file seeded with MUG ($12.50, 5 in
stock) and TEE ($20.00, out of stock). Stop with Ctrl-C. See README.md
for curl commands.
"""

import argparse
import tempfile
import threading
from pathlib import Path

from werkzeug.serving import make_server

from fakes.payment_provider import create_provider
from shop import db
from shop.api import create_app
from shop.payments import PaymentClient
from shop.repository import OrderRepository
from shop.service import OrderService


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--provider-mode", default="normal",
                        choices=["normal", "decline", "unavailable"])
    args = parser.parse_args()

    provider = create_provider(secret="sk_test_123")
    provider.config["MODE"] = args.provider_mode
    provider_server = make_server("127.0.0.1", args.port + 1, provider, threaded=True)
    threading.Thread(target=provider_server.serve_forever, daemon=True).start()

    path = Path(tempfile.mkdtemp()) / "shop.db"
    connection = db.connect(path)
    db.create_schema(connection)
    repository = OrderRepository(connection)
    with connection:
        repository.add_product("MUG", "Coffee mug", price_cents=1250, stock=5)
        repository.add_product("TEE", "T-shirt", price_cents=2000, stock=0)
    connection.close()

    def service_for_this_request():
        # sqlite3 connections belong to one thread; open one per request.
        connection = db.connect(path)
        payments = PaymentClient(f"http://127.0.0.1:{args.port + 1}", "sk_test_123")
        return OrderService(connection, OrderRepository(connection), payments)

    class PerRequestService:
        def place_order(self, *args):
            return service_for_this_request().place_order(*args)

        def get_order(self, order_id):
            return service_for_this_request().get_order(order_id)

    shop = create_app(PerRequestService(), api_key="shop-key")
    print(f"shop API     http://127.0.0.1:{args.port}   (X-API-Key: shop-key)")
    print(f"fake PayFast http://127.0.0.1:{args.port + 1}  (mode: {args.provider_mode})")
    print(f"database     {path}", flush=True)
    make_server("127.0.0.1", args.port, shop, threaded=True).serve_forever()


if __name__ == "__main__":
    main()
