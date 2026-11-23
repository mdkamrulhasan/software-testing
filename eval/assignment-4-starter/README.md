# Assignment 4 — Acceptance Testing (Starter Code)

This is the starter code for SE 413/513 Assignment 4. It is the **Course
Registration System** from Assignment 3, with one new feature: course
**waitlists** (story US-4). Everything in `src/`, `serve.py`, and
`tests/system/` is provided and **must not be modified**.

Two documents describe the system, and they do not agree:

- `SPEC.md` -- the development team's **system** specification
  (REQ-1 to REQ-11). The developer wrote REQ-9 to REQ-11 from the first
  draft of US-4. The provided system tests check it, and they all pass.
- `specs/user_stories.md` -- the **customer's** stories, acceptance
  criteria, and the examples agreed in a three-amigos session. This is
  the test basis for your acceptance tests.

## Project layout

```
assignment-4/
|-- src/                       (provided; registration, db, repository, service,
|                               notifier, errors, api -- now with waitlists)
|-- serve.py                   (provided) runs the whole system as one process
|-- SPEC.md                    (provided) system requirements REQ-1..11, HTTP API, seed data
|-- specs/user_stories.md      (provided; you add examples for US-1)
|-- tests/
|   |-- conftest.py            (PROVIDED harness: start_system, system, restart())
|   |-- system/test_waitlist_system.py  (PROVIDED: the developer's system tests)
|   `-- acceptance/
|       |-- conftest.py        (step library provided; you add four Then steps)
|       |-- features/schedule.feature   (worked example, US-3.1)
|       |-- features/*.feature (yours: enrollment, waitlist, operations)
|       `-- test_*.py          (one per feature file; stubs provided)
|-- pyproject.toml, requirements.txt
`-- README.md                  (this file; add your answers below)
```

## Setup

```
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # now includes pytest-bdd
```

## Running the system by hand

```
python serve.py
```

prints `READY url=http://127.0.0.1:8000 outbox=...`. In a second terminal,
fill SE499 (3 seats) and join its waitlist:

```
for s in S01 S02 S03; do
  curl -X POST http://127.0.0.1:8000/enrollments -H 'X-API-Key: registrar-key' \
       -H 'Content-Type: application/json' -d "{\"student_id\": \"$s\", \"course_code\": \"SE499\"}"
done
curl -X POST http://127.0.0.1:8000/waitlist -H 'X-API-Key: registrar-key' \
     -H 'Content-Type: application/json' -d '{"student_id": "S04", "course_code": "SE499"}'
curl -X DELETE http://127.0.0.1:8000/enrollments/S01/SE499 -H 'X-API-Key: registrar-key'
curl http://127.0.0.1:8000/students/S04/schedule -H 'X-API-Key: registrar-key'
```

(On Windows PowerShell, use `curl.exe` and escape the inner quotes, or use
Python's `requests`.) `python serve.py --db reg.db` keeps the database
between runs.

## Running the tests

From the project root:

```
pytest                                     # everything
pytest -m system                           # the developer's system tests (provided)
pytest -m acceptance                       # your acceptance scenarios
pytest -m operational                      # your operational acceptance checks
pytest tests/acceptance --gherkin-terminal-reporter -vv   # the report for the product owner
```

## The provided step library

`tests/acceptance/conftest.py` already defines these steps; your
`.feature` lines must match them word for word (students are `S01`...,
courses `SE499`...; lists read `S01, S02 and S03`):

```
Given the students and courses in SPEC.md
Given S01, S02 and S03 are enrolled in SE499         (or: S01 is enrolled in ART101)
Given S04 has enrolled in MTH201, HIS105, PHY230 and CHM110
Given S04 and S05 join the SE499 waitlist            (or: S04 joins the SE499 waitlist)
Given S04 has left the SE499 waitlist

When S01 enrolls in SE413
When S01 withdraws from SE499
When S04 joins the SE499 waitlist                    (or: S13 tries to join the SE499 waitlist)
When S04 leaves the SE499 waitlist
When S14 looks at their schedule
When the system is restarted
When a load balancer checks the system's health without credentials

Then they are enrolled with 3 credits and a fee of $300.00
Then they are told they are number 1 on the waitlist
Then S05 is enrolled in SE499                        (or: S02 and S03 are enrolled in SE499)
Then S04 is not enrolled in SE499
Then S01 has 3 credits and a fee of $300.00
Then S04 is on no waitlist
Then SE499 has 3 of 3 seats taken
Then S04 receives a message that they are number 1 on the SE499 waitlist
Then S01 receives nothing
Then they see the courses MTH201, HIS105, PHY230 and ENG150
Then they see 15 credits and a fee of $1,425.00
Then the system reports that it is healthy
```

You write four more (Section 5(a)):

```
Then they are told "course is full"
Then S05 is number 1 on the SE499 waitlist
Then S05 receives a confirmation for SE499 of $300.00
Then S13 receives a rejection for SE499 saying "prerequisite CIS350 not completed"
```

## Notes

- The starter passes all of its system tests. Some of the agreed examples
  in `specs/user_stories.md` will **fail** when you automate them. Do not
  fix the code: mark those scenarios as strict `xfail` (Section 5(c)).
- `xfail_strict = true` is set in `pyproject.toml`: an `xfail` scenario
  that unexpectedly passes is reported as a failure.
- To give one scenario of a feature file its own marker (such as
  `xfail`), bind it with `@scenario(...)` in the test module **before**
  the `scenarios(...)` call; `scenarios()` skips scenarios already bound.
- Acceptance tests must not import from `src/`: like system tests, they
  see only HTTP and the outbox, through the harness in `tests/conftest.py`.

---

## Your answers (Assignment 4)

<!-- Replace this section with the items listed in the assignment's
     Deliverables Checklist (Section 8). -->
