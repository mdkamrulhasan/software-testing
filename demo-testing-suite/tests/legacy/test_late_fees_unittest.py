"""The Lecture 1 (Testing Foundations) unittest-style tests for
calculate_late_fee, kept verbatim for the "A Unit Test, Revisited" slide.

This file intentionally still uses unittest.TestCase rather than plain
pytest style -- that contrast IS the point of the slide. pytest runs
unittest-style tests without any changes at all (worth saying out loud
in class), which is itself a small piece of evidence that pytest
subsumes unittest rather than replacing it outright.

Run just this file to show a PASS and a FAIL side by side before
switching to pytest's own style:

    pytest tests/legacy/test_late_fees_unittest.py -v
"""

import unittest

from app.billing.late_fees import calculate_late_fee


class TestLateFee(unittest.TestCase):
    def test_typical_fee(self):
        self.assertEqual(calculate_late_fee(3), 4.5)

    def test_negative_days_should_not_be_negative_fee(self):
        # Documents the requirement; currently FAILS, exposing the fault
        # from Lecture 1 (see app/billing/late_fees.py's KNOWN BUG note).
        self.assertGreaterEqual(calculate_late_fee(-4), 0)
