"""A conftest.py scoped to tests/checkout/ only. Fixtures defined here
(like discounted_cart below) are invisible to test_cart.py one directory
up -- that asymmetry is the entire point of the slide's diagram: visible
below, not visible sideways or above.
"""

import pytest


@pytest.fixture
def discounted_cart(sample_cart):
    # Reaches "up" to the parent directory's sample_cart fixture --
    # visibility flows DOWN the tree, so a fixture defined here can use
    # one defined above it, but not the other way around.
    sample_cart["discount_percent"] = 10
    return sample_cart
