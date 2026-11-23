"""Runs features/schedule.feature (US-3). PROVIDED as a worked example."""

import pytest
from pytest_bdd import scenarios

pytestmark = pytest.mark.acceptance

scenarios("features/schedule.feature")
