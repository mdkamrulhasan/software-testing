"""monkeypatch demo: safely set an environment variable for one test
only, with automatic cleanup even on failure.

"monkeypatch: Safely Patching Things" slide.
"""

from app.payments.api_client import get_api_key


def test_get_api_key(monkeypatch):
    monkeypatch.setenv("PAYMENT_API_KEY", "test-key-123")
    assert get_api_key() == "test-key-123"
