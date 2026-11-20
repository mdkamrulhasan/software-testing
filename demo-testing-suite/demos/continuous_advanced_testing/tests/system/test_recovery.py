"""Recoverability and operability system tests: NFR-2, NFR-3, SYS-8."""

import pytest
import requests

pytestmark = pytest.mark.system


def test_orders_work_again_after_a_provider_outage(shop):
    """NFR-2: no restart needed once PayFast is back."""
    shop.provider(mode="unavailable")
    during = shop.order("MUG", 1)
    assert during.status_code == 503
    assert during.headers["Retry-After"] == "30"

    shop.provider(mode="normal")
    after = shop.order("MUG", 1)
    assert after.status_code == 201
    assert shop.stock("MUG") == 4              # only the second order took stock


def test_health_stays_ok_during_a_provider_outage(shop):
    """NFR-3: PayFast being down does not make the shop unhealthy."""
    shop.provider(mode="unavailable")
    response = requests.get(shop.url + "/health", timeout=1)
    assert response.json() == {"status": "ok"}


def test_orders_and_stock_survive_a_restart(shop, start_shop):
    """SYS-8: stop the shop, start it again on the same database."""
    order = shop.order("MUG", 2).json()

    restarted = start_shop(restart_of=shop)

    assert restarted.get(f"/orders/{order['id']}").json() == order
    assert restarted.stock("MUG") == 3          # not re-seeded back to 5
