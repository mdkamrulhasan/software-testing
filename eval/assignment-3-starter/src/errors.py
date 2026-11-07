"""Exceptions shared by the registration system's components.

The service raises them; the API turns each one into an HTTP status
(see SPEC.md). They are part of the interface between those components.
"""


class UnknownStudent(Exception):
    """No student has this id."""


class UnknownCourse(Exception):
    """No course has this code."""


class AlreadyEnrolled(Exception):
    """The student is already enrolled in this course."""


class NotEnrolled(Exception):
    """The student is not enrolled in this course."""


class CourseFull(Exception):
    """Every seat in the course is taken."""


class NotEligible(Exception):
    """can_register() refused: credit limit or missing prerequisite.
    The message says which, and is shown to the student."""
