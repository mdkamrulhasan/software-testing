# Demo Guide — Functional Testing

Companion to the Week 8 reading, *Functional Testing: Designing Tests
from the Specification*, and its slides
(`lectures/F26/8.1_Functional_Testing.pdf`). Copied from
`docs/DEMO_GUIDE_week07_coverage_based_testing.md`'s template, same
shape, following the reading's section order. The slides' seven LIVE
DEMO and five TRY IT boxes are marked where they fall.

**Before class:** reinstall requirements (this week adds `hypothesis`
and `allpairspy`) and confirm the baseline (aside from the known,
intentional non-passes carried over from Weeks 1 and 3; see below):

```bash
pip install -r requirements.txt
pytest -v
```

You should still see **72 passed, 2 xfailed, 1 failed**. Week 8 adds
nothing to the main suite (`app/` has no rule tables or state machines
to apply this week's techniques to), so this is exactly Week 7's
baseline:
- `XFAIL`: `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged).
- `XFAIL`: `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (Lecture 3's boundary bug, unchanged).
- `FAIL`: `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (same Lecture 1 bug, documented the unittest way; unchanged).

The whole lecture runs inside the demo mini-project. **Its commands
must be run from that folder**, so the reading's `from shop... import`
lines and `tests/...` paths work as printed:

```bash
cd demos/functional_testing
```

`demos/functional_testing/README.md` lists every command in order, if
you want a cheat sheet open next to the slides. Clear Hypothesis's
example database before the property-based demo, so the class sees it
search from scratch: `rm -rf .hypothesis`.

---

## Where We Are / What Is Functional Testing?

No code. Bridge from Week 7's last slide: the four things coverage
cannot see (weak assertions, short-circuited sub-conditions, boundary
values, missing features) are all questions about the specification.
The one point to land before any demo is the oracle pitfall: run
`shipping_fee(20.0, True, True)`, see `10.0`, paste it into a test, and
that test can never fail there.

## From Requirements to Test Cases

No new file. Put REQ-1..8 on screen and leave them there; every test
name today points back at one of them. The traceability matrix is
literally the test IDs you will see in the `-v` output below.

## Recap: EP and BVA  *(LIVE DEMO 1)*

**Files:** `shop/shipping.py`, `tests/test_shipping_bva.py`

```bash
pytest tests/test_shipping_bva.py -v           # 2 passed
```

This is the test Week 7's 100%-coverage suite lacked. Close the loop
with the mutant from Week 7's Limitation 3:

```bash
sed -i.bak 's/amount >= 50/amount > 50/' shop/shipping.py
pytest tests/test_shipping_bva.py              # FAILED [50.0-0.0]: assert 7.99 == 0.0
mv shop/shipping.py.bak shop/shipping.py
```

Last week the same edit left 9 tests passing at 100% coverage.

## Decision Table Testing  *(LIVE DEMOS 2–3, TRY IT 1–2)*

**Files:** `shop/shipping.py`, `shop/shipping_buggy.py`,
`tests/test_shipping_dt.py`

Build the full 8-column table on the board before showing the
collapsed one. Ask the class to fill in column 5 (member, standard,
$50+): REQ-2 and REQ-3 both say free, so they agree. Then the
"what if REQ-2 said $2.99" question.

**LIVE DEMO 2, one test per rule:**

```bash
pytest tests/test_shipping_dt.py -v            # 5 passed, IDs R1..R5
```

Point at the IDs in the report: that is the traceability tip.

**LIVE DEMO 3, break the priority.** Change the import in
`tests/test_shipping_dt.py` to `from shop.shipping_buggy import
shipping_fee`, then:

```bash
pytest tests/test_shipping_dt.py               # FAILED ...[R1-member-express]; 1 failed, 4 passed
```

> **Slide 39 says `1 failed, 6 passed`.** That count came from a file
> that also held the two boundary tests. Here they live in
> `tests/test_shipping_bva.py`, so the decision-table file has 5 tests
> and the output matches the reading (`1 failed, 4 passed`).

**TRY IT 1 (students, 4 min).** Leave the import on the buggy version.
Students add `pytest.param(80.0, False, True, 15.0,
id="R2-guest-express-80")` and predict first. *Answer:* it fails on the
buggy version (a guest's $80 express order is free, `0.0 != 15.0`) and
passes on the correct one. That is the "don't care is not don't test"
box. Switch the import back, and remove the extra case if you want the
file to match the reading again.

**TRY IT 2 (students, 5 min), = Exercise 1(a–b).** Course
registration. *Answer:* three conditions (prerequisites met, seats
available, account hold), 8 columns, collapsing to **4 rules**:

| | R1 | R2 | R3 | R4 |
|---|---|---|---|---|
| Prerequisites met? | T | T | T | F |
| Section has seats? | T | F | — | — |
| Account hold? | F | F | T | — |
| Action | register | waitlist | reject | reject |
| Full-table columns | 1 | 1 | 2 | 4 |

## State Transition Testing  *(LIVE DEMO 4, TRY IT 3)*

**Files:** `shop/order.py`, `tests/test_order.py`

Draw the diagram, then build the 5 × 4 state table with the class and
count the red cells before running anything: 20 pairs, 5 valid, 15
invalid. The key-idea box is the point: once the table exists, the
tests are mechanical.

```bash
pytest tests/test_order.py -v                  # 22 passed
```

Show `order_in()`: every state is reached through `pay()` / `ship()` /
`deliver()` / `cancel()`, never `o.state = ...`. Then the last line of
`test_invalid_transitions_rejected`: REQ-7 has two halves (rejected
*and* unchanged), and the test asserts both.

**TRY IT 3 (students, 5 min), = Exercise 3.** Adding `return_item`
(DELIVERED → RETURNED, refunds). *Answer:* 6 states × 5 events = **30
pairs**, 6 valid, **24 invalid**. To keep all-transitions coverage:
add `"RETURNED": ["pay", "ship", "deliver", "return_item"]` to
`order_in`, add `"return_item"` to `EVENTS` and `"RETURNED"` to the
state list, add the new valid case, and add a refund check for the
return. That gives 6 + 24 + 3 = **33 tests**. The 24 invalid pairs are
the original 15, plus `return_item` from the four states other than
DELIVERED, plus all five events from the new RETURNED state.

## Combinatorial and Pairwise Testing  *(LIVE DEMO 5, TRY IT 4)*

**Files:** `pairwise.py`, `tests/test_checkout_pairwise.py`

Work 3 × 3 × 2 × 3 = 54 on the board, and 216 with a fourth 4-valued
option. Then:

```bash
python pairwise.py                             # 10 rows; pairs needed: 45  covered: 45  tests: 10
pytest tests/test_checkout_pairwise.py -v      # 10 skipped
```

The 10 rows are exactly the reading's table, in the same order
(allpairspy 2.5.1). The pytest file is the reading's `parametrize`
listing. Its body in the reading is `...`, which would let all ten rows
*pass* without checking anything, so here each row is skipped with the
reason "no oracle yet". Use it to make the fourth limitation concrete:
pairwise picks combinations, not expected results.

Then the NIST case study: most failures need one or two parameters,
none in that study needed more than six.

**TRY IT 4 (students, 4 min), = Exercise 4.** *Answers* (allpairspy
2.5.1):
- Exhaustive with `currency`: 3 × 3 × 2 × 3 × 4 = **216**.
- Pairwise, no filter: **16** rows, all 89 pairs covered.
- With the slide's `ok` filter: **11** rows, and no row pairs
  `gift_card` with a non-USD currency.

**"Done early?" on that slide has a surprising answer.** Run the
coverage check on the filtered set and it is **not** complete: of the
86 valid pairs (89 minus the three gift_card/non-USD ones), the 11
rows cover only **71**. The 15 missing ones are mostly currency pairs,
for example `coupon=SAVE10` with `EUR`, `customer=guest` with `EUR`,
`delivery=express` with `CAD`, and `payment=card` with `GBP`.
allpairspy builds rows greedily, and its filter can leave pairs it never
returns to. This is worth a minute: a generator's output is a claim to
check, the same way "100% coverage" was last week. Fixes: append rows
for the missing pairs by hand, or use a constraint-aware generator
(NIST ACTS, Microsoft PICT).

## Property-Based Testing with Hypothesis  *(LIVE DEMOS 6–7, TRY IT 5)*

**Files:** `shop/split.py` (buggy first version), `shop/split_fixed.py`,
`tests/test_split_pbt.py`

Show `split.py` and let the class confirm the two example tests in
their heads (`30.0 / 3`, `100.0 / 4`). Then:

**LIVE DEMO 6, find the bug:**

```bash
rm -rf .hypothesis
pytest tests/test_split_pbt.py
```

The `E` lines match the reading exactly: `assert 0.02 == 0.01`, then
`Failing test case: test_shares_add_up_to_total(total_cents=1,
people=2)`. Three fresh runs all shrank to that same example. Ask what
the raw failing input probably looked like before shrinking.

**LIVE DEMO 7, fix and re-run.** Change the import in
`tests/test_split_pbt.py` to `from shop.split_fixed import split_bill`:

```bash
pytest tests/test_split_pbt.py                 # 1 passed
python -c "from shop.split_fixed import split_bill; print(split_bill(0.01, 2), split_bill(100, 3))"
# [0.01, 0.0] [33.34, 33.33, 33.33]
```

Switch the import back afterwards. Optional: before switching to the
fix, re-run the buggy version *without* deleting `.hypothesis/`. It
fails again with the same example, because the saved failure is
replayed first.

Then the pitfall box: `assert split_bill(t, n) == [round(t/n, 2)] * n`
passes against the buggy version and can never fail.

**TRY IT 5 (students, 5 min), = Exercise 5.** Properties for Week 7's
`apply_coupon`. Students create `test_coupon_props.py` in
`demos/coverage_reports/` and import `from checkout_app.checkout import
apply_coupon`. *Answer,* with the slide's strategies:
- `apply_coupon(amount, code) >= 0` **passes**: SAVE10 multiplies by
  0.9 and FLAT5 floors at 0.
- `apply_coupon(amount, code) <= amount` **fails**, always with
  `code='NONE'`, at amounts such as `1.375` (→ `1.38`). The exact amount
  differs between runs (we saw 1.375, 1.1875 and 1.078125). *Why:*
  `apply_coupon` rounds to cents, and the strategy produces amounts
  with fractions of a cent, which can round **up**. Restrict the input
  to whole cents (`st.integers(...)` divided by 100) and the property
  passes. Use this for discussion: is the defect in the code, or in a
  property stated more strongly than the specification?

## Choosing a Technique / Functional Testing and Coverage Together

No new code. Optional, to show the "where vs. what" point:

```bash
pytest tests/test_shipping_dt.py tests/test_shipping_bva.py --cov=shop --cov-branch --cov-report=term-missing
```

7 passed; `shop/shipping.py` reaches 100%. `order.py`, `split.py` and
`split_fixed.py` show 0%: that is REQ-5..8, which this run never
tested. (`shipping_buggy.py` is also at 0%, because nothing imports it
unless you switch the import.) Coverage shows *where* to look; the specification says what
the right answer is.

## Common Mistakes / Mental Model / Summary / Key Takeaways

No new code. Each mistake points at something already run today:
- Code as the oracle → the opening pitfall.
- Untested don't-cares → TRY IT 1.
- Happy-path state tests → the 15 invalid pairs.
- Setting state directly → `order_in()`.
- Pairwise as exhaustive → the 71 of 86 filtered result.
- Properties that restate code → the `split_bill` pitfall box.

## Practice Exercises / Discussion Questions

Intentionally **not** implemented in the repository, the same way
Weeks 3–7 left their exercises. The answers for Exercises 1, 3, 4 and 5
are under the matching TRY IT above. Exercise 2 is open-ended. One
plausible bug: the code checks the hold only when the section is full,
so a student with a hold registers whenever seats are open. A single R3
test that sets "seats" to F passes; R3 with seats T catches it, which is
the same "test the don't-care both ways" lesson as TRY IT 1.

---

## After class

From `demos/functional_testing/`, confirm both switched imports are
back (`tests/test_shipping_dt.py` imports `shop.shipping`,
`tests/test_split_pbt.py` imports `shop.split`), that `git status .` is
clean with no `.bak` left, then `rm -rf .hypothesis`. If students
created `test_coupon_props.py` in `demos/coverage_reports/`, delete it.
From the project root, confirm `pytest -v` is still at **72 passed, 2
xfailed, 1 failed**.

## Extending this for the *next* lecture

1. Add new app code under `app/<some_subpackage>/`. Only create a new
   top-level `app/` subpackage if the feature doesn't fit under
   billing/pricing/reports/payments/accounts/notifications/orders.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path,
   and check `pytest --cov=app --cov-branch
   --cov-report=term-missing:skip-covered` still lists nothing.
3. Put deliberately incomplete or buggy illustrations under
   `demos/<short_topic_name>/`, where a plain `pytest` won't pick them
   up (`testpaths = tests` in `pytest.ini`). If, like
   `functional_testing/`, its imports or paths must match a reading
   exactly, make it a self-contained folder run from inside.
4. Copy this file as a starting template for the next lecture's guide.
