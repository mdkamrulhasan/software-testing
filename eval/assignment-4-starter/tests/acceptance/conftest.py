"""Step definitions for the acceptance scenarios (Sections 5 and 6).

Step definitions live here so that every .feature file can use every
step. The harness (tests/conftest.py) gives you `start_system` and
`system`; do NOT import anything from src/ in tests/acceptance/ -- an
acceptance test, like a system test, sees only HTTP and the outbox.

PROVIDED: a step library for setting up (Given), acting (When), and most
checks (Then). Read it before writing scenarios: your .feature lines must
match these patterns word for word. The worked example
(features/schedule.feature) shows how they fit together.

YOURS: the four Then steps listed at the bottom of this file (Section 5),
plus any extra steps your scenarios need.
"""

import re
from decimal import Decimal

import pytest
import requests
from pytest_bdd import given, parsers, then, when


def dollars(text):
    """'$1,425.00' or '1425.00' -> Decimal('1425.00'), exactly (no float rounding)."""
    return Decimal(text.replace("$", "").replace(",", ""))


def codes(text):
    """'MTH201, HIS105 and PHY230' -> {'MTH201', 'HIS105', 'PHY230'}."""
    return set(text.replace(" and ", ", ").replace(",", " ").split())


# ---------------------------------------------------------------------------
# WORKED EXAMPLE (US-3.1) -- provided
# ---------------------------------------------------------------------------


@given("the students and courses in SPEC.md", target_fixture="system")
def the_seeded_system(start_system):
    """A new running system with the seed data in SPEC.md."""
    return start_system()


@when(parsers.parse("{student:w} looks at their schedule"), target_fixture="schedule")
def looks_at_schedule(system, student):
    response = system.get(f"/students/{student}/schedule")
    assert response.status_code == 200
    return response.json()


@then(parsers.parse("they see the courses {course_list}"))
def they_see_the_courses(schedule, course_list):
    assert {c["code"] for c in schedule["courses"]} == codes(course_list)


@then(parsers.parse("they see {credits:d} credits and a fee of ${fee}"))
def they_see_credits_and_fee(schedule, credits, fee):
    assert schedule["total_credits"] == credits
    assert Decimal(str(schedule["fee"])) == dollars(fee)


# ---------------------------------------------------------------------------
# STEP LIBRARY -- provided
# ---------------------------------------------------------------------------


STUDENTS = r"(?P<students>S\d+(?:(?:, | and )S\d+)*)"
COURSES = r"(?P<courses>[A-Z]+\d+(?:(?:, | and )[A-Z]+\d+)*)"


def ids(text):
    return re.findall(r"[A-Z]+\d+", text)


@pytest.fixture
def context():
    """What the last When step did: its response, and how many
    notifications had been sent before it."""
    return {}


def act(context, system, request):
    """Run a When step's request; remember its response, and how many
    notifications had been sent before it (see notifications_to)."""
    context["sent_before"] = len(system.outbox())
    context["response"] = request()
    return context["response"]


def schedule_of(system, student):
    response = system.get(f"/students/{student}/schedule")
    assert response.status_code == 200
    return response.json()


def notifications_to(system, student, since=0):
    """Notifications sent to `student`, from position `since` in the outbox
    on. Use since=context["sent_before"] for "since the last When step"."""
    return [n for n in system.outbox()[since:] if n["student_id"] == student]


# -- Given: set-up through the system, as a user would ----------------------


@given(parsers.re(STUDENTS + r" (?:is|are) enrolled in (?P<course>[A-Z]+\d+)$"))
def students_are_enrolled(system, students, course):
    for student in ids(students):
        assert system.enroll(student, course).status_code == 201


@given(parsers.re(r"(?P<student>S\d+) has enrolled in " + COURSES + "$"))
def student_has_enrolled_in(system, student, courses):
    for course in ids(courses):
        assert system.enroll(student, course).status_code == 201


@given(parsers.re(STUDENTS + r" (?:joins?|join) the (?P<course>[A-Z]+\d+) waitlist$"))
def students_join_waitlist(system, students, course):
    for student in ids(students):
        assert system.join_waitlist(student, course).status_code == 201


@given(parsers.parse("{student:w} has left the {course:w} waitlist"))
def student_has_left_waitlist(system, student, course):
    assert system.leave_waitlist(student, course).status_code == 204


# -- When ------------------------------------------------------------------------


@when(parsers.parse("{student:w} enrolls in {course:w}"))
def enrolls(context, system, student, course):
    act(context, system, lambda: system.enroll(student, course))


@when(parsers.parse("{student:w} withdraws from {course:w}"))
def withdraws(context, system, student, course):
    act(context, system, lambda: system.withdraw(student, course))


@when(parsers.parse("{student:w} joins the {course:w} waitlist"))
@when(parsers.parse("{student:w} tries to join the {course:w} waitlist"))
def joins_waitlist(context, system, student, course):
    act(context, system, lambda: system.join_waitlist(student, course))


@when(parsers.parse("{student:w} leaves the {course:w} waitlist"))
def leaves_waitlist(context, system, student, course):
    act(context, system, lambda: system.leave_waitlist(student, course))


@when("the system is restarted")
def the_system_is_restarted(system):
    system.restart()


@when("a load balancer checks the system's health without credentials",
      target_fixture="health")
def health_without_credentials(system):
    return requests.get(system.url + "/health", timeout=10)


# -- Then: what the student sees ------------------------------------------------


@then(parsers.parse("they are enrolled with {credits:d} credits and a fee of ${fee}"))
def they_are_enrolled_with(context, credits, fee):
    response = context["response"]
    assert response.status_code == 201
    body = response.json()
    assert body["total_credits"] == credits
    assert Decimal(str(body["fee"])) == dollars(fee)


@then(parsers.parse("they are told they are number {position:d} on the waitlist"))
def told_position(context, position):
    response = context["response"]
    assert response.status_code == 201
    assert response.json()["position"] == position


@then(parsers.re(STUDENTS + r" (?:is|are) enrolled in (?P<course>[A-Z]+\d+)$"))
def is_enrolled(system, students, course):
    for student in ids(students):
        assert course in {c["code"] for c in schedule_of(system, student)["courses"]}


@then(parsers.parse("{student:w} is not enrolled in {course:w}"))
def is_not_enrolled(system, student, course):
    assert course not in {c["code"] for c in schedule_of(system, student)["courses"]}


@then(parsers.parse("{student:w} has {credits:d} credits and a fee of ${fee}"))
def has_credits_and_fee(system, student, credits, fee):
    schedule = schedule_of(system, student)
    assert schedule["total_credits"] == credits
    assert Decimal(str(schedule["fee"])) == dollars(fee)


@then(parsers.parse("{student:w} is on no waitlist"))
def on_no_waitlist(system, student):
    assert schedule_of(system, student)["waitlisted"] == []


@then(parsers.parse("{course:w} has {taken:d} of {capacity:d} seats taken"))
def seats_taken(system, course, taken, capacity):
    info = system.get(f"/courses/{course}").json()
    assert (info["seats_taken"], info["capacity"]) == (taken, capacity)


# -- Then: what the student receives (the outbox) ------------------------------


@then(parsers.parse("{student:w} receives a message that they are number {position:d} "
                    "on the {course:w} waitlist"))
def receives_waitlisted(context, system, student, position, course):
    sent = notifications_to(system, student, context.get("sent_before", 0))
    assert {"type": "waitlisted", "student_id": student, "course_code": course,
            "position": position} in sent


@then(parsers.parse("{student:w} receives nothing"))
def receives_nothing(context, system, student):
    assert notifications_to(system, student, context.get("sent_before", 0)) == []


# -- Then: what the operators see ------------------------------------------------


@then("the system reports that it is healthy")
def reports_healthy(health):
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# YOUR STEP DEFINITIONS -- Section 5
# ---------------------------------------------------------------------------
# TODO: implement these four Then steps, with exactly these patterns:
#
#   @then(parsers.parse('they are told "{message}"'))
#       the last When step's response is an error (4xx) whose JSON body is
#       {"error": message}
#
#   @then(parsers.parse("{student:w} is number {position:d} on the {course:w} waitlist"))
#       the student's schedule lists the course among their waitlists, at
#       that position
#
#   @then(parsers.parse("{student:w} receives a confirmation for {course:w} of ${fee}"))
#       since the last When step, exactly one confirmation was sent to the
#       student, for that course, with that fee (compare with dollars())
#
#   @then(parsers.parse('{student:w} receives a rejection for {course:w} saying "{reason}"'))
#       since the last When step, a rejection for that course with that
#       reason was sent to the student
#
# Use the helpers above: context["response"], context["sent_before"],
# schedule_of(), notifications_to(), dollars(). Add any other step your
# scenarios need here too. Constrain every parameter that is not the last
# thing on its line ({student:w}, {count:d}, ...).
