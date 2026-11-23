# Course Registration System: System Specification

The development team's specification (the **system** requirements). In
Assignment 3 this was your test basis. In Assignment 4 your test basis is
`specs/user_stories.md` -- the **customer's** stories, acceptance
criteria, and agreed examples. Where the two disagree, the user stories
win: that is what acceptance testing is for.

REQ-9 to REQ-11 (the waitlist) were written by the developer from the
first draft of story US-4, *before* the three-amigos session recorded in
`specs/user_stories.md`.

## What changed since Assignment 3

- The withdrawal defect from Assignment 3, Section 4(d), is **fixed**:
  withdrawing removes only that student's enrollment (REQ-6).
- New: course **waitlists** (REQ-9 to REQ-11), `POST /waitlist`,
  `DELETE /waitlist/...`, a `waitlisted` list in the schedule, and a
  `waitlisted` notification.

## Requirements

| ID | Requirement |
|---|---|
| **REQ-1** | A student may enroll in a course only if `can_register(current_credits, course_credits, prerequisite_met)` allows it, where `current_credits` is the total credits of the courses the student is enrolled in now, and `prerequisite_met` is true when the course has no prerequisite or the student has completed it. |
| **REQ-2** | Each enrollment takes one seat. A course never has more enrolled students than its capacity, even when many students enroll at the same moment. |
| **REQ-3** | Enrolling in a course the student is already enrolled in is refused and changes nothing (no seat is taken). |
| **REQ-4** | A successful enrollment returns the student's new total credits and the semester fee, `calculate_registration_fee(total_credits)`. |
| **REQ-5** | The student is notified of every decision: a **confirmation** with the fee when enrolled (directly or from a waitlist); a **rejection** with the reason when not eligible (REQ-1) or when the course is full (REQ-2); a **waitlisted** message with the position when placed on a waitlist. Requests that are invalid, name an unknown student or course, or are duplicates send no notification. |
| **REQ-6** | A student can withdraw from a course. Withdrawing frees exactly one seat and removes only that student's enrollment. |
| **REQ-7** | A student's schedule lists their courses, total credits, semester fee, and the waitlists they are on, each with their position. |
| **REQ-8** | Every request except `GET /health` needs the header `X-API-Key: registrar-key`. Every response, including every error, is JSON. |
| **REQ-9** | A student may join the waitlist of a course that is **full**, if they are eligible for it (REQ-1), not enrolled in it, and not already on its waitlist. Students are placed on the waitlist in the order they join; the response gives their position, starting at 1. |
| **REQ-10** | When a seat opens in a course (REQ-6), it is offered to the first student on the waitlist, who is removed from the waitlist. If that student is eligible (REQ-1) they are enrolled and sent a confirmation with the fee; otherwise they are sent a rejection with the reason. |
| **REQ-11** | A student can leave a waitlist. |

## Architecture

```
HTTP client --IP1--> api.py --IP2--> RegistrationService --IP3--> RegistrationRepository --IP4--> SQLite
                                        |        |
                                        |        +--IP5--> notifier (send_confirmation / send_rejection / send_waitlisted)
                                        +--> registration.py (can_register, calculate_registration_fee)
```

## HTTP API

| Request | Success | Errors |
|---|---|---|
| `GET /health` (no key) | `200 {"status": "ok"}` | `503` if the database is unreachable |
| `POST /enrollments` body `{"student_id": "S01", "course_code": "SE413"}` | `201` with `{"student_id", "course_code", "credits", "total_credits", "fee"}` | `400` invalid body (each id: 1-20 letters or digits); `401` no/wrong key; `404` unknown student or course; `409` `course is full` or `already enrolled`; `422` not eligible, message `prerequisite <code> not completed` or `credit limit exceeded` |
| `DELETE /enrollments/<student_id>/<course_code>` | `204` | `404` `not enrolled` |
| `POST /waitlist` body `{"student_id": "S04", "course_code": "SE499"}` | `201` with `{"student_id", "course_code", "position"}` | `400`, `401`, `404` as above; `409` `course has open seats`, `already enrolled`, or `already on waitlist`; `422` not eligible (as above) |
| `DELETE /waitlist/<student_id>/<course_code>` | `204` | `404` `not on waitlist` |
| `GET /students/<student_id>/schedule` | `200` with `{"student_id", "courses": [{"code", "title", "credits"}], "total_credits", "fee", "waitlisted": [{"code", "title", "position"}]}` | `404` unknown student |
| `GET /courses/<code>` | `200` with `{"code", "title", "credits", "capacity", "seats_taken", "prerequisite"}` | `404` unknown course |

Every error body is `{"error": "<message>"}`.

## Notifications

`serve.py` writes each notification as one JSON line to its **outbox**
file (in production this would be email):

```json
{"type": "confirmation", "student_id": "S01", "course_code": "SE413", "fee": 300.0}
{"type": "rejection", "student_id": "S13", "course_code": "SE413", "reason": "prerequisite CIS350 not completed"}
{"type": "waitlisted", "student_id": "S04", "course_code": "SE499", "position": 1}
```

## Seed data (a new database started by `serve.py`)

| Course | Title | Credits | Capacity | Prerequisite |
|---|---|---|---|---|
| CIS350 | Intro to Software Engineering | 4 | 40 | -- |
| SE413 | Software Testing | 3 | 30 | CIS350 |
| SE499 | Capstone Seminar | 3 | **3** | CIS350 |
| MTH201 | Calculus I | 4 | 40 | -- |
| HIS105 | World History | 4 | 40 | -- |
| PHY230 | Physics I | 4 | 40 | -- |
| CHM110 | Chemistry I | 4 | 40 | -- |
| ENG150 | Academic Writing | 3 | 40 | -- |
| ART101 | Drawing Studio | 1 | **1** | -- |

| Students | Completed | Enrolled in |
|---|---|---|
| S01 ... S12 | CIS350 | nothing |
| S13 | nothing | nothing |
| S14 | CIS350 | MTH201, HIS105, PHY230, ENG150 (15 credits) |

Every waitlist starts empty. `serve.py --db <file>` reuses an existing
database as it is (no re-seeding), so enrollments and waitlists survive a
restart.
