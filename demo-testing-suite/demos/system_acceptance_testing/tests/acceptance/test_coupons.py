"""Runs the scenarios in features/coupons.feature (steps: conftest.py)."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.acceptance

scenarios("features/coupons.feature")
