# Demo Guide — Data-Flow Testing and Coverage Concepts

Companion to the Week 6 reading, *Data-Flow Testing and Coverage
Concepts*. Copied from `docs/DEMO_GUIDE_week05_mocking_coverage.md`'s
template, same shape, following the reading's own section order.

**Before class:** install the new `pylint` dependency and confirm the
baseline is green (aside from the known, intentional non-passes
carried over from Weeks 1 and 3; see below):

```bash
pip install -r requirements.txt      # now includes pylint
pytest -v
```

You should see **69 passed, 2 xfailed, 1 failed**:
- `XFAIL`: `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged).
- `XFAIL`: `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (Lecture 3's boundary bug, unchanged).
- `FAIL`: `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (same Lecture 1 bug, documented the unittest way; unchanged).

None of this week's four new tests are involved in any of the three.
This week is purely additive.

---

## From Control Flow to Data Flow

No new file. Bridge from Week 5: point at
`tests/payments/test_transactions.py` and ask what its 100% branch
coverage report says about the *values* computed. (Nothing.) That
question is this week's reading in one line.

## Definitions and Uses

**File:** `app/billing/charges.py`

`sum_positive()` is the reading's worked example, verbatim, with its
`# S1`–`# S5` labels. In billing terms: statement line items are
charges (positive) and credits/refunds (zero or negative); only the
charges are summed. Before showing the module docstring's def/use
table, have the class tag each line **D**, **C**, or **P** for `total`
and `n` (the reading's tip box). S4 is the one to dwell on: a c-use of
`total` *and* a def of `total` in the same statement.

## Why Data-Flow Testing Matters

**Files:** `demos/data_flow/anomalies.py`,
`demos/data_flow/test_anomalies.py`

Two of the reading's three anomaly patterns, deliberately shipped:
`describe_balance()` (**use before def** — `status` is never assigned
when `balance == 0`) and `apply_payment()` (**dead definition** —
`remaining` is computed and never read). Run the tests with coverage
first:

```bash
pytest demos/data_flow/test_anomalies.py -v \
    --cov=anomalies --cov-branch --cov-report=term-missing
```

All three tests pass, every statement ran (Miss 0), and the report is
92% with `34->36` missing. Ask what that edge is. (The `elif`'s False
edge: `balance == 0`.) Branch coverage hints at the first bug only as a
missing edge, and says nothing at all about the second.

Then the static view, with no tests at all:

```bash
pylint demos/data_flow/anomalies.py --disable=all \
    --enable=possibly-used-before-assignment,unused-variable
```

```
demos/data_flow/anomalies.py:36:25: E0606: Possibly using variable 'status' before assignment (possibly-used-before-assignment)
demos/data_flow/anomalies.py:40:4: W0612: Unused variable 'remaining' (unused-variable)
```

That is the reading's "Data-Flow Testing in Practice" section live:
static analyzers do def-use analysis internally. Finish by
uncommenting `test_zero_balance` at the bottom of `test_anomalies.py`
and watching it fail with `UnboundLocalError`. Worth saying aloud:
Python *crashes* on a use before def; the reading's point is that
other languages may silently return garbage or a stale value instead.

The OpenSSL case study has no code; it is the reading's third pattern
(a definition that should have reached the seed was removed).

## Def-Use Relationships / A Worked Example: `sum_positive()`

**File:** `tests/billing/test_charges.py`

The module docstring is the reading's seven-pair table, with a
"covered by" column naming the test id that covers each pair. Draw
the annotated CFG (reading's Figure 1) and trace pair #3 — D2 at S4
back around the loop to S4 — before running anything.

```bash
pytest tests/billing/test_charges.py -v \
    --cov=app.billing.charges --cov-branch --cov-report=term-missing
```

The ids read as the reading's argument, in order:

1. `all-defs:credit-only` (`[-1]`) and `all-defs:one-charge` (`[3]`):
   the All-Defs set. Already 100% branch coverage in this function.
2. `all-uses:two-charges` (`[3, 5]`): the only test that exercises the
   loop-carried pair #3. Adds no new statement or branch; adds the
   pair.
3. `du-path:loop-carried-via-credit` (`[3, -2, 5]`): pair #3 again,
   but along the *other* back edge (S3 false, a skipped credit). No
   new DU pair, so All-Uses doesn't require it; it is what
   All-DU-Paths asks for.

## Data-Flow Coverage Criteria / How the Criteria Relate

**Files:** `demos/data_flow/accumulator_bug.py`,
`demos/data_flow/test_accumulator_bug.py`

The payoff demo. Same function, with S4 broken to `total = 0 + n` —
each charge kills the running total instead of adding to it (the
reading's "killed definition" pattern), and pair #3 no longer exists.

```bash
pytest demos/data_flow/test_accumulator_bug.py -v \
    --cov=accumulator_bug --cov-branch --cov-report=term-missing
```

The two All-Defs tests **pass**, the report says **100% statement and
branch coverage**, and only `test_all_uses_two_charges_exposes_the_bug`
fails (`assert 5 == 8`). This is the reading's mental-model prompt:
"Branch coverage ... says nothing about whether the accumulated value
was ever actually checked after more than one update." It is also the
answer to Exercise 5.

**Files:** `demos/data_flow/receipt.py`,
`demos/data_flow/test_receipt.py`

The reading's third "How the Criteria Relate" bullet — **All-Defs does
not subsume branch coverage** — is only asserted in the reading
(`sum_positive()` happens to cover both branches anyway). This shows
it:

```bash
pytest demos/data_flow/test_receipt.py \
    --cov=receipt --cov-branch --cov-report=term-missing
```

One test satisfies All-Defs (walk the def/use table in `receipt.py`'s
docstring), and the report is **75%**, BrPart 1, line 33 missing.
Uncomment `test_total_with_breakdown` at the bottom of the test file:
All-Uses is reached and the report goes to 100%.

## Data-Flow Testing in Practice

Already shown with `pylint` above. If time allows, point out that
neither `coverage.py` nor `pytest-cov` has a data-flow mode: the
pair-by-pair bookkeeping in `test_charges.py`'s docstring was done by
hand, exactly as the reading says it usually is.

## Common Pitfalls / A Practical Mental Model / Summary

No code. Each pitfall has a file to point at:
- "DU pair vs. textual proximity": S4's own def and use.
- "Assuming All-Defs is enough": `test_accumulator_bug.py`.
- "Overlooking loop-carried pairs": pair #3 in `test_charges.py`.

## Practice Exercises / Discussion Questions

`first_negative()` (Exercises 1–4) is intentionally **not**
implemented, the same way Weeks 3–5 left their exercises. Work it on
paper first, then have students write the function and parametrized
tests whose ids name the DU pairs, as `test_charges.py` does. Exercise
5 is the accumulator-bug demo above.

## Key Takeaways for SE 413/513

No code. Close with the reading's takeaway list.

---

## After class

Confirm `pytest -v` from the project root is back to the expected
**69 passed, 2 xfailed, 1 failed** baseline. Re-comment any test you
uncommented in `demos/data_flow/` so the demos start in the documented
state next time. (`demos/` is never part of a plain `pytest` run, so it
can't affect the baseline either way.) Delete any `.coverage` data file
the runs left behind.

## Extending this for the *next* lecture

1. Add new app code under `app/<some_subpackage>/`, the same way this
   lecture added `app/billing/charges.py`. Only create a new top-level
   `app/` subpackage if the feature doesn't fit under
   billing/pricing/reports/payments/accounts/notifications/orders.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
3. Put deliberately incomplete or buggy illustrations (like
   `demos/data_flow/`) under `demos/<short_topic_name>/`, where a plain
   `pytest` won't pick them up (`testpaths = tests` in `pytest.ini`).
4. Copy this file as a starting template for the next lecture's guide.
   Coverage-based testing (Week 7) can start from the two real gaps the
   whole-suite coverage report still shows (`order_service.py`,
   `password_reset.py`; see the Week 5 guide).
