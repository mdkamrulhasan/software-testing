"""Step definitions for the acceptance scenarios in features/.

Each step translates one line of the customer's language into calls on
the running shop (tests/conftest.py starts it). Money is written in
dollars in the .feature files, because that is how the product owner
talks; the steps convert to the API's cents.

Steps live here, not in the test modules, so that every feature can use
every step: "Given the shop sells:" opens all three features.
"""

from decimal import Decimal

from pytest_bdd import given, parsers, then, when


def cents(dollars):
    """'12.50' -> 1250, exactly (no float rounding)."""
    return int(Decimal(dollars) * 100)


def dollars(cents_value):
    return f"{Decimal(cents_value) / 100:.2f}"


# -- Given ------------------------------------------------------------------

@given("the shop sells:", target_fixture="the_shop")
def the_shop_sells(start_shop, datatable):
    header, *rows = datatable
    catalog = []
    for row in rows:
        product = dict(zip(header, row))
        catalog.append({"sku": product["sku"], "name": product["name"],
                        "price_cents": cents(product["price"]),
                        "stock": int(product["stock"])})
    return start_shop(seed=catalog)


@given("my card will be declined")
def card_will_be_declined(the_shop):
    the_shop.provider(mode="decline")


# -- When -------------------------------------------------------------------

@when(parsers.parse('I order {quantity:d} "{sku}"'), target_fixture="response")
def i_order(the_shop, quantity, sku):
    return the_shop.order(sku, quantity)


@when(parsers.parse('I order {quantity:d} "{sku}" with coupon "{code}"'),
      target_fixture="response")
def i_order_with_coupon(the_shop, quantity, sku, code):
    return the_shop.order(sku, quantity, coupon=code)


@when("I look at the catalog", target_fixture="catalog")
def i_look_at_the_catalog(the_shop):
    return the_shop.get("/products").json()


# -- Then -------------------------------------------------------------------

@then("I see:")
def i_see(catalog, datatable):
    header, *rows = datatable
    shown = [[p["sku"], p["name"], dollars(p["price_cents"]), str(p["stock"])]
             for p in catalog]
    assert shown == rows


@then("my order is confirmed")
def my_order_is_confirmed(response):
    assert response.status_code == 201, response.json()
    assert response.json()["status"] == "paid"


@then(parsers.parse("I am charged ${amount}"))
def i_am_charged(the_shop, amount):
    assert [c["amount"] for c in the_shop.charges()] == [cents(amount)]


@then("I am not charged")
def i_am_not_charged(the_shop):
    assert the_shop.charges() == []


@then(parsers.parse("my confirmation shows a subtotal of ${subtotal}, "
                    "a discount of ${discount}, and a total of ${total}"))
def confirmation_shows(response, subtotal, discount, total):
    order = response.json()
    shown = (dollars(order["subtotal_cents"]), dollars(order["discount_cents"]),
             dollars(order["total_cents"]))
    assert shown == (subtotal, discount, total)


@then(parsers.parse('I am told "{message}"'))
def i_am_told(response, message):
    assert 400 <= response.status_code < 500
    assert response.json() == {"error": message}


@then("I can look my order up again")
def i_can_look_my_order_up_again(the_shop, response):
    assert the_shop.get(response.headers["Location"]).json() == response.json()


@then(parsers.parse('the catalog shows {count:d} "{sku}" in stock'))
def catalog_shows_stock(the_shop, count, sku):
    assert the_shop.stock(sku) == count
