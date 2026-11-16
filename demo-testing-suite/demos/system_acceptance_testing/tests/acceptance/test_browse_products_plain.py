"""The same acceptance tests as test_browse_products.py, in regular pytest.

test_browse_products.py runs features/browse_products.feature: the
scenario is written in Gherkin, and each line is matched to a step
function in conftest.py. This file checks the same two scenarios (US-1.1,
US-1.2, US-1.3) with no feature file and no pytest-bdd: the scenario, its
implementation, and its assertions all live in one Python test function,
and Given-When-Then is only a comment.

Both versions start the same shop as a separate process (the start_shop
fixture in tests/conftest.py) and talk to it only over HTTP, so they are
acceptance tests at the same level. What differs is who can read them:
the .feature file is written for the product owner; this file is written
for developers.

Compare:
    pytest tests/acceptance/test_browse_products.py -v
    pytest tests/acceptance/test_browse_products_plain.py -v
"""

import pytest

pytestmark = pytest.mark.acceptance

# The Background of browse_products.feature, as Python data. The API
# speaks cents, so the prices are written in cents here; the feature file
# writes dollars and lets a step convert them.
CATALOG = [
    {"sku": "MUG", "name": "Coffee mug", "price_cents": 1250, "stock": 5},
    {"sku": "TEE", "name": "T-shirt", "price_cents": 2000, "stock": 0},
]


@pytest.fixture
def the_shop(start_shop):
    """Background: Given the shop sells a coffee mug (5 in stock) and a
    T-shirt (sold out)."""
    return start_shop(seed=CATALOG)


# US-1.1, US-1.2
def test_the_catalog_shows_price_and_stock(the_shop):
    # Given the shop sells MUG ($12.50, 5 in stock) and TEE ($20.00, sold out)
    #   (the the_shop fixture)

    # When I look at the catalog
    response = the_shop.get("/products")

    # Then I see each product's price and how many are in stock
    assert response.status_code == 200
    shown = [(p["sku"], p["name"], p["price_cents"], p["stock"])
             for p in response.json()]
    assert shown == [
        ("MUG", "Coffee mug", 1250, 5),
        ("TEE", "T-shirt", 2000, 0),
    ]


# US-1.3
def test_buying_reduces_the_stock_shown(the_shop):
    # Given the shop sells MUG with 5 in stock
    #   (the the_shop fixture)

    # When I order 2 MUG
    the_shop.order("MUG", 2)

    # Then the catalog shows 3 MUG in stock
    assert the_shop.stock("MUG") == 3
