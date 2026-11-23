"""PROVIDED -- the developer's system tests for the waitlist (SPEC.md
REQ-9 to REQ-11). They all pass. Read them; do not change them.

They check the system against SPEC.md, the team's own specification.
Your acceptance tests (tests/acceptance/) check it against
specs/user_stories.md, the customer's.
"""

import pytest

pytestmark = pytest.mark.system


def fill_se499(system):
    for student in ("S01", "S02", "S03"):
        assert system.enroll(student, "SE499").status_code == 201


def seats_taken(system, code):
    return system.get(f"/courses/{code}").json()["seats_taken"]


def test_students_join_a_full_course_waitlist_in_order(system):
    """REQ-9, REQ-5"""
    fill_se499(system)
    first = system.join_waitlist("S04", "SE499")
    second = system.join_waitlist("S05", "SE499")
    assert (first.status_code, first.json()["position"]) == (201, 1)
    assert (second.status_code, second.json()["position"]) == (201, 2)
    assert {"type": "waitlisted", "student_id": "S05", "course_code": "SE499",
            "position": 2} in system.outbox()


@pytest.mark.parametrize("student, course, status, message", [
    ("S01", "SE413", 409, "course has open seats"),
    ("S01", "SE499", 409, "already enrolled"),
    ("S13", "SE499", 422, "prerequisite CIS350 not completed"),
    ("S99", "SE499", 404, "unknown student: S99"),
])
def test_who_may_not_join_a_waitlist(system, student, course, status, message):
    """REQ-9"""
    fill_se499(system)
    response = system.join_waitlist(student, course)
    assert (response.status_code, response.json()) == (status, {"error": message})


def test_joining_the_same_waitlist_twice_is_refused(system):
    """REQ-9"""
    fill_se499(system)
    system.join_waitlist("S04", "SE499")
    response = system.join_waitlist("S04", "SE499")
    assert (response.status_code, response.json()) == (409, {"error": "already on waitlist"})


def test_a_freed_seat_goes_to_the_first_student_waiting(system):
    """REQ-10, REQ-5, REQ-7"""
    fill_se499(system)
    system.join_waitlist("S04", "SE499")
    system.join_waitlist("S05", "SE499")
    assert system.withdraw("S01", "SE499").status_code == 204
    assert seats_taken(system, "SE499") == 3
    schedule = system.get("/students/S04/schedule").json()
    assert [c["code"] for c in schedule["courses"]] == ["SE499"]
    assert schedule["waitlisted"] == []
    assert system.outbox()[-1] == {"type": "confirmation", "student_id": "S04",
                                   "course_code": "SE499", "fee": 300.0}


def test_an_ineligible_first_student_is_rejected_and_removed(system):
    """REQ-10, REQ-1, REQ-5"""
    fill_se499(system)
    system.join_waitlist("S04", "SE499")
    for course in ("MTH201", "HIS105", "PHY230", "CHM110"):  # 16 credits
        system.enroll("S04", course)
    system.withdraw("S01", "SE499")
    schedule = system.get("/students/S04/schedule").json()
    assert "SE499" not in [c["code"] for c in schedule["courses"]]
    assert schedule["waitlisted"] == []
    assert system.outbox()[-1] == {"type": "rejection", "student_id": "S04",
                                   "course_code": "SE499",
                                   "reason": "credit limit exceeded"}


def test_the_schedule_shows_waitlist_positions(system):
    """REQ-7, REQ-9"""
    fill_se499(system)
    system.join_waitlist("S04", "SE499")
    system.join_waitlist("S05", "SE499")
    schedule = system.get("/students/S05/schedule").json()
    assert schedule["waitlisted"] == [
        {"code": "SE499", "title": "Capstone Seminar", "position": 2}]


def test_a_student_can_leave_a_waitlist(system):
    """REQ-11"""
    fill_se499(system)
    system.join_waitlist("S04", "SE499")
    assert system.leave_waitlist("S04", "SE499").status_code == 204
    assert system.leave_waitlist("S04", "SE499").json() == {"error": "not on waitlist"}
    assert system.get("/students/S04/schedule").json()["waitlisted"] == []


def test_withdrawing_removes_only_that_student(system):
    """REQ-6 (the Assignment 3 defect, now fixed)"""
    fill_se499(system)
    system.withdraw("S01", "SE499")
    assert seats_taken(system, "SE499") == 2
    for student in ("S02", "S03"):
        courses = system.get(f"/students/{student}/schedule").json()["courses"]
        assert [c["code"] for c in courses] == ["SE499"]
