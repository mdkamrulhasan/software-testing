# SE 413/513 — Software Testing: Running Demo Application & Test Suite

This is the shared codebase behind the in-class pytest demos. It is
meant to **grow week over week** rather than being rebuilt from scratch
for each lecture. If you're returning to this after time away, start
here.

Companion pieces:
- `docs/DEMO_GUIDE_week02_pytest_fixtures.md` — slide-by-slide, what to
  run and say during *this* lecture.
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
  pricing/discounts.py       Week 2 (this lecture)
  pricing/cart.py            Week 2 (this lecture)
  reports/report_writer.py   Week 2 (this lecture)
  payments/api_client.py     Week 2 (this lecture)
  accounts/user_repository.py Week 2 (this lecture) — built for later
                               lectures (mocking, integration testing)
                               and the final project to extend

tests/                  The "real" growing suite — mirrors app/'s layout
  conftest.py               Project-wide fixtures (empty so far — see its docstring)
  legacy/                   Week 1's unittest-style tests, kept for the "Revisited" slide
  billing/  pricing/  reports/  payments/  accounts/

demos/                  Deliberately isolated teaching examples — NOT
                        swept into a plain `pytest` run (see pytest.ini)
  scope_pitfall/            The flaky-test pitfall, run on its own
  module_scope_db/          The scope="module" contrast case
  conftest_hierarchy/       An on-disk copy of the "conftest.py Hierarchy" slide's diagram

docs/
  DEMO_GUIDE_week02_pytest_fixtures.md   Slide-by-slide: what to run, when, why

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

Expect one `XFAIL` in the full run (`test_calculate_late_fee[-4-0.0]` in
`tests/billing/test_late_fees.py`) and one `FAIL` if you run
`tests/legacy/test_late_fees_unittest.py` on its own — both are
intentional and explained where they occur.

## Extending this for the *next* lecture (Equivalence Partitioning & BVA)

1. If the next lecture needs a new function to analyze for boundaries,
   add it under `app/<some_subpackage>/`, the same way this lecture
   added `discounts.py`: one function or small class, one clear
   docstring, one "why this exists" note if it's not obvious.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
   Only create a new top-level `app/` subpackage if the new feature
   genuinely doesn't fit under billing/pricing/reports/payments/accounts.
3. If the lecture needs a dedicated, isolated illustration (like this
   lecture's `scope_pitfall/`), add it under `demos/<short_topic_name>/`
   and keep it out of `tests/` so a plain `pytest` doesn't pick it up
   (it's already excluded by `testpaths = tests` in `pytest.ini`).
4. Copy `docs/DEMO_GUIDE_week02_pytest_fixtures.md` as a starting
   template for the new lecture's guide — same table shape, new slide
   names and file paths.

## Extending this for the final project

See `final_project/README.md`.
