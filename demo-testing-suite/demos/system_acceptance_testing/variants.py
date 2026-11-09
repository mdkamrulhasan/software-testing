"""Which versions of the shop's components to run.

By default, the correct ones. Two environment variables swap in the
deliberately defective versions, for the demos in README.md:

    SHOP_SERVICE=racy       shop/service_racy.py: charges first, takes stock after
    SHOP_COUPONS=per_unit   shop/pricing_per_unit.py: FLAT5 read as "per unit"

Both serve.py and the in-process integration tests import from here, so
one variable switches the component everywhere it is used -- including
inside the server process that the system and acceptance tests start
(child processes inherit the environment).

e.g.  SHOP_SERVICE=racy pytest tests/system
"""

import os

if os.environ.get("SHOP_SERVICE") == "racy":
    from shop.service_racy import OrderService
else:
    from shop.service import OrderService

if os.environ.get("SHOP_COUPONS") == "per_unit":
    from shop.pricing_per_unit import price_order
else:
    from shop.pricing import price_order

__all__ = ["OrderService", "price_order"]
