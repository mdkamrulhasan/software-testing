"""Registering students for courses: the component that ties the rules
(registration.py), the database (repository.py), and the notifier
together."""

import sqlite3

from errors import (AlreadyEnrolled, CourseFull, NotEligible, NotEnrolled,
                    UnknownCourse, UnknownStudent)
from registration import calculate_registration_fee, can_register


class RegistrationService:
    def __init__(self, connection, repository, notifier):
        self.connection = connection
        self.repository = repository
        self.notifier = notifier

    def enroll(self, student_id, course_code):
        """Enroll a student; return the enrollment (SPEC.md, POST /enrollments)."""
        if self.repository.get_student(student_id) is None:
            raise UnknownStudent(student_id)
        course = self.repository.get_course(course_code)
        if course is None:
            raise UnknownCourse(course_code)

        current = self.repository.current_credits(student_id)
        prerequisite = course["prerequisite"]
        prerequisite_met = (prerequisite is None
                            or self.repository.has_completed(student_id, prerequisite))
        if not can_register(current, course["credits"], prerequisite_met):
            reason = (f"prerequisite {prerequisite} not completed"
                      if not prerequisite_met else "credit limit exceeded")
            self.notifier.send_rejection(student_id, course_code, reason)
            raise NotEligible(reason)

        # One transaction: the seat and the enrollment are saved together,
        # or (if either fails) not at all.
        try:
            with self.connection:
                if not self.repository.take_seat(course_code):
                    raise CourseFull(course_code)
                self.repository.add_enrollment(student_id, course_code)
        except CourseFull:
            self.notifier.send_rejection(student_id, course_code, "course is full")
            raise
        except sqlite3.IntegrityError:
            raise AlreadyEnrolled(f"{student_id} in {course_code}")

        total = current + course["credits"]
        fee = calculate_registration_fee(total)
        self.notifier.send_confirmation(student_id, course_code, fee)
        return {"student_id": student_id, "course_code": course_code,
                "credits": course["credits"], "total_credits": total, "fee": fee}

    def withdraw(self, student_id, course_code):
        """Remove a student from a course and free the seat."""
        with self.connection:
            if not self.repository.remove_enrollment(student_id, course_code):
                raise NotEnrolled(f"{student_id} in {course_code}")
            self.repository.release_seat(course_code)

    def schedule(self, student_id):
        """The student's courses, total credits, and semester fee."""
        if self.repository.get_student(student_id) is None:
            raise UnknownStudent(student_id)
        courses = self.repository.enrolled_courses(student_id)
        total = sum(c["credits"] for c in courses)
        return {"student_id": student_id, "courses": courses,
                "total_credits": total, "fee": calculate_registration_fee(total)}

    def course(self, code):
        course = self.repository.get_course(code)
        if course is None:
            raise UnknownCourse(code)
        return course

    def health(self):
        self.connection.execute("SELECT 1").fetchone()
        return True
