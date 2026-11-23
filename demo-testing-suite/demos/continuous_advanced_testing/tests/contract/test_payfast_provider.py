"""Provider side of the shop-PayFast contract: does PAYFAST keep it?

Each interaction's request is replayed against a PayFast, after putting
it into the interaction's provider state, and the response is checked
against the contract. Which PayFast:

    pytest tests/contract                                  # our fake (default)
    PAYFAST=sandbox-next pytest tests/contract/test_payfast_provider.py

Checking our FAKE keeps the fake honest: every system and acceptance
test trusts it. Checking the REAL provider's sandbox (here, a stand-in
for it after PayFast's next release) catches PayFast changing under us.
In a real pipeline the second check runs on a schedule, or in the
provider's own pipeline, because the provider changes on its schedule,
not ours.
"""

import os
import threading

import pytest
import requests
from werkzeug.serving import make_server

from fakes.payfast_sandbox_next import create_sandbox
from fakes.payment_provider import create_provider
from tests.contract.contract import interactions, response_mismatches

pytestmark = pytest.mark.contract

SECRET = "sk_test_123"
PROVIDERS = {"fake": create_provider, "sandbox-next": create_sandbox}


@pytest.fixture
def payfast():
    """The PayFast under verification, served over real HTTP."""
    app = PROVIDERS[os.environ.get("PAYFAST", "fake")](SECRET)
    server = make_server("127.0.0.1", 0, app, threaded=True)
    thread = threading.Thread(target=server.serve_forever,
                              kwargs={"poll_interval": 0.01}, daemon=True)
    thread.start()
    app.url = f"http://127.0.0.1:{server.port}"
    yield app
    server.shutdown()
    thread.join()


# Provider states: how to put this provider into the state an interaction
# assumes. Pact calls these "state handlers". For our fake, its test-only
# /_test/config endpoint; for a real sandbox, test card numbers and the like.
STATES = {
    "the card will be accepted": {"mode": "normal"},
    "the card will be declined": {"mode": "decline"},
    "PayFast is unavailable": {"mode": "unavailable"},
}


@pytest.mark.parametrize("interaction", interactions(), ids=lambda i: i["description"])
def test_payfast_honors_the_contract(payfast, interaction):
    requests.post(f"{payfast.url}/_test/config", json=STATES[interaction["providerState"]],
                  timeout=5)
    sent = interaction["request"]

    response = requests.request(sent["method"], payfast.url + sent["path"],
                                headers=sent["headers"], json=sent["body"], timeout=5)

    body = response.json() if "json" in response.headers.get("Content-Type", "") else None
    assert response_mismatches(interaction["response"], response.status_code, body) == []
