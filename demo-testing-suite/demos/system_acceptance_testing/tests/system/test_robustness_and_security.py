"""Security and robustness system tests: SYS-6 and SYS-7.

A system tester sends what a careless client or an attacker would send,
not what the API documentation suggests. The first version of this
file found finding F1 (specs/system_test_plan.md, Section 8): two of the
inputs below crashed the Week 10 shop with an HTML `500` page.
"""

import pytest
import requests

pytestmark = pytest.mark.system

HOSTILE_BODIES = [
    pytest.param({"sku": ["MUG"], "quantity": 1, "customer_email": "a@b.c"},
                 id="sku-is-a-list"),                                    # F1
    pytest.param({"sku": "MUG", "quantity": 10**30, "customer_email": "a@b.c"},
                 id="quantity-too-big-for-sqlite"),                      # F1
    pytest.param({"sku": "MUG", "quantity": 101, "customer_email": "a@b.c"},
                 id="quantity-just-over-the-limit"),
    pytest.param({"sku": "MUG", "quantity": True, "customer_email": "a@b.c"},
                 id="quantity-is-a-boolean"),
    pytest.param({"sku": "MUG", "quantity": 1, "customer_email": "a@b.c",
                  "coupon": {"code": "SAVE10"}}, id="coupon-is-an-object"),
    pytest.param({"sku": "MUG'; DROP TABLE products; --", "quantity": 1,
                  "customer_email": "a@b.c"}, id="sql-injection-in-sku"),
    pytest.param([], id="body-is-a-list"),
    pytest.param("x" * 100_000, id="body-is-a-huge-string"),
]


@pytest.mark.parametrize("body", HOSTILE_BODIES)
def test_hostile_input_gets_a_json_4xx(shop, body):
    """SYS-7: rejected, in JSON, with no internals; and nothing changes."""
    response = shop.post("/orders", json=body)

    assert 400 <= response.status_code < 500, response.text[:200]
    assert response.headers["Content-Type"] == "application/json"
    assert "Traceback" not in response.text
    assert shop.stock("MUG") == 5          # the products table is intact
    assert shop.charges() == []


def test_body_that_is_not_json_gets_a_json_400(shop):
    response = shop.post("/orders", data="sku=MUG&quantity=1",
                         headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 400
    assert response.headers["Content-Type"] == "application/json"


@pytest.mark.parametrize("method, path", [
    ("GET", "/products"), ("POST", "/orders"), ("GET", "/orders/1"),
])
def test_every_endpoint_except_health_needs_the_key(shop, method, path):
    """SYS-6."""
    response = requests.request(method, shop.url + path, timeout=5)  # no key
    assert response.status_code == 401
    assert response.json() == {"error": "missing or invalid API key"}


def test_health_needs_no_key(shop):
    """SYS-6, NFR-3: a load balancer's probe carries no credentials."""
    assert requests.get(shop.url + "/health", timeout=5).json() == {"status": "ok"}


def test_unknown_route_answers_in_json(shop):
    response = shop.get("/admin")
    assert response.status_code == 404
    assert response.headers["Content-Type"] == "application/json"
