# Demo Guide — Equivalence Partitioning, Boundary-Value Analysis, and Negative Testing

Companion to the Week 3 reading (*Equivalence Partitioning, Boundary-Value
Analysis, and Negative Testing*). No slide-deck source for this lecture
was available when this guide was written, so section headings below
follow the reading's own structure rather than slide titles — adjust the
mapping if the slide deck ends up organized differently.

**Before class:** confirm the baseline is green (aside from the known,
intentional non-passes — see below):

```bash
pip install -r requirements.txt
pytest -v
```

You should see **33 passed, 2 xfailed, 1 failed**:
- `XFAIL` — `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged — see "Negative Testing
  Exposes What EP Alone Misses" below).
- `XFAIL` — `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (this lecture's new boundary bug — see "Putting It Together" below).
- `FAIL` — `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (the same Lecture 1 bug, documented the unittest way instead of via
  xfail; kept for the "Revisited" contrast, same as in Week 2).

If anything else fails, something was left mid-edit from a previous
session.

---

## Learning Objectives

No code — orientation only.

## Why We Need Systematic Test-Case Design

No new file. Bridge from Lecture 1's Principle 2 ("exhaustive testing is
impossible") verbally, then pose the reading's framing question: *if we
can't test everything, which inputs do we test?*

## Equivalence Partitioning — The Basic Idea / Valid and Invalid Classes

No code yet — work the `is_valid_username(username)` example on the
board or a slide, exactly as in the reading (recall from the *pytest*
reading's Exercise 1; it is not part of this codebase). Three classes:
length < 3, 3–20, > 20.

## Multiple Parameters

No code — verbal only. Use the "3 classes × 3 classes = 9 combinations"
arithmetic from the reading to motivate why teams test classes
individually rather than combinatorially by default.

## Boundary-Value Analysis — Why Boundaries Matter / The Technique

No new file — work the abstract 3–20 length example from the reading
(boundary at 3 tested with 2/3/4, boundary at 20 tested with 19/20/21).

## A Boundary Bug in `calculate_late_fee()`

**File:** `app/billing/late_fees.py`

This is the same function from Weeks 1–2, unmodified. Open it and point
at `if fee > max_fee`. Ask: "what's the exact input where this flips?"
Then demonstrate in a REPL, live:

```bash
python3
>>> from app.billing.late_fees import calculate_late_fee
>>> calculate_late_fee(days_late=25/1.50)   # fee == 25.0 exactly
25.0
```

The boundary happens to be handled correctly here (`>` is strict, so
`fee == max_fee` falls through to `return fee`). Use this to make the
point that BVA is about *checking* the boundary, not assuming it's
broken — contrast with the `determine_shipping_cost` boundary later in
this lecture, where the equivalent check reveals a real bug.

## The Zune 30GB Freeze Case Study

No code — discussion. Walk the `while days > 365` / `if days > 366`
mismatch from the reading and ask students to spot the boundary gap
(`days == 366`) before you point it out.

## Negative Testing — Positive vs. Negative / What Counts as Invalid Input

No new file — introduce the five categories from the reading
(out-of-range, wrong type, missing/empty, malformed, extreme/adversarial)
verbally.

## Negative Testing Exposes What EP Alone Misses

**File:** `app/billing/late_fees.py`, `tests/billing/test_late_fees.py`

```bash
python3
>>> from app.billing.late_fees import calculate_late_fee
>>> calculate_late_fee(-4)
-6.0
```

Then run the suite and point at the `XFAIL` line:

```bash
pytest tests/billing/test_late_fees.py -v
```

Connect it explicitly to the KNOWN BUG docstring in `late_fees.py`: no
equivalence class was ever defined for negative `days_late`, because the
original requirement never mentioned it — exactly the gap negative
testing is meant to close.

## The Year 2000 Problem (Y2K) Case Study

No code — discussion. Frame it as "an unexamined equivalence class at
civilization scale," per the reading.

## Putting It Together: `determine_shipping_cost()`

**File:** `app/pricing/shipping.py`, `tests/pricing/test_shipping.py`

This is the lecture's centerpiece worked example — walk all four steps
from the reading against the real files:

1. **Step 1 — Equivalence classes.** Open `shipping.py`, read the
   docstring's specification aloud, and map it to the reading's EC1–EC5
   table.
2. **Step 2 — Boundary values.** Point at the four boundaries (0, 1, 5,
   20). Ask students to predict the expected cost at each `at boundary`
   value *before* running anything — then focus on 5.0 specifically:
   per the spec it's EC2 ($10.00), but `elif weight_kg < 5` is strict.
3. **Step 3 — Negative test cases.** Show the `None` case in a REPL:
   ```bash
   python3
   >>> from app.pricing.shipping import determine_shipping_cost
   >>> determine_shipping_cost(None)
   ```
   Point out the raw `TypeError` leaking a Python internals message
   instead of a clear, documented error — a real (if minor) defect only
   a deliberate type-negative test would catch.
4. **Step 4 — Run the suite.**
   ```bash
   pytest tests/pricing/test_shipping.py -v
   ```
   Point at the `XFAIL` on `test_valid_weights[5.0-10.0]` and connect it
   back to the KNOWN BUG note in `shipping.py`. This bug is intentionally
   **not** fixed here — like the Lecture 1 late-fee bug, it stays
   formally tracked via `xfail` rather than silently patched, so a
   future lecture can revisit it.

## How Much Is Enough?

No code — discussion, tying back to Principle 6 ("testing is
context-dependent") from Lecture 1.

## Common Pitfalls / A Practical Mental Model / Summary

No code — recap using the reading's tables and the three mental-model
prompts (partition it / find the flip / ask for garbage).

## Practice Exercises / Discussion Questions

Assign as take-home or in-class pen-and-paper work. Exercises 1–3
(`classify_bmi`) and Exercise 4 (`parse_percentage`) are intentionally
**not** implemented in this codebase — they're meant to be worked out on
paper first. If a future lecture wants a live-coding version of either,
add it under `app/` following the same pattern as `shipping.py`.

## Key Takeaways for SE 413/513

No code — close with the seven takeaways from the reading.

---

## After class

Confirm `pytest -v` from the project root is back to the expected
**33 passed, 2 xfailed, 1 failed** baseline (no live-edit steps this
lecture, so nothing should need reverting).

## Extending this for the *next* lecture (TDD and Test Doubles)

1. If the next lecture needs a new function to drive test-first, add it
   under `app/<some_subpackage>/`, the same way this lecture added
   `shipping.py` under `app/pricing/`. Only create a new top-level
   `app/` subpackage if the new feature genuinely doesn't fit under
   billing/pricing/reports/payments/accounts.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
3. If the lecture needs a dedicated, isolated illustration, add it under
   `demos/<short_topic_name>/` and keep it out of `tests/` so a plain
   `pytest` doesn't pick it up (`testpaths = tests` in `pytest.ini`).
4. Copy this file as a starting template for the new lecture's guide —
   same shape, new section names and file paths.
