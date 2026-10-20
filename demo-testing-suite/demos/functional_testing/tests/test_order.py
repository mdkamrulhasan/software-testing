import pytest
from shop.order import Order, InvalidTransition

def order_in(state):
    o = Order()
    path = {"CREATED": [], "PAID": ["pay"], "SHIPPED": ["pay", "ship"],
            "DELIVERED": ["pay", "ship", "deliver"],
            "CANCELLED": ["cancel"]}[state]
    for event in path:
        getattr(o, event)()
    return o

@pytest.mark.parametrize("start, event, end", [
    ("CREATED", "pay", "PAID"),
    ("CREATED", "cancel", "CANCELLED"),
    ("PAID", "ship", "SHIPPED"),
    ("PAID", "cancel", "CANCELLED"),
    ("SHIPPED", "deliver", "DELIVERED"),
])
def test_valid_transitions(start, event, end):
    o = order_in(start)
    getattr(o, event)()
    assert o.state == end

EVENTS = ["pay", "ship", "deliver", "cancel"]
VALID = {("CREATED", "pay"), ("CREATED", "cancel"), ("PAID", "ship"),
         ("PAID", "cancel"), ("SHIPPED", "deliver")}
INVALID = [(s, e)
           for s in ["CREATED", "PAID", "SHIPPED", "DELIVERED", "CANCELLED"]
           for e in EVENTS if (s, e) not in VALID]

@pytest.mark.parametrize("start, event", INVALID)
def test_invalid_transitions_rejected(start, event):
    o = order_in(start)
    with pytest.raises(InvalidTransition):
        getattr(o, event)()
    assert o.state == start          # REQ-7: order unchanged

def test_cancel_after_payment_refunds():
    o = order_in("PAID")
    o.cancel()
    assert o.refunded

def test_cancel_before_payment_does_not_refund():
    o = Order()
    o.cancel()
    assert not o.refunded
