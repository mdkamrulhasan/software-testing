# Demo Guide — Test-Driven Development, Mocking, and Dependency Isolation

Companion to the Week 4 reading (*Test-Driven Development, Mocking, and
Dependency Isolation*). Copied from
`docs/DEMO_GUIDE_week03_ep_bva_negative_testing.md`'s template, same
shape, following the reading's own section order.

**Before class:** confirm the baseline is green (aside from the known,
intentional non-passes carried over from Weeks 1 and 3 — see below):

```bash
pip install -r requirements.txt
pytest -v
```

You should see **43 passed, 2 xfailed, 1 failed**:
- `XFAIL` — `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged).
- `XFAIL` — `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (Lecture 3's boundary bug, unchanged).
- `FAIL` — `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (same Lecture 1 bug, documented the unittest way; unchanged).

None of this lecture's new tests are involved in any of the three — this
week is purely additive. If anything else fails, something was left
mid-edit from a previous session.

---

## Learning Objectives

No code — orientation only.

## What Is Test-Driven Development? / The Red-Green-Refactor Cycle

**File:** `tests/practice/tdd_password_demo.py`

This file is the in-class live-coding script for the reading's
`is_strong_password()` worked example. It is *not* named `test_*.py` on
purpose — pytest's default collection pattern skips it, so it can sit in
this half-finished state (only Cycle 1's RED test and fake
implementation are active; Cycles 2–4 and the refactor are commented
out) without breaking `pytest -v`.

Walk it live, uncommenting one cycle at a time:
1. Run just this file to show Cycle 1 RED → GREEN:
   ```bash
   pytest tests/practice/tdd_password_demo.py -v
   ```
2. Uncomment Cycle 2's test, run again, watch it fail against
   `return False`. Uncomment Cycle 2's implementation, watch it pass.
3. Repeat for Cycles 3 and 4.
4. Uncomment the refactor. Re-run all four tests to confirm nothing
   broke.

Connect explicitly to the "fake it till you make it" Key Idea box and
the Equivalence Partitioning tie-in Tip box in the reading — each cycle
here corresponds to one equivalence class from Week 3's vocabulary.

## Why TDD Forces Testable Design

No new file — discussion only, using the reading's own framing
("hard to unit test is usually a design problem").

## Dependency Isolation and Seams

**File:** `app/notifications/password_reset.py`

This is the lecture's centerpiece worked example, transcribed directly
from the reading's `PasswordResetService` / `smtplib` walkthrough. Open
it and point at the docstring: the reading's "before" version (a
hard-coded `smtplib.SMTP(...)` call inside the method) is described
there but deliberately **not** reproduced as runnable code — only the
"after" version, with `email_client` injected through the constructor,
actually exists in this file. Ask students to say out loud why the
"before" version would be painful to unit test before showing the
"after" version's seam.

Point at `EmailClient`: an interface with no real behavior, whose only
job is to give `create_autospec` something to constrain a mock to later
in the lecture (see Common Pitfalls, below).

## The Test Double Taxonomy

**File:** `tests/notifications/test_password_reset_service.py`

Walk the five doubles in the file's own order — it mirrors the
reading's section order exactly:

1. **Dummy** — `DummyLogger`, poisoned so any accidental use raises
   immediately. Point out that `send_reset_email()` never calls
   `logger` at all, so a *correct* test never triggers it.
2. **Stub** — `StubEmailClient`. Emphasize what the test does *not* do:
   no assertion is made about `send()` being called.
3. **Fake** — `FakeEmailClient`. This is **state verification**: the
   test inspects `email_client.sent_emails` after the fact.
4. **Spy** — `SpyEmailClient`. Note in the reading's own words how close
   this is to the fake — the difference is intent, not mechanics.
5. **Mock** — a bare `MagicMock()`, verified with
   `assert_called_once_with(...)`. This is **behavior verification**:
   the assertion is against the mock itself, not any resulting state.

```bash
pytest tests/notifications/test_password_reset_service.py -v
```

All seven tests in this file pass — there is no deliberate bug to find
this lecture (Weeks 1 and 3 already carry the running ones). The
teaching payload here is in reading the five doubles side by side, not
in a failure.

## Mocking `UserRepository` Instead of a Real Database

**Files:** `app/accounts/registration_service.py`,
`tests/accounts/test_registration_service.py`

Callback to Week 2: open `app/accounts/user_repository.py` and reread
its docstring aloud — "*A mocking lecture can mock UserRepository
instead of sqlite3 itself.*" That sentence was written two lectures ago,
specifically for today. `UserRegistrationService` is the first caller of
`UserRepository` that actually needs isolating.

```bash
pytest tests/accounts/test_registration_service.py -v
```

Point out that this test file never touches sqlite3 at all —
`create_autospec(UserRepository, instance=True)` replaces the whole
dependency, contrasted with `tests/accounts/test_user_repository.py`,
which still exercises a real `:memory:` connection because *that* file
is testing `UserRepository` itself, not one of its callers.

## State Verification vs. Behavior Verification / Classical vs. Mockist Schools

No new file — discussion, using `test_reset_email_is_recorded_by_the_fake`
(state) and `test_email_client_called_with_correct_message` (behavior)
from the notifications test file as the two concrete anchors. Ask: which
school does each test above belong to?

## Common Pitfalls

**Files:** the last two tests in
`tests/notifications/test_password_reset_service.py`, and the last test
in `tests/accounts/test_registration_service.py`

Live-demo "mocks that lie":
```bash
pytest tests/notifications/test_password_reset_service.py::test_bare_mock_lets_a_typoed_method_through_silently -v
pytest tests/notifications/test_password_reset_service.py::test_autospec_mock_catches_the_same_typo -v
```
The first test *passes* precisely because a bare `MagicMock()` accepts
any attribute name, typo included — that is the pitfall, not a test
failure. The second test shows `create_autospec(EmailClient, ...)`
catching the identical typo with an `AttributeError`. The accounts test
file repeats the same point against `UserRepository`, tying it back to
the mocking-a-real-dependency example above.

## A Practical Mental Model / Summary

No code — recap using the reading's four mental-model prompts and the
dummy/stub/fake/spy/mock summary table.

## Practice Exercises / Discussion Questions

Assign as take-home or in-class work. Exercise 2 (`SessionManager` /
`time.time()`) is intentionally **not** implemented in this codebase —
it is meant to be worked out on paper first, the same way Week 3 left
`classify_bmi` and `parse_percentage` as paper exercises. If a future
lecture wants a live-coding version, add it under `app/` following the
same pattern as `password_reset.py`.

## Key Takeaways for SE 413/513

No code — close with the seven takeaways from the reading.

---

## After class

Confirm `pytest -v` from the project root is back to the expected
**43 passed, 2 xfailed, 1 failed** baseline. If Cycles 2–4 of
`tdd_password_demo.py` were uncommented live during class, they are not
collected by a plain `pytest` run regardless (the file isn't named
`test_*.py`), so there is nothing to revert there — but consider
re-commenting them anyway so the file is ready to demo fresh next time.

## Extending this for the *next* lecture

1. If the next lecture needs a new function or class to build test-first
   or to isolate with a double, add it under `app/<some_subpackage>/`,
   the same way this lecture added `app/notifications/password_reset.py`
   and `app/accounts/registration_service.py`. Only create a new
   top-level `app/` subpackage if the new feature genuinely doesn't fit
   under billing/pricing/reports/payments/accounts/notifications.
2. Add its tests under the mirroring `tests/<some_subpackage>/` path.
3. If the lecture needs a dedicated, isolated illustration, add it under
   `demos/<short_topic_name>/` and keep it out of `tests/` so a plain
   `pytest` doesn't pick it up (`testpaths = tests` in `pytest.ini`).
4. Copy this file as a starting template for the new lecture's guide —
   same shape, new section names and file paths.
