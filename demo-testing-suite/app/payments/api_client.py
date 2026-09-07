"""A minimal client for a (fictional) payment provider's API key lookup.

Demonstrates pytest's built-in monkeypatch fixture: tests that depend on
environment variables should set them through monkeypatch, which
automatically restores the original environment after the test ends --
even if the test fails. See tests/payments/test_api_client.py.
"""

import os


def get_api_key():
    """Return the payment provider's API key from the environment.

    Raises:
        KeyError: If PAYMENT_API_KEY is not set. Real code would likely
            raise a clearer, custom exception here -- kept simple to
            match the slide exactly.
    """
    return os.environ["PAYMENT_API_KEY"]
