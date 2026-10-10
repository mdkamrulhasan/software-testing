# Assignment 2 — Coverage, Data-Flow Testing, and Test Doubles (Starter Code)

This is the starter code for SE 413/513 Assignment 2. `src/registration.py`
is complete and **must not be modified** — it includes the two functions
from Assignment 1 (`can_register`, `calculate_registration_fee`, unchanged)
plus two new functions this assignment targets:

- `summarize_batch_registrations(requests)` — processes a batch of
  registration requests and accumulates an approval count and total fees.
- `enroll_student(current_credits, course_credits, prerequisite_met, notifier)`
  — attempts to enroll a student and notifies the result through a
  `notifier` collaborator (`send_confirmation(fee)` / `send_rejection()`).

## Project layout

```
assignment-2/
|-- src/registration.py        (provided — do not modify)
|-- tests/test_registration.py (implement your tests here)
|-- tests/conftest.py          (implement your fixtures here)
|-- pyproject.toml
|-- README.md
```

## Setup

1. (Recommended) Create and activate a virtual environment:

   ```
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

2. Install dependencies:

   ```
   pip install pytest pytest-cov
   ```

## Running the tests

From the project root:

```
pytest
```

## Measuring coverage

`pyproject.toml` already configures branch measurement and restricts
coverage to `src/` (see `[tool.coverage.run]`). Run:

```
pytest --cov --cov-branch --cov-report=term-missing
```

This reports statement and branch coverage together, with a `Missing`
column listing uncovered lines and `a->b` arcs (uncovered branch
outcomes). Add tests until no gaps remain for
`summarize_batch_registrations` and `enroll_student` (Section 4 of the
assignment). Because the report measures the whole file, it may also list
lines inside `can_register`/`calculate_registration_fee` (lines 15-59) —
those were already covered in Assignment 1 and are **not** part of this
assignment's coverage target; only close gaps inside
`summarize_batch_registrations` and `enroll_student` (lines 62 onward).

To see statement-only coverage for comparison (Section 4c), drop
`--cov-branch`:

```
pytest --cov --cov-report=term-missing
```

## Notes

- Do not modify `src/registration.py`. If you believe there is a defect in
  it, contact the instructor rather than changing it yourself.
- `registration` is importable directly in your tests (no `src.` prefix
  needed), e.g. `from registration import can_register`.
- The four markers from Assignment 1 (`unit`, `positive`, `negative`,
  `boundary`) are already registered in `pyproject.toml` if you find them
  useful here; this assignment does not require new markers.
