"""Course registration rules (unchanged since Assignment 1).

``can_register()`` and ``calculate_registration_fee()`` are exactly the
functions you tested in Assignments 1 and 2. In Assignment 3 they are no
longer called on their own: ``service.py`` calls them with data read from
the database. Do NOT modify this file.
"""

from __future__ import annotations


def can_register(current_credits: int, course_credits: int, prerequisite_met: bool) -> bool:
    """Determine whether a student may register for a course.

    A student may register when ALL of the following hold:
      * ``current_credits`` is between 0 and 15, inclusive.
      * ``course_credits`` is between 1 and 4, inclusive.
      * ``current_credits + course_credits`` does not exceed 18.
      * ``prerequisite_met`` is True.
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
