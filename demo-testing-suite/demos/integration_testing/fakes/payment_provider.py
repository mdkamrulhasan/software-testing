"""A fake PayFast: a small, working implementation of
specs/payment_provider_api.md.

The tests run it on a real local port (see tests/conftest.py), so the
shop's PaymentClient talks to it over real HTTP, through the real
`requests` library, exactly as it would talk to PayFast. Unlike a mock,
it enforces the provider's contract: wrong auth gets a 401, an amount
that is not integer cents gets a 400, and a repeated Idempotency-Key
does not charge twice.

`provider.config["MODE"]` makes it misbehave on purpose:
  "normal"       charge succeeds
  "decline"      402 card_declined
  "unavailable"  503 with an HTML body, as a proxy might send
and `provider.config["DELAY"]` (seconds) makes every response slow.
"""

import itertools
import time

from flask import Flask, jsonify, request


def create_provider(secret):
    provider = Flask(__name__)
    provider.config.update(MODE="normal", DELAY=0.0)
    provider.requests = []  # every request received, for tests to inspect
    provider.charges = []   # every charge actually made
    by_key = {}
    ids = itertools.count(1)

    @provider.post("/v1/charges")
    def create_charge():
        provider.requests.append(request.get_json(silent=True))
        time.sleep(provider.config["DELAY"])
        if provider.config["MODE"] == "unavailable":
            page = "<html><body><h1>503 Service Unavailable</h1></body></html>"
            return page, 503, {"Content-Type": "text/html"}
        if request.headers.get("Authorization") != f"Bearer {secret}":
            return jsonify(error="invalid_api_key"), 401

        body = request.get_json(silent=True) or {}
        amount = body.get("amount")
        if type(amount) is not int or amount <= 0:
            return jsonify(error="amount must be a positive integer number of cents"), 400
        if body.get("currency") != "USD":
            return jsonify(error="unsupported currency"), 400

        key = request.headers.get("Idempotency-Key")
        if key in by_key:
            return jsonify(by_key[key]), 201
        if provider.config["MODE"] == "decline":
            return jsonify(error="card_declined"), 402

        charge = {"id": f"ch_{next(ids)}", "amount": amount,
                  "currency": "USD", "status": "succeeded"}
        provider.charges.append(charge)
        if key:
            by_key[key] = charge
        return jsonify(charge), 201

    return provider
