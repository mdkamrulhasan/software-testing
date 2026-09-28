# Demo Guide — Mock vs. MagicMock, and Control-Flow Graphs & Coverage

Companion to the two Week 5 readings: *Mock vs. MagicMock in Python*
and *Control-Flow Graphs and Statement, Branch, and Path Coverage*.
Copied from `docs/DEMO_GUIDE_week04_tdd_test_doubles.md`'s template,
same shape, following each reading's own section order (mocking first,
since it closes out Week 4's test-doubles unit).

**Before class:** install the new `pytest-cov` dependency and confirm
the baseline is green (aside from the known, intentional non-passes
carried over from Weeks 1 and 3; see below):

```bash
pip install -r requirements.txt      # now includes pytest-cov
pytest -v
```

You should see **65 passed, 2 xfailed, 1 failed**:
- `XFAIL`: `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged).
- `XFAIL`: `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (Lecture 3's boundary bug, unchanged, and reused below).
- `FAIL`: `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (same Lecture 1 bug, documented the unittest way; unchanged).

None of this week's twenty new tests are involved in any of the three.
This week is purely additive.

---

# Part 1: Mock vs. MagicMock

## What Is a Mock? / What Is MagicMock?

No new file. Recap Week 4: every double in
`tests/accounts/test_registration_service.py` and
`tests/orders/test_order_service.py` is used only through **ordinary
method calls** (`repository.insert_user(...)`,
`payment_service.process_payment(100)`), so `Mock` /
`create_autospec` was always enough. This week's examples are the
first ones where it isn't.

**Files:** `app/accounts/user_lookup.py`,
`tests/accounts/test_user_lookup.py`

Open `app/accounts/user_lookup.py`. Every function in it uses its
dependency through a magic method: `len()`, `[0]`, `in`, `for`, or
`with`. Ask the class to name the dunder behind each one before
showing the reading's table.

## Mock and MagicMock: The Core Difference

Start with the failure. It's more memorable than the fix:
```bash
pytest tests/accounts/test_user_lookup.py::test_plain_mock_raises_type_error_on_len -v
pytest tests/accounts/test_user_lookup.py::test_plain_mock_works_once_the_magic_method_is_attached_by_hand -v
```
The first shows a plain `Mock` raising `TypeError` at `len()`. The
second is the reading's table footnote: attach `__len__` by hand and
a plain `Mock` works. `MagicMock` just does that for every magic
method up front.

## Worked Examples 2–6

```bash
pytest tests/accounts/test_user_lookup.py -v
```

Walk the tests in file order. They follow the reading's examples:

1. **Example 2 (len and indexing):** `test_process_users_returns_the_first_user`,
   then `test_process_users_never_indexes_an_empty_repository` for the
   tip box (magic methods support `assert_not_called()` too).
2. **Example 3 (`in`):** `test_check_permission_mixes_mock_and_magicmock`.
   Point at the two constructors on adjacent lines: `user` is a
   `Mock`, `user.permissions` is a `MagicMock`. The choice is made
   **per object, not per test** (Discussion Question 5).
3. **Example 4 (iteration)**, including the pitfall box:
   ```bash
   pytest tests/accounts/test_user_lookup.py -k "twice or second_time" -v
   ```
   `test_iter_return_value_is_silently_empty_the_second_time` **passes**,
   and that is the pitfall: configuring `iter([...])` makes the second
   loop quietly see nothing. Same "a passing test can be the problem"
   framing as Week 4's "mocks that lie".
4. **Example 5 (context managers):** `test_read_file_uses_the_object_returned_by_enter`.
   Read `file.__enter__.return_value.read.return_value` left to right
   aloud, as the reading's tip box does.
5. **Example 6 (database connection):** `test_get_user_name_queries_through_the_cursor`.
   This is the answer to Discussion Question 4: map each link of
   `connection.cursor.return_value.__enter__.return_value` onto a line of
   `get_user_name()`.

Example 1 (ordinary method calls) has no new file. Week 4's
registration and order tests already are that example.

## A Useful Decision Rule / Why Not Always Use MagicMock? / Common Student Mistakes

No code. Discussion, using `test_check_permission_mixes_mock_and_magicmock`
as the concrete anchor for "choose the simplest double that accurately
represents the interface."

## Practice Exercises / Discussion Questions

Exercises 1–4 (`products`, `load_config`, `notify`) are intentionally
**not** implemented. Work them on paper first, the same way Weeks 3
and 4 left their exercises. Exercise 4's `notify` is a good
cold-call: `user_service` is only used through ordinary calls, so
`Mock`; the `user["email"]` indexing happens on the *returned* value,
not on `user_service` (Discussion Question 2).

---

# Part 2: Control-Flow Graphs and Coverage

## From Black-Box to White-Box Testing

No code. Bridge from Week 3's EP/BVA; Part 2 closes by reusing
Week 3's shipping bug.

## Control-Flow Graphs

**File:** `app/payments/transactions.py`

`classify_transaction()` and `contains_negative()` are the reading's
two CFG examples, verbatim. Draw `classify_transaction()`'s graph on
the board from the code (three diamonds, four return blocks) before
showing the reading's figure. Then point at `contains_negative()`'s
`for` loop as the source of a **back edge**.

## Statement Coverage

**File:** `tests/payments/test_transactions.py`

The four `classify_transaction` cases are parametrized in the same
order the reading adds them, so you can replay its 5/7 ≈ 71%
calculation live by selecting the first two:
```bash
pytest "tests/payments/test_transactions.py::test_classify_transaction_every_path[amount<0]" \
       "tests/payments/test_transactions.py::test_classify_transaction_every_path[intl-under-1000]" \
       --cov=app.payments.transactions --cov-report=term-missing
```
The tool counts statements for the whole module (including the `def`
lines and `contains_negative()`), so it reports 54%, not 5/7. But the
**Missing** column shows lines `24, 28`, exactly the two returns the
reading says are unexecuted (`"flagged"` and `"domestic"`). The
`32-35` range is `contains_negative()`, which this selection doesn't
touch.

## The Limitation of Statement Coverage / the "goto fail" case study

**Files:** `demos/coverage_gaps/handshake.py`,
`demos/coverage_gaps/test_handshake.py`

A Python analogue of CVE-2014-1266: a copy-pasted `if hash_ok:` lost
its `not`, so it always returns `True` before the params and signature
checks can run.
```bash
pytest demos/coverage_gaps/test_handshake.py \
    --cov=handshake --cov-report=term-missing
```
Both tests pass; the report shows lines 30–34 (every check after the
bug) as never executed. Then add the missing negative test from the
file's docstring and watch it fail.

Worth saying aloud, since students will try it: if the bug were a bare
`return True`, coverage.py would report **100%**. Statically dead code
after an unconditional `return` is dropped by the compiler and not
counted as a statement at all. `handshake.py`'s docstring explains
why the demo bug is conditional instead.

## Branch (Decision) Coverage / Measuring Coverage in Practice

**Files:** `demos/coverage_gaps/myapp.py`,
`demos/coverage_gaps/test_myapp.py`

`myapp.py` is a four-line copy of `apply_membership_discount()` with no
docstring, so its line numbers match the reading exactly. Run it
twice, with and without branch measurement:
```bash
pytest demos/coverage_gaps/test_myapp.py --cov=myapp --cov-report=term-missing
pytest demos/coverage_gaps/test_myapp.py --cov=myapp --cov-branch --cov-report=term-missing
```
The first says **100%**. The second reproduces the reading's report:
**83%**, `2->4` missing. That is the reading's "`--cov-branch` matters"
tip box, live. The fully covered version of this function (both
branches) is `app/pricing/membership.py` +
`tests/pricing/test_membership.py`, part of the main suite.

## Path Coverage / Cyclomatic Complexity and Basis Path Testing

**File:** `tests/payments/test_transactions.py`

```bash
pytest tests/payments/test_transactions.py -v \
    --cov=app.payments.transactions --cov-branch --cov-report=term-missing
```
The test ids name the paths. `classify_transaction`: four ids, one per
path, V(G) = 4. `contains_negative`: the three basis paths for V(G) = 3
(`zero-iterations`, `one-iteration-early-return`,
`one-iteration-loop-exits`) plus a "many" case, the reading's
zero/one/many mental model. The report is 100% branch coverage, yet
the loop still has unboundedly many untested paths.

## What Coverage Cannot Tell You

**No new file.** Reuse Week 3:
```bash
pytest tests/pricing/test_shipping.py --cov=app.pricing.shipping --cov-branch --cov-report=term-missing
```
The report is **100% branch coverage**, and in the same output
`test_valid_weights[5.0-10.0]` is still `XFAIL`. That is the reading's
Section 9 argument in a single command: coverage cannot see the
boundary value that exposes the `< 5` bug; only BVA did.

## Common Pitfalls: coverage on our own suite

Close Part 2 by pointing the tool at the whole codebase:
```bash
pytest --cov=app --cov-branch --cov-report=term-missing
```
Every Week 5 module is at 100%, but two Week 4 files are not. Ask the
class to explain each before you do:
- `app/orders/order_service.py`: **80%, line 37 missing.** A real gap:
  no test ever drives `place_order()` down its `"Payment failed"`
  branch (`PaymentStub` always returns `True`). Left in place on
  purpose as an exercise: have students write the stub-returning-`False`
  test and watch the report go to 100%.
- `app/notifications/password_reset.py`: **63%, `SmtpEmailClient`
  missing.** A deliberate gap. The class's own docstring says it is
  never exercised, because testing it needs a real mail server, which
  is the reason the seam exists. This is the "coverage is a diagnostic,
  not a target" pitfall: 100% here would mean a worse test suite, not a
  better one.

## A Practical Mental Model / Summary

No code. Recap using the four mental-model prompts.

## Practice Exercises / Discussion Questions

`grade_letter()` (Exercises 1–3) and the first-index search (Exercise
4) are intentionally **not** implemented. Work them on paper, then have
students verify their hand-computed coverage by writing the function
and tests themselves and running `--cov-branch`.

## Key Takeaways for SE 413/513

No code. Close with both readings' takeaway lists.

---

## After class

Confirm `pytest -v` from the project root is back to the expected
**65 passed, 2 xfailed, 1 failed** baseline. If the negative test was
added to `demos/coverage_gaps/test_handshake.py` live, remove it again
so the demo starts green next time. (`demos/` is never part of a plain
`pytest` run, so it can't affect the baseline either way.) Delete any
`.coverage` data file the runs left behind.

## Extending this for the *next* lecture

1. Add new app code under `app/<some_subpackage>/`, the same way this
   lecture added `app/accounts/user_lookup.py`,
   `app/payments/transactions.py`, and `app/pricing/membership.py`.
   Only create a new top-level `app/` subpackage if the feature doesn't
   fit under billing/pricing/reports/payments/accounts/notifications/orders.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
3. Put deliberately incomplete or buggy illustrations (like
   `demos/coverage_gaps/`) under `demos/<short_topic_name>/`, where a
   plain `pytest` won't pick them up (`testpaths = tests` in
   `pytest.ini`).
4. Copy this file as a starting template for the next lecture's guide.
   Data-flow testing (Week 6) is a natural fit for another
   `app/payments/` or `app/billing/` function.
