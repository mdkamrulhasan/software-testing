"""Runs the scenarios in features/browse_products.feature (steps: conftest.py)."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.acceptance

scenarios("features/browse_products.feature")
