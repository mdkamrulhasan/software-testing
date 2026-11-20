"""A stand-in for PayFast's *real* sandbox, after PayFast's next release.

In real life this is not code we have: it is the provider's sandbox
(https://sandbox.payfast.example), which PayFast changes on its own
schedule. Here it is our fake with one change PayFast's release notes
could easily call "minor": a successful charge now returns its id as
`charge_id` instead of `id`.

Nothing in the shop's own test suite notices -- every test talks to
fakes/payment_provider.py, which still says `id`. The provider side of
the contract test does notice, when it is pointed here:

    PAYFAST=sandbox-next pytest tests/contract/test_payfast_provider.py
"""

import json

from flask import request

from fakes.payment_provider import create_provider


def create_sandbox(secret):
    sandbox = create_provider(secret)

    @sandbox.after_request
    def next_release_renames_id(response):
        if request.path == "/v1/charges" and response.status_code == 201:
            charge = response.get_json()
            charge["charge_id"] = charge.pop("id")
            response.set_data(json.dumps(charge))
        return response

    return sandbox
