"""Course registration business logic.

This module is provided as complete, working starter code for SE 413/513
Assignment 1. It implements the two functions described in the assignment
exactly as specified.

Do NOT modify the business logic in this file. Your task is to design and
implement a thorough test suite (see the ``tests/`` package) that verifies
this behavior using equivalence partitioning, boundary-value analysis, and
positive/negative testing.
"""

from __future__ import annotations


def can_register(current_credits: int, course_credits: int, prerequisite_met: bool) -> bool:
    """Determine whether a student may register for a course.

    A student may register when ALL of the following hold:
      * ``current_credits`` is between 0 and 15, inclusive.
      * ``course_credits`` is between 1 and 4, inclusive.
      * ``current_credits + course_credits`` does not exceed 18.
      * ``prerequisite_met`` is True.

    Args:
        current_credits: The student's current credit load.
        course_credits: The credit value of the course being requested.
        prerequisite_met: Whether the student has satisfied the prerequisite.

    Returns:
        True if registration is allowed, False otherwise.
    """
    if not (0 <= current_credits <= 15):
        return False

    if not (1 <= course_credits <= 4):
        return False

    if current_credits + course_credits > 18:
        return False

    if not prerequisite_met:
        return False

    return True


def calculate_registration_fee(total_credits: int) -> float:
    """Calculate the registration fee for a given total credit load.

    Pricing:
      * The first 12 credits are billed at $100/credit.
      * Credits above 12, up to 18, are billed at $75/credit.

    Args:
        total_credits: The student's total credit load after registration.
            Must be between 0 and 18, inclusive.

    Returns:
        The total registration fee as a float.

    Raises:
        ValueError: If ``total_credits`` is outside the valid [0, 18] range.
    """
    if not (0 <= total_credits <= 18):
        raise ValueError(
            f"total_credits must be between 0 and 18 inclusive, got {total_credits!r}"
        )

    if total_credits <= 12:
        return total_credits * 100.0

    base_fee = 12 * 100.0
    discounted_credits = total_credits - 12
    return base_fee + discounted_credits * 75.0
