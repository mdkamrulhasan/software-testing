# Demo Guide — Coverage-Based Testing

Companion to the Week 7 reading, *Coverage-Based Testing: Measuring and
Interpreting Coverage with `coverage.py` and `pytest-cov`*. Copied from
`docs/DEMO_GUIDE_week06_data_flow.md`'s template, same shape, following
the reading's own section order.

**Before class:** reinstall requirements (now pins `coverage>=7.5` and adds `pytest-xdist`)
and confirm the baseline (aside from the known, intentional
non-passes carried over from Weeks 1 and 3; see below):

```bash
pip install -r requirements.txt
pytest -v
```

You should see **72 passed, 2 xfailed, 1 failed**:
- `XFAIL`: `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged).
- `XFAIL`: `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (Lecture 3's boundary bug, unchanged).
- `FAIL`: `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (same Lecture 1 bug, documented the unittest way; unchanged).

None of this week's three new tests are involved in any of the three.

Most of this lecture runs inside the demo mini-project. **Its commands
must be run from that folder**, so the report paths
(`checkout_app/checkout.py`, `tests/test_checkout_v1.py`) match the
reading:

```bash
cd demos/coverage_reports
```

`demos/coverage_reports/README.md` lists every command in order, if
you want a cheat sheet open next to the slides.

---

## Recap / What Is Coverage-Based Testing? / Types of Code Coverage

No new file. Bridge from Weeks 5–6: `tests/payments/test_transactions.py`
and `tests/billing/test_charges.py` already showed that the criteria
exist. This week is about the tool output. One question carries the
whole lecture: *which parts of the code did my tests never even run?*

## The Running Example

**Files:** `demos/coverage_reports/checkout_app/checkout.py`,
`demos/coverage_reports/tests/test_checkout_v1.py`

`checkout.py` is the reading's listing, verbatim. **Do not add a
docstring or reformat it**: every line number in every report below
depends on it. Put it on screen with line numbers and leave it there.
Ask the class to guess the v1 suite's coverage before running anything.

## Measuring Coverage with `coverage.py`

Run the reading's progression one step at a time, and have the class
explain each change in the number before showing the next run:

```bash
coverage run -m pytest tests/test_checkout_v1.py
coverage report                       # checkout.py 74%, TOTAL 81%
```

The 81% includes `tests/test_checkout_v1.py` itself, which is the
"Including test files" pitfall. Restrict measurement to the app code:

```bash
coverage run --source=checkout_app -m pytest tests/test_checkout_v1.py
coverage report -m                    # 74%   Missing: 8, 16-17, 24, 28
```

Map each `Missing` entry back to the listing aloud: the negative-quantity
`raise`, the `FLAT5` coupon, paid shipping, `format_receipt()`.

```bash
coverage run --branch --source=checkout_app -m pytest tests/test_checkout_v1.py
coverage report -m                    # 66%   Branch 10, BrPart 3
```

The number **dropped** with the same tests. That is the reading's first
warning box: a number quoted without saying whether `--branch` was on is
ambiguous.

### Making Settings Permanent

**File:** `demos/coverage_reports/coverage_settings.toml`

The reading's `[tool.coverage.*]` block, under a name nothing reads by
default. Explain why before running it: if this folder had a
`pyproject.toml`, `fail_under = 90` would have applied to every command
above, and the 81% → 74% → 66% progression could not have been shown.

```bash
coverage run --rcfile=coverage_settings.toml -m pytest tests/test_checkout_v1.py
coverage report --rcfile=coverage_settings.toml
echo $?                               # 2
```

`Coverage failure: total of 66 is less than fail-under=90`. Point at
the exit status: that nonzero exit is what lets CI stop on it.

## Integrating Coverage with `pytest`: `pytest-cov`

```bash
pytest tests/test_checkout_v1.py --cov=checkout_app --cov-branch --cov-report=term-missing
pytest tests/test_checkout_v1.py --cov=checkout_app --cov-branch --cov-fail-under=80
echo $?                               # 1
```

The table is identical to the `coverage.py` run, because it uses the
same engine. The second run prints `3 passed` *and*
`FAIL Required test coverage of 80% not reached. Total coverage: 65.52%`:
the tests passed, but the command failed. `--cov-config=coverage_settings.toml`
picks up the same settings file, which is the reading's "configure once"
tip.

## Interpreting Coverage Reports

Work the formula on the board from the v1 table: (14 + 5) / (19 + 10) =
65.5% → 66%. Then name the three partial branches (lines 7, 14, 22) and
ask why line 16 is *missing* rather than partial (it never ran at all).

### Reading the `Missing` Column

**File:** `demos/coverage_reports/tests/test_checkout_coupons_only.py`

The reading's arrow example, which the v1 suite cannot show:

```bash
coverage run --branch --source=checkout_app -m pytest tests/test_checkout_coupons_only.py
coverage report -m                    # 41%   Missing: 5-10, 16->18, 22-24, 28
```

Ask what input takes `16->18`. (An unrecognized coupon code.) That is
the key-idea box: every arrow is a question whose answer is the next
test.

### Reading the HTML Report

```bash
coverage run --branch --source=checkout_app -m pytest tests/test_checkout_v1.py
coverage html
open htmlcov/index.html               # macOS; use xdg-open / start elsewhere
```

Reproduce the reading's three figures live: the index (74% / 50% /
66%), the file view with the three yellow lines (hover over line 7),
and the toggle buttons (turn off *run* to leave a to-do list).

## Function Coverage in Practice

Same HTML report, *Functions* button. `format_receipt` is at 0%,
`apply_coupon` at 44%. Function coverage is 3/4 = 75%. Then the warning
box: `apply_coupon` counts as covered at the function level from one
`SAVE10` call.

## From Report to Tests: Closing the Gaps

**File:** `demos/coverage_reports/tests/test_checkout_v2.py`

Before opening the file, build the reading's gap → behavior → test
table with the class, one row per `Missing` entry. Spend the time on
row three: the `max(..., 0)` floor is one line that any `FLAT5` test
covers, but the behavior only shows below $5. Coverage will never ask
for that test.

```bash
pytest tests/test_checkout_v2.py --cov=checkout_app --cov-branch --cov-report=term-missing
```

100%, 9 passed. Ask: is `checkout.py` now fully tested?

### The same method, on the real suite

**Files:** `tests/orders/test_order_service.py`,
`tests/notifications/test_password_reset_service.py`,
`app/notifications/password_reset.py`

Back to the project root (`cd ../..`). These are the two gaps the
Week 5 guide left open, closed this week. To show the "before" report
live, restore the three Week 6 directories, run, and put them back:

```bash
git checkout 0d9535f -- app/notifications tests/notifications tests/orders
pytest --cov=app --cov-branch --cov-report=term-missing:skip-covered
git checkout HEAD -- app/notifications tests/notifications tests/orders
```

(`order_service.py` 80%, line 37; `password_reset.py` 63%, lines 34,
47, 50–56.) Then the current state:

```bash
pytest --cov=app --cov-branch --cov-report=term-missing:skip-covered
```

`TOTAL 113 0 34 0 100%`, with `22 files skipped due to complete
coverage`. Each gap became a behavior:
- **Line 37** → "a declined payment is reported." `DecliningPaymentStub`,
  a second canned answer next to Week 4's `PaymentStub`.
- **Lines 47, 50–56** (`SmtpEmailClient`) → "the message goes to the
  configured host" and "the connection is closed even when sending
  fails" (the `finally`). Both are tested by patching `smtplib.SMTP`
  (Week 5's mocking), so no mail server is involved.
- **Line 34** (`EmailClient.send`'s `raise NotImplementedError`) →
  excluded with `# pragma: no cover` and a comment giving the reason.
  This is the reading's Best Practice 7. Ask the class whether the
  exclusion would pass code review. (It should: an abstract method has
  no behavior.) Contrast it with excluding `SmtpEmailClient` because it
  seemed hard to test, which Week 5 nearly did.

## What Coverage Cannot Tell You

Back in `demos/coverage_reports/`.

**Limitation 1, execution is not verification.**
**File:** `tests/test_checkout_noassert.py`

```bash
pytest tests/test_checkout_noassert.py --cov=checkout_app --cov-branch --cov-report=term-missing
```

100%, no assertions. Ask what bug this test *would* catch. (Only one
that raises an unexpected exception.)

**Limitation 2, branches are not conditions.** No new file. On line 22
of the listing: in v2, `amount >= 50` is evaluated exactly once, for the
$20 non-member, and is False. Line 22's True outcome always comes from
`is_member`, so the "free over $50" rule has never been true, and the
report shows no gap.

**Limitation 3, coverage cannot see boundaries.** A live edit:

```bash
sed -i.bak 's/amount >= 50/amount > 50/' checkout_app/checkout.py    # or edit by hand
pytest tests/test_checkout_v2.py --cov=checkout_app --cov-branch --cov-report=term-missing
mv checkout_app/checkout.py.bak checkout_app/checkout.py             # or: git checkout -- checkout_app/checkout.py
```

Still 9 passed, still 100%. The test that would catch it,
`shipping_fee(50.0, False) == 0.0`, is Exercise 4: let the class
write it rather than showing it. The tip box introduces mutation
testing (`mutmut`). It is only named here and is covered later in the
course.

**Limitation 4, missing code.** No code. Case-insensitive coupons
(`"save10"`) have no line to be uncovered.

## Best Practices / Common Mistakes

No new code. Each item points at something already run today:
- Branches, not statements → 74% vs. 66%.
- Measure the right code → 81% with test files included.
- Exclude sparingly and visibly → the `EmailClient.send` pragma.
- Writing tests to hit lines → `test_checkout_noassert.py`.
- Treating 100% as done → the boundary mutant.
- Stale data → `coverage erase`.

## Applying This to Your Semester Project

No code. Point teams at `pytest --cov=app --cov-branch
--cov-report=term-missing:skip-covered` from the project root as the
shape of a per-module report, and at the Track A advice: take a baseline
*before* adding tests.

## Practice Exercises / Discussion Questions

Intentionally **not** implemented, the same way Weeks 3–6 left their
exercises. Exercise 2's report was verified against `checkout.py`
(62%, `7-9, 15, 16->18, 24`). Students can reproduce it by putting the
four calls in a new file under `demos/coverage_reports/tests/`.
Exercise 3 is this lecture's demo, done by the students. Exercise 4 is
the boundary test above.

## Key Takeaways for SE 413/513

No code. Close with the reading's takeaway list.

---

## Companion mini-deck: `coverage.py` vs. `pytest-cov`

**Folder:** `demos/coverage_vs_pytest_cov/` (run from inside it)

For the standalone 10-slide deck on how the two tools relate
(`lectures/F26/7.2_Coverage_py_vs_pytest-cov.pdf`). It uses
its own `tempconv` package, so its line numbers are independent of
`checkout_app`. `demos/coverage_vs_pytest_cov/README.md` lists every
command slide by slide, with the expected output. The two runs worth
doing live:

- **Shared data file:** `pytest --cov=tempconv --cov-branch`, then
  `coverage report -m` with no re-run: same 67% table.
- **Parallel workers:** `pytest -n 2 --cov=tempconv --cov-branch` reports
  67%, but `coverage run --branch --source=tempconv -m pytest -n 2`
  reports 0% with "No data was collected". Needs `pytest-xdist`, now in
  `requirements.txt`.

Afterwards, `coverage erase && rm -rf htmlcov` in that folder too.

---

## After class

From `demos/coverage_reports/`, confirm `checkout_app/checkout.py` is
unmodified (`git status .` is clean, and no `.bak` file is left), then
`coverage erase && rm -rf htmlcov`. From the project root, confirm
`pytest -v` is back to the expected **72 passed, 2 xfailed, 1 failed**
baseline. (`demos/` is never part of a plain `pytest` run, so it can't
affect the baseline either way.)

## Extending this for the *next* lecture

1. Add new app code under `app/<some_subpackage>/`. Only create a new
   top-level `app/` subpackage if the feature doesn't fit under
   billing/pricing/reports/payments/accounts/notifications/orders.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path,
   and check `pytest --cov=app --cov-branch
   --cov-report=term-missing:skip-covered` still lists nothing. Every
   `app/` module is at 100% branch coverage as of this week, so any gap
   that appears is new.
3. Put deliberately incomplete or buggy illustrations under
   `demos/<short_topic_name>/`, where a plain `pytest` won't pick them
   up (`testpaths = tests` in `pytest.ini`). If, like
   `coverage_reports/`, it needs report paths or line numbers to match a
   reading exactly, make it a self-contained folder run from inside.
4. Copy this file as a starting template for the next lecture's guide.
