# Course Registration System: Specification

The test basis for Assignment 3. The numbered requirements are what your
tests trace to (put the IDs in your test docstrings).

## Requirements

| ID | Requirement |
|---|---|
| **REQ-1** | A student may enroll in a course only if `can_register(current_credits, course_credits, prerequisite_met)` allows it, where `current_credits` is the total credits of the courses the student is enrolled in now, and `prerequisite_met` is true when the course has no prerequisite or the student has completed it. |
| **REQ-2** | Each enrollment takes one seat. A course never has more enrolled students than its capacity, **even when many students enroll at the same moment**. |
| **REQ-3** | Enrolling in a course the student is already enrolled in is refused and changes nothing (no seat is taken). |
| **REQ-4** | A successful enrollment returns the student's new total credits and the semester fee, `calculate_registration_fee(total_credits)`. |
| **REQ-5** | The student is notified of every decision: a **confirmation** with the fee when enrolled; a **rejection** with the reason when not eligible (REQ-1) or when the course is full (REQ-2). Requests that are invalid, name an unknown student or course, or are duplicates (REQ-3) send no notification. |
| **REQ-6** | A student can withdraw from a course. Withdrawing frees exactly one seat and removes **only that student's** enrollment. |
| **REQ-7** | A student's schedule lists their courses, total credits, and semester fee. |
| **REQ-8** | Every request except `GET /health` needs the header `X-API-Key: registrar-key`. Every response, including every error, is JSON -- never an HTML page or a stack trace, whatever the request contains. |

## Architecture

```
HTTP client --IP1--> api.py --IP2--> RegistrationService --IP3--> RegistrationRepository --IP4--> SQLite
                                        |        |
                                        |        +--IP5--> notifier (send_confirmation / send_rejection)
                                        +--> registration.py (can_register, calculate_registration_fee)
```

## HTTP API

| Request | Success | Errors |
|---|---|---|
| `GET /health` (no key) | `200 {"status": "ok"}` | `503` if the database is unreachable |
| `POST /enrollments` body `{"student_id": "S01", "course_code": "SE413"}` | `201` with `{"student_id", "course_code", "credits", "total_credits", "fee"}` | `400` invalid body (each id: 1-20 letters or digits); `401` no/wrong key; `404` unknown student or course; `409` `course is full` or `already enrolled`; `422` not eligible, message `prerequisite <code> not completed` or `credit limit exceeded` |
| `DELETE /enrollments/<student_id>/<course_code>` | `204` | `404` `not enrolled` |
| `GET /students/<student_id>/schedule` | `200` with `{"student_id", "courses": [{"code", "title", "credits"}], "total_credits", "fee"}` | `404` unknown student |
| `GET /courses/<code>` | `200` with `{"code", "title", "credits", "capacity", "seats_taken", "prerequisite"}` | `404` unknown course |

Every error body is `{"error": "<message>"}`.

## Notifications

`serve.py` writes each notification as one JSON line to its **outbox**
file (in production this would be email):

```json
{"type": "confirmation", "student_id": "S01", "course_code": "SE413", "fee": 300.0}
{"type": "rejection", "student_id": "S13", "course_code": "SE413", "reason": "prerequisite CIS350 not completed"}
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
