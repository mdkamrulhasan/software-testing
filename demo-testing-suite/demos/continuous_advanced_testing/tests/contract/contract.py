"""A small consumer-driven contract checker, in the style of Pact.

The contract (contracts/shop-payfast.json) lists the interactions the
shop relies on: for each, the request the shop sends and the parts of
the response it uses. Both sides are checked against the same file:

  consumer side  test_shop_consumer.py: the shop's PaymentClient, talking
                 to a stub that answers from the contract, must send the
                 requests the contract describes and handle the answers.
  provider side  test_payfast_provider.py: a PayFast (our fake, or the
                 real sandbox) must answer each contract request the way
                 the contract describes.

Matching is *by type*, like Pact's default ("like" matching): every
header and body field listed must be present, with a value of the same
JSON type. Extra headers and fields are allowed, so the provider is free
to add fields and the contract pins only what the consumer uses.
"""

import json
import logging
import threading
from pathlib import Path

from flask import Flask, jsonify, request
from werkzeug.serving import make_server

CONTRACT = Path(__file__).resolve().parents[2] / "contracts" / "shop-payfast.json"

logging.getLogger("werkzeug").setLevel(logging.ERROR)  # one line per request otherwise


def load():
    return json.loads(CONTRACT.read_text())


def interactions():
    return load()["interactions"]


def json_type(value):
    """The JSON type of a decoded value. bool is checked before int,
    because in Python True is an int."""
    for python_type, name in [(bool, "boolean"), (int, "integer"), (float, "number"),
                              (str, "string"), (list, "array"), (dict, "object")]:
        if isinstance(value, python_type):
            return name
    return "null"


def mismatches(expected, actual, where="body"):
    """Every way `actual` fails to match `expected` by type, as messages."""
    if json_type(expected) != json_type(actual):
        return [f"{where}: expected {json_type(expected)} like {expected!r}, got {actual!r}"]
    problems = []
    if isinstance(expected, dict):
        for key, value in expected.items():
            if key not in actual:
                problems.append(f"{where}.{key}: missing")
            else:
                problems.extend(mismatches(value, actual[key], f"{where}.{key}"))
    return problems


def request_mismatches(expected, method, path, headers, body):
    """Does a request the consumer sent match the contract's request?"""
    problems = []
    if method != expected["method"] or path != expected["path"]:
        problems.append(f"request line: expected {expected['method']} {expected['path']}, "
                        f"got {method} {path}")
    sent = {name.lower(): value for name, value in headers.items()}
    for name, value in expected.get("headers", {}).items():
        if name.lower() not in sent:
            problems.append(f"header {name}: missing")
        else:
            problems.extend(mismatches(value, sent[name.lower()], f"header {name}"))
    if "body" in expected:
        problems.extend(mismatches(expected["body"], body, "request body"))
    return problems


def response_mismatches(expected, status, body):
    """Does a response the provider sent match the contract's response?"""
    problems = []
    if status != expected["status"]:
        problems.append(f"status: expected {expected['status']}, got {status}")
    if "body" in expected:
        problems.extend(mismatches(expected["body"], body, "response body"))
    return problems


class Stub:
    """A PayFast that knows only one interaction: it records every request
    and answers with the contract's example response."""

    def __init__(self, interaction):
        self.interaction = interaction
        self.received = []
        app = Flask("payfast-contract-stub")

        @app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
        def answer(path):
            self.received.append({"method": request.method, "path": "/" + path,
                                  "headers": dict(request.headers),
                                  "body": request.get_json(silent=True)})
            response = interaction["response"]
            if "body" in response:
                return jsonify(response["body"]), response["status"]
            return "<html><body>stub</body></html>", response["status"], {"Content-Type": "text/html"}

        self.server = make_server("127.0.0.1", 0, app, threaded=True)
        self.url = f"http://127.0.0.1:{self.server.port}"
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       kwargs={"poll_interval": 0.01}, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.thread.join()

    def mismatches(self):
        expected = self.interaction["request"]
        problems = []
        for number, sent in enumerate(self.received, start=1):
            problems.extend(f"request {number}: {problem}" for problem in request_mismatches(
                expected, sent["method"], sent["path"], sent["headers"], sent["body"]))
        return problems
