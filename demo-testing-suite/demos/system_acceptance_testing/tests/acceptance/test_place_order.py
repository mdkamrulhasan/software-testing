"""Runs the scenarios in features/place_order.feature (steps: conftest.py)."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.acceptance

scenarios("features/place_order.feature")
