"""Course registration business logic.

This module is provided as complete, working starter code for SE 413/513
Assignment 2. It includes the two functions from Assignment 1 (unchanged)
plus two new functions that this assignment's test suite targets.

Do NOT modify the business logic in this file. Your task is to design and
implement a thorough test suite (see the ``tests/`` package) using
statement/branch coverage, data-flow testing, and test doubles.
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


def summarize_batch_registrations(requests: list) -> tuple:
    """Process a batch of registration requests and summarize the results.

    Each request in ``requests`` is a tuple
    ``(current_credits, course_credits, prerequisite_met)``. For every
    request that :func:`can_register` approves, this function accumulates
    the registration fee (computed from the student's resulting total
    credit load) into a running total, and counts the approval. Rejected
    requests contribute nothing to either accumulator.

    Args:
        requests: A list of ``(current_credits, course_credits,
            prerequisite_met)`` tuples.

    Returns:
        A ``(approved_count, total_fees)`` tuple: how many requests were
        approved, and the sum of their registration fees.
    """
    approved_count = 0
    total_fees = 0.0

    for current_credits, course_credits, prerequisite_met in requests:
        if can_register(current_credits, course_credits, prerequisite_met):
            approved_count = approved_count + 1
            total_credits = current_credits + course_credits
            total_fees = total_fees + calculate_registration_fee(total_credits)

    return approved_count, total_fees


def enroll_student(current_credits: int, course_credits: int, prerequisite_met: bool, notifier) -> bool:
    """Attempt to enroll a student, notifying them of the outcome.

    If registration is allowed, ``notifier.send_confirmation(fee)`` is
    called with the computed registration fee. Otherwise,
    ``notifier.send_rejection()`` is called with no arguments.

    Args:
        current_credits: The student's current credit load.
        course_credits: The credit value of the requested course.
        prerequisite_met: Whether the student has satisfied the prerequisite.
        notifier: A collaborator exposing ``send_confirmation(fee)`` and
            ``send_rejection()``. In production this might send a real
            email or push notification; in tests, pass a test double.

    Returns:
        True if the student was enrolled, False otherwise.
    """
    if can_register(current_credits, course_credits, prerequisite_met):
        total_credits = current_credits + course_credits
        fee = calculate_registration_fee(total_credits)
        notifier.send_confirmation(fee)
        return True

    notifier.send_rejection()
    return False
