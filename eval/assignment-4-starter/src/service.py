"""Registering students for courses: the component that ties the rules
(registration.py), the database (repository.py), and the notifier
together."""

import sqlite3

from errors import (AlreadyEnrolled, AlreadyWaitlisted, CourseFull,
                    CourseHasOpenSeats, NotEligible, NotEnrolled, NotWaitlisted,
                    UnknownCourse, UnknownStudent)
from registration import calculate_registration_fee, can_register


class RegistrationService:
    def __init__(self, connection, repository, notifier):
        self.connection = connection
        self.repository = repository
        self.notifier = notifier

    # -- helpers -------------------------------------------------------------
    def _student_and_course(self, student_id, course_code):
        if self.repository.get_student(student_id) is None:
            raise UnknownStudent(student_id)
        course = self.repository.get_course(course_code)
        if course is None:
            raise UnknownCourse(course_code)
        return course

    def _ineligibility(self, student_id, course):
        """REQ-1: why the student may not take the course now, or None."""
        current = self.repository.current_credits(student_id)
        prerequisite = course["prerequisite"]
        prerequisite_met = (prerequisite is None
                            or self.repository.has_completed(student_id, prerequisite))
        if can_register(current, course["credits"], prerequisite_met):
            return None
        if not prerequisite_met:
            return f"prerequisite {prerequisite} not completed"
        return "credit limit exceeded"

    def _confirmation(self, student_id, course):
        """The enrollment record and fee for a student just enrolled (REQ-4)."""
        total = self.repository.current_credits(student_id)
        fee = calculate_registration_fee(total)
        return {"student_id": student_id, "course_code": course["code"],
                "credits": course["credits"], "total_credits": total, "fee": fee}

    # -- enrolling and withdrawing -------------------------------------------
    def enroll(self, student_id, course_code):
        """Enroll a student; return the enrollment (SPEC.md, POST /enrollments)."""
        course = self._student_and_course(student_id, course_code)
        reason = self._ineligibility(student_id, course)
        if reason:
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

        enrollment = self._confirmation(student_id, course)
        self.notifier.send_confirmation(student_id, course_code, enrollment["fee"])
        return enrollment

    def withdraw(self, student_id, course_code):
        """Remove a student from a course, free the seat, and offer it to
        the waitlist (REQ-6, REQ-10)."""
        with self.connection:
            if not self.repository.remove_enrollment(student_id, course_code):
                raise NotEnrolled(f"{student_id} in {course_code}")
            self.repository.release_seat(course_code)
            notifications = self._offer_seat(course_code)
        for send in notifications:  # only after the transaction has committed
            send()

    def _offer_seat(self, course_code):
        """REQ-10: offer a freed seat to the first student on the waitlist.

        Runs inside withdraw()'s transaction. Returns the notifications to
        send once that transaction has committed.
        """
        student_id = self.repository.first_on_waitlist(course_code)
        if student_id is None:
            return []
        course = self.repository.get_course(course_code)
        self.repository.remove_from_waitlist(student_id, course_code)
        reason = self._ineligibility(student_id, course)
        if reason:
            return [lambda: self.notifier.send_rejection(student_id, course_code, reason)]
        self.repository.take_seat(course_code)
        self.repository.add_enrollment(student_id, course_code)
        fee = self._confirmation(student_id, course)["fee"]
        return [lambda: self.notifier.send_confirmation(student_id, course_code, fee)]

    # -- the waitlist ----------------------------------------------------------
    def join_waitlist(self, student_id, course_code):
        """REQ-9: put an eligible student on a full course's waitlist."""
        course = self._student_and_course(student_id, course_code)
        if self.repository.is_enrolled(student_id, course_code):
            raise AlreadyEnrolled(f"{student_id} in {course_code}")
        if course["seats_taken"] < course["capacity"]:
            raise CourseHasOpenSeats(course_code)
        reason = self._ineligibility(student_id, course)
        if reason:
            self.notifier.send_rejection(student_id, course_code, reason)
            raise NotEligible(reason)
        try:
            with self.connection:
                position = self.repository.add_to_waitlist(student_id, course_code)
        except sqlite3.IntegrityError:
            raise AlreadyWaitlisted(f"{student_id} for {course_code}")
        self.notifier.send_waitlisted(student_id, course_code, position)
        return {"student_id": student_id, "course_code": course_code,
                "position": position}

    def leave_waitlist(self, student_id, course_code):
        with self.connection:
            if not self.repository.remove_from_waitlist(student_id, course_code):
                raise NotWaitlisted(f"{student_id} for {course_code}")

    # -- reads -----------------------------------------------------------------
    def schedule(self, student_id):
        """The student's courses, total credits, semester fee, and waitlists."""
        if self.repository.get_student(student_id) is None:
            raise UnknownStudent(student_id)
        courses = self.repository.enrolled_courses(student_id)
        total = sum(c["credits"] for c in courses)
        return {"student_id": student_id, "courses": courses,
                "total_credits": total, "fee": calculate_registration_fee(total),
                "waitlisted": self.repository.waitlisted_courses(student_id)}

    def course(self, code):
        course = self.repository.get_course(code)
        if course is None:
            raise UnknownCourse(code)
        return course

    def health(self):
        self.connection.execute("SELECT 1").fetchone()
        return True
