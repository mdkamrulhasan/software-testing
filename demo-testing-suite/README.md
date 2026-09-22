# SE 413/513 — Software Testing: Running Demo Application & Test Suite

This is the shared codebase behind the in-class pytest demos. It is
meant to **grow week over week** rather than being rebuilt from scratch
for each lecture. If you're returning to this after time away, start
here.

Companion pieces:
- `docs/DEMO_GUIDE_week02_pytest_fixtures.md` — slide-by-slide, what to
  run and say during the Week 2 (pytest fixtures) lecture.
- `docs/DEMO_GUIDE_week03_ep_bva_negative_testing.md` — the same, for
  Week 3 (Equivalence Partitioning, Boundary-Value Analysis, and
  Negative Testing).
- `docs/DEMO_GUIDE_week04_tdd_test_doubles.md` — the same, for Week 4
  (Test-Driven Development, Mocking, and Dependency Isolation).
- `final_project/README.md` — how the final project is meant to build
  on everything here.

## Why one shared app instead of one folder per lecture

`calculate_late_fee` and the shopping-cart functions already appear in
two lectures (Testing Foundations, then this one) and are referenced
again in this lecture's discussion prompt and its teaser for next time.
Duplicating them per-lecture folder would let the running examples
silently drift out of sync, and it throws away a real teaching
opportunity: students seeing the *same* `calculate_late_fee` bug persist
across weeks, get documented with `xfail` here, and (presumably) get
properly fixed in a later lecture, is a more honest picture of how real
defects live in real codebases than a fresh bug invented every week.

## Layout

```
app/                    The "system under test" — grows one feature at a time
  billing/late_fees.py       Week 1 (Testing Foundations)
  pricing/discounts.py       Week 2
  pricing/cart.py            Week 2
  pricing/shipping.py        Week 3 (EP / BVA / negative testing)
  reports/report_writer.py   Week 2
  payments/api_client.py     Week 2
  accounts/user_repository.py Week 2 — built for later
                               lectures (mocking, integration testing)
                               and the final project to extend
  accounts/registration_service.py Week 4 — mocks UserRepository
                               instead of sqlite3, per that file's own
                               Week 2 docstring
  notifications/password_reset.py  Week 4 (TDD / mocking / dependency
                               isolation) — dummy, stub, fake, spy, mock

tests/                  The "real" growing suite — mirrors app/'s layout
  conftest.py               Project-wide fixtures (empty so far — see its docstring)
  legacy/                   Week 1's unittest-style tests, kept for the "Revisited" slide
  billing/  pricing/  reports/  payments/  accounts/  notifications/
    pricing/test_shipping.py     Week 3's EP/BVA/negative-testing suite
    notifications/test_password_reset_service.py  Week 4's test-double
      taxonomy suite (dummy/stub/fake/spy/mock)
    accounts/test_registration_service.py          Week 4's
      UserRepository-mocking suite

  practice/                 In-class live-coding scripts — not named
                             `test_*.py`, so plain `pytest` skips them
    tdd_password_demo.py      Week 4's Red-Green-Refactor script

demos/                  Deliberately isolated teaching examples — NOT
                        swept into a plain `pytest` run (see pytest.ini)
  scope_pitfall/            The flaky-test pitfall, run on its own
  module_scope_db/          The scope="module" contrast case
  conftest_hierarchy/       An on-disk copy of the "conftest.py Hierarchy" slide's diagram

docs/
  DEMO_GUIDE_week02_pytest_fixtures.md         Week 2, slide-by-slide
  DEMO_GUIDE_week03_ep_bva_negative_testing.md Week 3, section-by-section
  DEMO_GUIDE_week04_tdd_test_doubles.md        Week 4, section-by-section

final_project/          Scaffold + a stated working assumption — read
                        before assigning
```

## Running things

```bash
pip install -r requirements.txt

pytest                          # the real suite: everything under tests/
pytest -v                       # same, with each test named
pytest tests/billing            # just one subpackage
pytest demos/scope_pitfall -v   # a demo folder, run explicitly (not part of the main suite)
```

Expect a full run of `pytest -v` to report **43 passed, 2 xfailed, 1
failed**:
- `XFAIL` — `test_calculate_late_fee[-4-0.0]` in
  `tests/billing/test_late_fees.py` (Week 1's negative-days bug).
- `XFAIL` — `test_valid_weights[5.0-10.0]` in
  `tests/pricing/test_shipping.py` (Week 3's boundary bug).
- `FAIL` — `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (the same Week 1 bug, documented the unittest way; this one is swept
  into the default run since `tests/legacy` is under `testpaths`).

All three are intentional, unchanged since Week 3, and explained where
they occur — see `docs/DEMO_GUIDE_week03_ep_bva_negative_testing.md` for
the full walkthrough. Week 4 is purely additive: its ten new tests (in
`tests/notifications/` and `tests/accounts/test_registration_service.py`)
all pass — see `docs/DEMO_GUIDE_week04_tdd_test_doubles.md`.

## Extending this for the *next* lecture

1. If the next lecture needs a new function or class to build test-first
   or to isolate with a double, add it under `app/<some_subpackage>/`,
   the same way Week 3 added `shipping.py` and Week 4 added
   `notifications/password_reset.py` and
   `accounts/registration_service.py`. Only create a new top-level
   `app/` subpackage if the new feature genuinely doesn't fit under
   billing/pricing/reports/payments/accounts/notifications.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
3. If the lecture needs a dedicated, isolated illustration (like Week
   2's `scope_pitfall/`), add it under `demos/<short_topic_name>/` and
   keep it out of `tests/` so a plain `pytest` doesn't pick it up (it's
   already excluded by `testpaths = tests` in `pytest.ini`).
4. Copy `docs/DEMO_GUIDE_week04_tdd_test_doubles.md` as a starting
   template for the new lecture's guide — same shape, new section names
   and file paths.

## Extending this for the final project

See `final_project/README.md`.
