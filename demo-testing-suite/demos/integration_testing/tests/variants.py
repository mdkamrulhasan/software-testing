"""Which versions of the shop's components the tests run against.

By default, the correct ones. Two environment variables swap in the
deliberately broken versions, for the demos in README.md:

    SHOP_PAYMENTS=v1     shop/payments_v1.py: sends dollars, not cents
    SHOP_SERVICE=buggy   shop/service_buggy.py: the transaction bug

e.g.  SHOP_PAYMENTS=v1 pytest tests/test_api.py
"""

import os

if os.environ.get("SHOP_PAYMENTS") == "v1":
    from shop.payments_v1 import PaymentClient
else:
    from shop.payments import PaymentClient

if os.environ.get("SHOP_SERVICE") == "buggy":
    from shop.service_buggy import OrderService
else:
    from shop.service import OrderService

__all__ = ["PaymentClient", "OrderService"]
