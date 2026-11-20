"""DEFECTIVE variant of shop/payments.py, for the Week 14 contract-testing demo.

A refactoring dropped the Idempotency-Key header: "the provider's spec
says it is only *recommended*, and every test still passes". Every test
does still pass -- the fake PayFast does not require the header -- but
a retried charge can now charge the customer twice on the real PayFast.
Only the contract (contracts/shop-payfast.json) says the shop sends it.

    SHOP_PAYMENTS=no_idempotency pytest                  # 60 passed
    SHOP_PAYMENTS=no_idempotency pytest tests/contract   # the consumer test fails
"""

import requests

from shop.errors import PaymentDeclined, PaymentError, PaymentUnavailable
from shop.payments import RETRYABLE


class PaymentClient:
    def __init__(self, base_url, api_key, *, timeout=5.0, retries=1, session=None):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()

    def charge(self, amount_cents, reference):
        payload = {"amount": amount_cents, "currency": "USD", "reference": reference}
        headers = {"Authorization": f"Bearer {self.api_key}"}   # no Idempotency-Key
        problem = "no attempt was made"
        for _ in range(self.retries + 1):
            try:
                response = self.session.post(
                    f"{self.base_url}/v1/charges",
                    json=payload, headers=headers, timeout=self.timeout,
                )
            except (requests.ConnectionError, requests.Timeout) as exc:
                problem = f"provider unreachable ({type(exc).__name__})"
                continue
            if response.status_code in RETRYABLE:
                problem = f"provider returned {response.status_code}"
                continue
            break
        else:
            raise PaymentUnavailable(problem)

        if response.status_code == 201:
            return response.json()["id"]
        if response.status_code == 402:
            raise PaymentDeclined(response.json()["error"])
        raise PaymentError(
            f"provider rejected the request: {response.status_code} "
            f"{response.text.strip()}"
        )
