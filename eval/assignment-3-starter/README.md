# Assignment 3 — Integration and System Testing (Starter Code)

This is the starter code for SE 413/513 Assignment 3. The **Course
Registration System** from Assignments 1–2 is now a small, complete
system: an HTTP API, a service, and a SQLite database, built on the same
`can_register()` and `calculate_registration_fee()` you tested before.
Everything in `src/` and `serve.py` is provided and **must not be
modified**. `SPEC.md` is the specification your tests check against.

## Project layout

```
assignment-3/
|-- src/
|   |-- registration.py      can_register(), calculate_registration_fee() (Assignments 1-2)
|   |-- db.py                schema, connect(), seed data
|   |-- repository.py        all SQL (RegistrationRepository)
|   |-- service.py           RegistrationService: enroll(), withdraw(), schedule()
|   |-- notifier.py          OutboxNotifier (used by serve.py)
|   |-- errors.py            exceptions shared by the components
|   `-- api.py               Flask HTTP API
|-- serve.py                 runs the whole system as one process
|-- SPEC.md                  requirements REQ-1..8, HTTP API, seed data
|-- tests/
|   |-- integration/conftest.py       (implement your fixtures here)
|   |-- integration/test_integration.py (implement your tests here)
|   |-- system/conftest.py            (PROVIDED: starts serve.py for each test)
|   `-- system/test_system.py         (implement your tests here)
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

## Setup

1. (Recommended) Create and activate a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Running the system by hand

```
python serve.py
```

prints `READY url=http://127.0.0.1:8000 outbox=...`. In a second terminal:

```
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/enrollments -H 'X-API-Key: registrar-key' \
     -H 'Content-Type: application/json' -d '{"student_id": "S01", "course_code": "SE413"}'
curl http://127.0.0.1:8000/students/S01/schedule -H 'X-API-Key: registrar-key'
```

(On Windows PowerShell, use `curl.exe` and escape the inner quotes, or
use Python's `requests`.) Every start uses a fresh database seeded as in
`SPEC.md`, unless you pass `--db <file>`.

## Running the tests

From the project root:

```
pytest                    # everything
pytest -m integration     # integration tests only
pytest -m system          # system tests only (each starts its own server)
```

## Notes

- Do not modify `src/` or `serve.py`. The starter contains **one known
  defect** (Section 4(d) of the assignment): document it with a test, do
  not fix it.
- Modules in `src/` are importable directly in your tests (no `src.`
  prefix), e.g. `from repository import RegistrationRepository`.
- `xfail_strict = true` is set in `pyproject.toml`: an `xfail` test that
  unexpectedly passes is reported as a failure.
- System tests must not import from `src/`: they see only HTTP and the
  outbox, through the provided `system` fixture.
