"""The shop's HTTP API (specs/shop_api.md), built with Flask."""

from flask import Flask, jsonify, request

from shop.errors import (
    OutOfStock, PaymentDeclined, PaymentError, PaymentUnavailable, UnknownProduct,
)


def create_app(service, api_key):
    app = Flask(__name__)

    def error(status, message, headers=None):
        return jsonify(error=message), status, headers or {}

    @app.before_request
    def require_api_key():
        if request.headers.get("X-API-Key") != api_key:
            return error(401, "missing or invalid API key")

    @app.post("/orders")
    def place_order():
        body = request.get_json(silent=True)
        problem = validate_order(body)
        if problem:
            return error(400, problem)
        try:
            order = service.place_order(
                body["sku"], body["quantity"], body["customer_email"]
            )
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

    return app


def validate_order(body):
    """Return a message describing what is wrong with `body`, or None."""
    if not isinstance(body, dict):
        return "request body must be a JSON object"
    missing = [f for f in ("sku", "quantity", "customer_email") if f not in body]
    if missing:
        return f"missing field(s): {', '.join(missing)}"
    if type(body["quantity"]) is not int or body["quantity"] < 1:
        return "quantity must be a positive integer"
    if not isinstance(body["customer_email"], str) or "@" not in body["customer_email"]:
        return "customer_email must be an email address"
    return None
