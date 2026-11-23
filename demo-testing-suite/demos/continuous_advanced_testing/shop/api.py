"""The shop's HTTP API (specs/shop_api.md, v1.1), built with Flask."""

from flask import Flask, jsonify, request

from shop.errors import (
    InvalidCoupon, OutOfStock, PaymentDeclined, PaymentError,
    PaymentUnavailable, UnknownProduct,
)

MAX_QUANTITY = 100


def create_app(service, api_key):
    app = Flask(__name__)

    def error(status, message, headers=None):
        return jsonify(error=message), status, headers or {}

    @app.before_request
    def require_api_key():
        if request.path == "/health":
            return None  # SYS-6: probes from a load balancer carry no key
        if request.headers.get("X-API-Key") != api_key:
            return error(401, "missing or invalid API key")

    @app.get("/health")
    def health():
        try:
            service.health()
        except Exception:
            return jsonify(status="unavailable"), 503
        return jsonify(status="ok")

    @app.get("/products")
    def list_products():
        return jsonify(service.list_products())

    @app.post("/orders")
    def place_order():
        body = request.get_json(silent=True)
        problem = validate_order(body)
        if problem:
            return error(400, problem)
        try:
            order = service.place_order(
                body["sku"], body["quantity"], body["customer_email"],
                body.get("coupon"),
            )
        except InvalidCoupon as exc:
            return error(400, str(exc))
        except UnknownProduct:
            return error(404, f"unknown sku: {body['sku']}")
        except OutOfStock:
            return error(409, "insufficient stock")
        except PaymentDeclined:
            return error(402, "payment declined")
        except PaymentUnavailable:
            return error(503, "payment provider unavailable", {"Retry-After": "30"})
        except PaymentError:
            return error(502, "payment provider rejected the request")
        return jsonify(order), 201, {"Location": f"/orders/{order['id']}"}

    @app.get("/orders/<int:order_id>")
    def get_order(order_id):
        order = service.get_order(order_id)
        if order is None:
            return error(404, "order not found")
        return jsonify(order)

    @app.errorhandler(404)
    @app.errorhandler(405)
    def json_errors(exc):  # Flask's defaults are HTML pages
        return error(exc.code, exc.name.lower())

    @app.errorhandler(500)
    def internal_error(exc):  # SYS-7: never an HTML page or a stack trace
        return error(500, "internal error")

    return app


def validate_order(body):
    """Return a message describing what is wrong with `body`, or None."""
    if not isinstance(body, dict):
        return "request body must be a JSON object"
    missing = [f for f in ("sku", "quantity", "customer_email") if f not in body]
    if missing:
        return f"missing field(s): {', '.join(missing)}"
    if not isinstance(body["sku"], str):                      # Week 11, finding F1
        return "sku must be a string"
    if type(body["quantity"]) is not int or not 1 <= body["quantity"] <= MAX_QUANTITY:
        return f"quantity must be an integer from 1 to {MAX_QUANTITY}"  # Week 11, F1
    if not isinstance(body["customer_email"], str) or "@" not in body["customer_email"]:
        return "customer_email must be an email address"
    if "coupon" in body and not isinstance(body["coupon"], str):
        return "coupon must be a string"
    return None
