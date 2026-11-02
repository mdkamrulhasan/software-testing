"""Client for the PayFast payment provider -- the OUTDATED version.

KNOWN BUG (deliberate, for the "incorrect data format" demo): this copy
was written against v1 of PayFast's API, which took `amount` as a
decimal string of dollars ("12.50"). v2, the current contract in
specs/payment_provider_api.md, requires an integer number of cents
(1250). Every unit test that mocks the HTTP layer still passes, because
the mock was written from the same outdated assumption. See
tests/test_payments_stubbed.py and tests/test_payments_live.py.
"""

import requests

from shop.errors import PaymentDeclined, PaymentError, PaymentUnavailable

RETRYABLE = {500, 502, 503, 504}


class PaymentClient:
    def __init__(self, base_url, api_key, *, timeout=5.0, retries=1, session=None):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        self.retries = retries
        self.session = session or requests.Session()

    def charge(self, amount_cents, reference):
        """Charge `amount_cents` (an int, in cents); return the charge id.

        Retries on a 5xx or a network failure. The Idempotency-Key header
        makes that safe: PayFast charges a given key at most once.
        """
        payload = {
            "amount": f"{amount_cents / 100:.2f}",  # KNOWN BUG: v1 format
            "currency": "USD",
            "reference": reference,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Idempotency-Key": reference,
        }
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
