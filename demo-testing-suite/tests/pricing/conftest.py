"""Fixtures shared by every test module under tests/pricing/.

pytest auto-discovers this file (no import needed anywhere) and makes
every fixture below available to test_discounts.py and test_cart.py in
this same directory. Demonstrates "Defining and Using a Fixture" and
"Fixtures Can Depend on Other Fixtures".
"""

import pytest


@pytest.fixture
def sample_cart():
    """A shopping cart pre-loaded with two items."""
    return {
        "items": [
            {"name": "widget", "price": 9.99, "quantity": 3},
            {"name": "gadget", "price": 24.99, "quantity": 1},
        ]
    }


@pytest.fixture
def empty_cart():
    """A cart with no items -- the building block for cart_with_one_item."""
    return {"items": []}


@pytest.fixture
def cart_with_one_item(empty_cart):
    """A cart with exactly one item, built on top of empty_cart.

    This is the "fixtures depending on fixtures" example: pytest resolves
    empty_cart first, passes its return value into this function, and
    this function mutates and returns it. Because empty_cart() is called
    fresh for every test that (transitively) needs it, one test's
    mutation here can never leak into another test.
    """
    empty_cart["items"].append({"name": "widget", "price": 9.99, "quantity": 1})
    return empty_cart
