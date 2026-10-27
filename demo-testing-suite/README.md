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
- `docs/DEMO_GUIDE_week05_mocking_coverage.md` — the same, for Week 5
  (Mock vs. MagicMock; Control-Flow Graphs and Statement, Branch, and
  Path Coverage).
- `docs/DEMO_GUIDE_week06_data_flow.md` — the same, for Week 6
  (Data-Flow Testing and Coverage Concepts).
- `docs/DEMO_GUIDE_week07_coverage_based_testing.md` — the same, for
  Week 7 (Coverage-Based Testing with `coverage.py` and `pytest-cov`).
- `docs/DEMO_GUIDE_week08_functional_testing.md` — the same, for
  Weeks 8–9 (Functional Testing: decision tables, state transitions,
  pairwise, and property-based testing).
- `docs/DEMO_GUIDE_week10_integration_testing.md` — the same, for
  Week 10 (Integration Testing: strategies, design/API reviews, APIs,
  databases, external services, and test doubles).
- `docs/CHANGE_SUMMARY_weekNN.pdf` — student-facing, week-by-week
  summaries of what changed in this codebase and why.
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
  billing/charges.py         Week 6 — data-flow worked example
                               (sum_positive: defs, uses, DU pairs,
                               a loop-carried pair)
  pricing/discounts.py       Week 2
  pricing/cart.py            Week 2
  pricing/shipping.py        Week 3 (EP / BVA / negative testing)
  pricing/membership.py      Week 5 — statement vs. branch coverage example
  reports/report_writer.py   Week 2
  payments/api_client.py     Week 2
  payments/transactions.py   Week 5 — control-flow-graph examples
                               (classify_transaction, contains_negative)
  accounts/user_repository.py Week 2 — built for later
                               lectures (mocking, integration testing)
                               and the final project to extend; Week 10
                               added create_schema(), the production
                               `users` schema (NOT NULL UNIQUE names)
  accounts/registration_service.py Week 4 — mocks UserRepository
                               instead of sqlite3, per that file's own
                               Week 2 docstring
  notifications/password_reset.py  Week 4 — "Dependency Isolation and
                               Seams" worked example (the DI seam itself)
  orders/order_service.py          Week 4 — "Test Double Taxonomy"
                               worked example: dummy, stub, fake, spy, mock
  accounts/user_lookup.py          Week 5 — Mock vs. MagicMock worked
                               examples: len, indexing, `in`, iteration,
                               `with`, a DB cursor

tests/                  The "real" growing suite — mirrors app/'s layout
  conftest.py               Project-wide fixtures (empty so far — see its docstring)
  integration/              Week 10: tests that assemble REAL components
                             (UserRegistrationService + UserRepository +
                             a SQLite file); marked `integration`. The one
                             folder that does not mirror app/, because
                             its tests span several app/ modules
  legacy/                   Week 1's unittest-style tests, kept for the "Revisited" slide
  billing/  pricing/  reports/  payments/  accounts/  notifications/  orders/
    pricing/test_shipping.py     Week 3's EP/BVA/negative-testing suite
    notifications/test_password_reset_service.py  Week 4's DI-seam +
      "mocks that lie" tests
    orders/test_order_service.py                   Week 4's test-double
      taxonomy suite (dummy/stub/fake/spy/mock)
    accounts/test_registration_service.py          Week 4's
      UserRepository-mocking suite
    accounts/test_user_lookup.py                   Week 5's MagicMock suite
    payments/test_transactions.py                  Week 5's CFG / path /
      basis-path suite
    pricing/test_membership.py                     Week 5's statement-vs-
      branch coverage pair
    billing/test_charges.py                        Week 6's DU-pair suite:
      test ids name the criterion (All-Defs / All-Uses / All-DU-Paths)
      and the pairs each test covers
    orders/ + notifications/                       Week 7 closed the two
      gaps the whole-suite coverage report had shown since Week 4
      (a declined-payment stub; SmtpEmailClient vs. a patched smtplib)

  practice/                 In-class live-coding scripts — not named
                             `test_*.py`, so plain `pytest` skips them
    tdd_password_demo.py      Week 4's Red-Green-Refactor script

demos/                  Deliberately isolated teaching examples — NOT
                        swept into a plain `pytest` run (see pytest.ini)
  scope_pitfall/            The flaky-test pitfall, run on its own
  module_scope_db/          The scope="module" contrast case
  conftest_hierarchy/       An on-disk copy of the "conftest.py Hierarchy" slide's diagram
  coverage_gaps/            Week 5: deliberately under-tested code whose
                             pytest-cov reports reproduce the reading
                             (`2->4` branch gap; a "goto fail" analogue)
  data_flow/                Week 6: a broken loop-carried DU pair that
                             still gets 100% branch coverage; an
                             All-Defs set that leaves a branch untested;
                             use-before-def and dead-def anomalies for
                             pylint to find statically
  coverage_reports/         Week 7: a self-contained mini-project (its own
                             checkout_app/ and tests/) that reproduces
                             every coverage.py / pytest-cov report in the
                             reading. Run it from inside that folder.
  coverage_vs_pytest_cov/   Week 7 mini-deck: a tiny tempconv package, a
                             CLI script, and a thin suite showing how
                             coverage.py and pytest-cov relate (shared
                             .coverage file, --append, xdist). Also run
                             from inside that folder.
  functional_testing/       Weeks 8–9: a self-contained mini-project (its own
                             shop/ and tests/) with the reading's decision
                             table, Order state machine, allpairspy rows,
                             and Hypothesis property -- plus the buggy
                             versions each technique catches. Run it from
                             inside that folder.
  integration_testing/      Week 10: a self-contained mini-project (its own
                             shop/, fakes/, specs/, tests/): a Flask API,
                             SQLite, and a fake third-party payment
                             provider over real HTTP; a written design/API
                             review whose findings trace to tests; and two
                             broken components switched in with
                             SHOP_PAYMENTS=v1 / SHOP_SERVICE=buggy. Run it
                             from inside that folder.

docs/
  DEMO_GUIDE_week02_pytest_fixtures.md         Week 2, slide-by-slide
  DEMO_GUIDE_week03_ep_bva_negative_testing.md Week 3, section-by-section
  DEMO_GUIDE_week04_tdd_test_doubles.md        Week 4, section-by-section
  DEMO_GUIDE_week05_mocking_coverage.md        Week 5, section-by-section
  DEMO_GUIDE_week06_data_flow.md               Week 6, section-by-section
  DEMO_GUIDE_week07_coverage_based_testing.md  Week 7, section-by-section
  DEMO_GUIDE_week08_functional_testing.md      Weeks 8–9, section-by-section
  DEMO_GUIDE_week10_integration_testing.md     Week 10, section-by-section
  CHANGE_SUMMARY_week0N.tex / .pdf             Student-facing change summaries

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

# Coverage (Week 5) -- always pass --cov-branch; statement coverage alone
# can look deceptively complete.
pytest --cov=app --cov-branch --cov-report=term-missing

# Whole-suite coverage (Week 7) -- every app/ module is now at 100%
# branch coverage; list only what isn't:
pytest --cov=app --cov-branch --cov-report=term-missing:skip-covered
pytest --cov=app --cov-branch --cov-report=html     # htmlcov/index.html

# Integration tests only, or everything but (Week 10) -- the
# `integration` marker is registered in pytest.ini.
pytest -m integration
pytest -m "not integration"

# Static def-use analysis (Week 6) -- finds use-before-def and dead
# definitions without running any test.
pylint demos/data_flow/anomalies.py --disable=all \
    --enable=possibly-used-before-assignment,unused-variable
```

Expect a full run of `pytest -v` to report **75 passed, 3 xfailed, 1
failed**:
- `XFAIL` — `test_calculate_late_fee[-4-0.0]` in
  `tests/billing/test_late_fees.py` (Week 1's negative-days bug).
- `XFAIL` — `test_valid_weights[5.0-10.0]` in
  `tests/pricing/test_shipping.py` (Week 3's boundary bug).
- `FAIL` — `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (the same Week 1 bug, documented the unittest way; this one is swept
  into the default run since `tests/legacy` is under `testpaths`).
- `XFAIL` (strict) — `test_failed_welcome_email_does_not_leave_a_half_registered_user`
  in `tests/integration/test_registration.py` (Week 10: `register()`
  commits the user before emailing, so a failed email leaves a user who
  was never welcomed and cannot retry; found by integration testing).

The first three are intentional, unchanged since Week 3, and explained where
they occur — see `docs/DEMO_GUIDE_week03_ep_bva_negative_testing.md` for
the full walkthrough. Week 4 is purely additive: its twelve new tests
(in `tests/notifications/`, `tests/orders/`, and
`tests/accounts/test_registration_service.py`) all pass — see
`docs/DEMO_GUIDE_week04_tdd_test_doubles.md`. Week 5 is additive too:
its twenty new tests (`tests/accounts/test_user_lookup.py`,
`tests/payments/test_transactions.py`, `tests/pricing/test_membership.py`)
all pass, and each of this week's new `app/` modules reaches 100% branch
coverage — see `docs/DEMO_GUIDE_week05_mocking_coverage.md`. Week 6 is
additive as well: its four new tests (`tests/billing/test_charges.py`)
all pass and `app/billing/charges.py` is at 100% branch coverage. Its
deliberately buggy examples live in `demos/data_flow/`, outside the
default run — see `docs/DEMO_GUIDE_week06_data_flow.md`. Week 7 adds
three tests that close the last two whole-suite coverage gaps (in
`tests/orders/` and `tests/notifications/`), all passing, which brings
every `app/` module to 100% branch coverage. Its reading-reproduction
mini-project lives in `demos/coverage_reports/`, and a second one
comparing `coverage.py` with `pytest-cov` (shared data file, `--append`,
parallel `pytest-xdist` workers) lives in `demos/coverage_vs_pytest_cov/`.
Both are outside the default run — see
`docs/DEMO_GUIDE_week07_coverage_based_testing.md`. Weeks 8–9 add nothing
to the default run, so the counts above are unchanged: its decision-table,
state-transition, pairwise, and property-based examples (and the buggy
versions they catch) live in `demos/functional_testing/` — see
`docs/DEMO_GUIDE_week08_functional_testing.md`. Week 10 adds
`tests/integration/` (three passing tests and the strict `xfail` above)
and `create_schema()` in `app/accounts/user_repository.py`; `app/` stays
at 100% branch coverage, and `pytest -m "not integration"` reproduces the
Weeks 8–9 counts exactly. Its mini-project, with the reading's shop, its
specifications, its design review, and 46 tests, lives in
`demos/integration_testing/` — see
`docs/DEMO_GUIDE_week10_integration_testing.md`.

## Extending this for the *next* lecture

1. If the next lecture needs a new function or class to build test-first
   or to isolate with a double, add it under `app/<some_subpackage>/`,
   the same way Week 3 added `shipping.py`, Week 4 added
   `notifications/password_reset.py`, `orders/order_service.py`, and
   `accounts/registration_service.py`, Week 5 added
   `accounts/user_lookup.py`, `payments/transactions.py`, and
   `pricing/membership.py`, and Week 6 added `billing/charges.py`. Only create a new top-level
   `app/` subpackage if the new feature genuinely doesn't fit under
   billing/pricing/reports/payments/accounts/notifications/orders.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
   Tests that assemble several real components go under
   `tests/integration/` instead, with `pytestmark = pytest.mark.integration`.
3. If the lecture needs a dedicated, isolated illustration (like Week
   2's `scope_pitfall/`, Week 6's `data_flow/`, Week 7's
   `coverage_reports/` and `coverage_vs_pytest_cov/`, Weeks 8–9's
   `functional_testing/`, or Week 10's `integration_testing/`), add it under `demos/<short_topic_name>/` and
   keep it out of `tests/` so a plain `pytest` doesn't pick it up (it's
   already excluded by `testpaths = tests` in `pytest.ini`).
4. Copy `docs/DEMO_GUIDE_week10_integration_testing.md` as a starting
   template for the new lecture's guide — same shape, new section names
   and file paths.

## Extending this for the final project

See `final_project/README.md`.
