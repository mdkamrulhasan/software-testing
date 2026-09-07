# Demo Guide — pytest: Assertions, Fixtures, and Test Organization

Companion to `w02_unittestingpytestfixtures.tex`. Use this alongside the
slides: switch to presenter view for the `\note{...}` talking points; use
this document for exactly which file to have open and which command to
run, in sync with each slide.

**Before class:** `cd` into the project root and confirm the baseline is
green:

```bash
pip install -r requirements.txt
pytest -v
```

You should see everything pass except one `XFAIL`
(`test_calculate_late_fee[-4-0.0]`). If anything else fails, something
was left mid-edit from a previous run — check "The Payoff: Assertion
Rewriting" row below, the one slide that asks you to temporarily break a
file.

Have two terminal tabs open: one at the project root for the main
suite, one you'll `cd` into `demos/<folder>` for the three isolated
examples (they're excluded from a plain `pytest` run on purpose — see
`pytest.ini`).

---

## About This Lecture / Learning Objectives

No code — orientation only. Don't open an editor yet.

## The Chain in Code / A Unit Test, Revisited (Last Week)

**File:** `app/billing/late_fees.py`, `tests/legacy/test_late_fees_unittest.py`

Open `late_fees.py` first and let students find the missing validation
themselves before you point at the `KNOWN BUG` docstring note. Then run:

```bash
pytest tests/legacy/test_late_fees_unittest.py -v
```

You'll see one `PASS` and one `FAIL` in the same file — this is the
"revisited" unittest-style test from Lecture 1, unmodified. Don't fix
the bug here; the fix is intentionally deferred (see the docstring).

## Why Not Just unittest? / Test Discovery and Running Tests

**No new file yet** — this is where you introduce pytest itself and run
the discovery commands from a clean terminal at the project root:

```bash
pytest                        # discover and run everything under tests/
pytest -v                     # same, listing each test by name
pytest tests/billing           # just one subpackage
pytest -k "discount"          # only tests matching a name
```

Point out that `tests/legacy/...` (unittest-style) and everything else
(pytest-style) both got discovered and run — no special-casing needed.

## A Test Is Just a Function

**File:** `tests/pricing/test_discounts.py` → `test_ten_percent_discount`
**App code:** `app/pricing/discounts.py`

Open both side by side. Point out: no base class, no special name beyond
`test_*`, just a function and one `assert`.

## The Payoff: Assertion Rewriting

**File:** `app/pricing/discounts.py` — this is the one live-edit moment
in the whole lecture.

1. Open `app/pricing/discounts.py`. Find the two `return` lines at the
   bottom of `calculate_discounted_price`.
2. Comment out the correct line, uncomment the buggy one (the comment
   above it is labeled `DEMO ONLY`).
3. Run:
   ```bash
   pytest tests/pricing/test_discounts.py::test_ten_percent_discount -v
   ```
4. Read the failure output aloud: the actual value, the expected value,
   and the `where` line showing which call produced it.
5. **Revert immediately** — swap the two lines back — before moving on.
   Every other test in the project assumes the correct version.

## Comparing Floating-Point Numbers

**File:** `tests/pricing/test_discounts.py` → `test_float_addition`

Show `0.1 + 0.2 == 0.3` failing in a plain Python REPL first (`python3`,
type it, watch it print `False`), then show the fixture file's
`pytest.approx` version passing.

## Testing for Exceptions: pytest.raises()

**File:** `tests/pricing/test_discounts.py` → `test_invalid_discount_raises_value_error`
**App code:** `app/pricing/discounts.py` — point at the `raise ValueError` line.

## Arrange–Act–Assert (AAA)

No new file — map the diagram onto the `pytest.raises` test you just
ran: (nothing to arrange, literals) / (the call) / (`pytest.raises`
around it).

## The Problem Fixtures Solve

No code — motivate the next section verbally before opening a file.

## Defining and Using a Fixture / Fixtures as Dependency Injection

**File:** `tests/pricing/conftest.py` (the `sample_cart` fixture) and
`tests/pricing/test_cart.py` (`test_cart_total`)
**App code:** `app/pricing/cart.py`

Open `conftest.py` and `test_cart.py` side by side — this is the moment
to say explicitly "notice `test_cart.py` never imports `sample_cart`;
that's not an accident, that's the mechanism." Walk the
request → resolve → inject arrows from the diagram against these two
real files.

```bash
pytest tests/pricing/test_cart.py::test_cart_total -v
```

## Fixtures Can Depend on Other Fixtures

**File:** `tests/pricing/conftest.py` (`empty_cart`, `cart_with_one_item`)
and `tests/pricing/test_cart.py` (`test_single_item_total`)

## Some Things Need Cleanup / yield Fixtures / The yield Fixture Timeline

**File:** `tests/accounts/conftest.py` (`db_connection`) and
`tests/accounts/test_user_repository.py` (`test_insert_and_query_user_raw_sql`)

```bash
pytest tests/accounts/test_user_repository.py -v
```

For the timeline slide, make the point concrete: temporarily add
`assert False` at the top of `test_insert_and_query_user_raw_sql`, rerun,
and show the connection still closes cleanly (no `ResourceWarning`, no
leaked connection) even though the test failed. Revert the `assert
False` afterward.

## Common Pitfall: return Has No Teardown

No new file — say it, point back at `db_connection`'s `yield` line, ask
"what would we lose if that were a `return`?"

## Why Scope Matters / The Four Scopes / Visualizing Scope Lifetime

**File:** `demos/module_scope_db/conftest.py` and
`demos/module_scope_db/test_user_repository_module_scope.py`

```bash
cd demos/module_scope_db
pytest -v
cd ../..
```

Contrast this fixture (`scope="module"`) against
`tests/accounts/conftest.py`'s default (`scope="function"`) — same
shape, one keyword argument different. Point out how
`test_insert_bob_alongside_alice` has to account for Alice's leftover
row; that extra care is the real cost of a wider scope.

## Common Pitfall: Wide Scope + Mutable State = Flaky Tests

**File:** `demos/scope_pitfall/` (both files)

```bash
cd demos/scope_pitfall
pytest -v
```

`test_second_order_sees_only_its_own_order` fails — walk through why
using the file's own module docstring. Then, live, open `conftest.py`,
change `scope="session"` to `scope="function"`, rerun, and show both
tests pass:

```bash
pytest -v
cd ../..
```

This is the day's best "aha" moment — budget the full 2 minutes the
timing comment allows, don't rush it.

## tmp_path: A Safe Temporary Directory

**File:** `tests/reports/test_report_writer.py`
**App code:** `app/reports/report_writer.py`

```bash
pytest tests/reports/test_report_writer.py -v
```

Worth mentioning: no `@pytest.fixture` for `tmp_path` anywhere in this
project — it ships with pytest itself, same as `monkeypatch` next.

## monkeypatch: Safely Patching Things

**File:** `tests/payments/test_api_client.py`
**App code:** `app/payments/api_client.py`

```bash
pytest tests/payments/test_api_client.py -v
```

If time allows, show in a REPL that `PAYMENT_API_KEY` is NOT set in the
real environment before/after the test run — the whole point is that
`monkeypatch` cleans up after itself automatically.

## The Problem: One Test Per Case Doesn't Scale

**File:** `tests/billing/test_late_fees.py` → `test_typical_fee_naive`,
`test_fee_is_capped_naive`

## @pytest.mark.parametrize / Documenting Known Bugs with xfail

**File:** `tests/billing/test_late_fees.py` → `test_calculate_late_fee`

```bash
pytest tests/billing/test_late_fees.py -v
```

Point at the `XFAIL` line in the output and connect it back to the
Lecture 1 bug in `app/billing/late_fees.py` — same fault, now formally
tracked instead of silently broken or silently ignored.

## Parametrize as a Testing-Technique Vehicle

No new file — verbal bridge to the EP/BVA teaser at the end of lecture.

## Sharing Fixtures Across Files: conftest.py

**File:** `tests/pricing/conftest.py` again — you already used it for
the fixtures section; now name what it is explicitly (a file pytest
auto-discovers, no import required) before moving to the hierarchy
example.

## conftest.py Hierarchy

**File:** `demos/conftest_hierarchy/` (all four files)

Open a file tree of this folder (or run `find demos/conftest_hierarchy
-type f`) side by side with the slide's diagram — same shape, real
files.

```bash
cd demos/conftest_hierarchy
pytest -v
cd ../..
```

Live-demo the asymmetry: temporarily add a test to
`tests/test_cart.py` that requests `discounted_cart`, rerun, and show
pytest's "fixture 'discounted_cart' not found" error. Remove the test
afterward.

## Beyond Today: Organizing a Growing Suite

**File:** the whole `tests/` tree (mirrors `app/`'s layout — point this
out explicitly) and `pytest.ini`'s `markers =` section.

```bash
pytest --markers
```

Shows `unit` and `slow` registered, ready to use as
`@pytest.mark.slow` / `pytest -m "not slow"` once the suite has slow
tests worth excluding.

## Recap / Key Takeaways / One Last Question / Questions?

No new code — the discussion prompt ("a teammate proposes making every
fixture session-scoped for speed") maps directly onto
`demos/scope_pitfall/`; you can reopen it here if the discussion runs
long and a concrete example helps someone.

---

## After class

Confirm you reverted the one live-edit step (`app/pricing/discounts.py`)
and that `pytest -v` from the project root is back to green (plus the
one expected `XFAIL`) before the next session.
