"""Consumer side of the shop-PayFast contract: does the SHOP keep it?

For each interaction in contracts/shop-payfast.json, the shop's real
PaymentClient talks to a stub that answers from the contract. The test
checks two things:

  1. every request the shop sent matches the contract's request, and
  2. the shop does the right thing with the contract's response.

No PayFast, fake or real, is involved: these run in milliseconds.

    SHOP_PAYMENTS=no_idempotency pytest tests/contract   # the shop breaks the contract
"""

import pytest

from shop.errors import PaymentDeclined, PaymentUnavailable
from tests.contract.contract import Stub, interactions
from variants import PaymentClient

pytestmark = pytest.mark.contract

BY_DESCRIPTION = {i["description"]: i for i in interactions()}


def charge_through(stub):
    client = PaymentClient(stub.url, "sk_test_123", timeout=2.0)
    return client.charge(2500, reference="order-1")


def test_an_accepted_card_returns_the_charge_id():
    with Stub(BY_DESCRIPTION["a charge for a card that is accepted"]) as stub:
        charge_id = charge_through(stub)

    assert stub.mismatches() == []
    assert charge_id == "ch_1"


def test_a_declined_card_raises_payment_declined():
    with Stub(BY_DESCRIPTION["a charge for a card that is declined"]) as stub:
        with pytest.raises(PaymentDeclined):
            charge_through(stub)

    assert stub.mismatches() == []
    assert len(stub.received) == 1                   # "Do not retry" (the spec)


def test_an_outage_is_retried_with_the_same_idempotency_key():
    with Stub(BY_DESCRIPTION["a charge while PayFast is unavailable"]) as stub:
        with pytest.raises(PaymentUnavailable):
            charge_through(stub)

    assert stub.mismatches() == []
    keys = [sent["headers"].get("Idempotency-Key") for sent in stub.received]
    assert keys == ["order-1", "order-1"]             # retried once, safely


def test_every_interaction_in_the_contract_has_a_consumer_test():
    """A contract entry with no consumer test is a promise nobody checks."""
    tested = {"a charge for a card that is accepted",
              "a charge for a card that is declined",
              "a charge while PayFast is unavailable"}
    assert set(BY_DESCRIPTION) == tested
