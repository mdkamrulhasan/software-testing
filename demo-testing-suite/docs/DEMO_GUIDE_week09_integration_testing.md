# Demo Guide — Integration Testing

Companion to the Week 9 reading, *Integration Testing: Testing How
Components Work Together*
(`reading_materials/w09_integration_testing.pdf`). Copied from
`docs/DEMO_GUIDE_week08_functional_testing.md`'s template, same shape,
following the reading's section order. There is no slide deck this
week; the reading's figures and tables carry the lecture.

**Before class:** reinstall requirements (this week adds `flask`,
`requests`, and `responses`) and confirm the baseline:

```bash
pip install -r requirements.txt
pytest -v
```

You should see **75 passed, 3 xfailed, 1 failed**. That is Week 8's
72 / 2 / 1 plus `tests/integration/` (three passes and one new strict
`xfail`):
- `XFAIL`: `tests/billing/test_late_fees.py::test_calculate_late_fee[-4-0.0]`
  (Lecture 1's negative-days bug, unchanged).
- `XFAIL`: `tests/pricing/test_shipping.py::test_valid_weights[5.0-10.0]`
  (Lecture 3's boundary bug, unchanged).
- `FAIL`: `tests/legacy/test_late_fees_unittest.py::TestLateFee::test_negative_days_should_not_be_negative_fee`
  (same Lecture 1 bug, documented the unittest way; unchanged).
- `XFAIL` (strict, **new**): `tests/integration/test_registration.py::test_failed_welcome_email_does_not_leave_a_half_registered_user`
  (a real defect integration testing found; see "Back in the Main
  Suite" below).

`pytest -m "not integration"` reproduces Week 8's 72 / 2 / 1 exactly.

Most of the lecture runs inside the demo mini-project. **Its commands
must be run from that folder**:

```bash
cd demos/integration_testing
pytest                      # 46 passed, in about a second
```

`demos/integration_testing/README.md` lists every command in order, with
its expected result, if you want a cheat sheet open next to the reading.
The broken components are switched in with environment variables that
last for one command only (`SHOP_PAYMENTS=v1 pytest ...`), so there is
nothing to switch back afterwards.

**Live HTTP:** `python serve.py` starts the whole shop on port 8000 and
the fake provider on 8001 (`--port` to change). Start it in a second
terminal before Section 7 if you want to use `curl`.

---

## Where We Are / What Is Integration Testing?

**Files:** `tests/test_order_service_unit.py`, `tests/variants.py`

Open with the unit tests. They are good Week 4 tests: autospec'd mocks,
behavior verification. Run them three times:

```bash
pytest tests/test_order_service_unit.py                       # 3 passed
SHOP_PAYMENTS=v1   pytest tests/test_order_service_unit.py    # 3 passed
SHOP_SERVICE=buggy pytest tests/test_order_service_unit.py    # 3 passed
```

Then tell the class there are two real defects in the code they just
saw pass. Don't say where yet. Ask what a mock *cannot* have. (A wire
format, transactions, constraints.) That is the reading's Section 3.1
in one demo.

The Mars Climate Orbiter box has no code. Point out that a *Software
Interface Specification* existed, so the units were written down; what
was missing was a check of the connection against it. That is the theme
of Section 6.

## Integration Strategies

**File:** `tests/test_api.py`

Big-bang, live:

```bash
SHOP_PAYMENTS=v1 pytest tests/test_api.py --tb=line          # assert 502 == 201
```

Ask the room to name every place the fault could be (all six
integration points are candidates). Keep the answer for Section 10,
where the incremental tests point straight at IP6.

Then put the reading's Figure 1 up and walk the strategy table. The
demo's own test files are the sandwich: bottom-up from
`test_repository.py` / `test_payments_*.py`, top-down from
`test_api_topdown.py`, meeting at `test_order_service.py`. The README's
"Test file" table maps each one.

## The Running Example

**Files:** `specs/shop_api.md`, `specs/payment_provider_api.md`, Figure 2

Draw Figure 2 on the board and number the arrows with the class before
showing the integration-point table. Emphasize the last column
("where the agreement is written down"), and ask which arrow would have
nothing in it if `errors.py` did not exist. (IP2 and IP5: the
exceptions *are* the contract.)

## Design and API Reviews

**File:** `specs/design_review.md`

This is the section to slow down on. Run a mini-review live: hand out
(or project) `payment_provider_api.md` and ask the class to apply the
checklist for five minutes. Students reliably find R1 (cents), R5 (HTML
5xx), and R6 (idempotency), and usually R7 (no timeout) if prompted with
"operational notes". Then reveal `design_review.md`. Every finding has a
test named in the last column. Pick R4 and walk the "From Review to
Test" box in the reading: integration point, scenario, oracle, test.

## API Integration Testing

**Files:** `tests/test_api_topdown.py`, `tests/test_api.py`, `serve.py`

With `python serve.py` running in another terminal, do the reading's
`curl` exchanges (the README has them): 201 with `Location`, then drop
the API key (401), send `"quantity": "2"` (400), order `TEE` (409).
Restart with `--provider-mode unavailable` for the 503 with
`Retry-After`.

Then the top-down tests:

```bash
pytest tests/test_api_topdown.py -v                           # 14 passed
```

The parametrized ids (`unknown-sku`, `out-of-stock`, `declined`,
`provider-down`, `our-bug`) read as the status table. Point at
`stub.calls == []`: the stub records calls, so a test can prove invalid
input never reached the service. Optional live break: in `shop/api.py`,
delete the `@app.errorhandler(404)` line and rerun
`test_unknown_route_answers_in_json_not_html` (Flask's HTML 404 comes
back). Restore it afterwards.

Authentication: `test_wrong_provider_key_is_502_not_503` in
`test_api.py`. Ask why 503 would be the wrong answer. (It invites
retries that can never succeed.)

## Database Integration Testing

**Files:** `tests/test_repository.py`, `shop/db.py`, `tests/conftest.py`
(`connection`, `stock`), `tests/test_order_service.py`

```bash
pytest tests/test_repository.py -v                            # 8 passed
```

Two moments worth doing live:

1. **R10.** Remove the `PRAGMA foreign_keys` line and rerun:
   ```bash
   sed -i.bak '/PRAGMA foreign_keys/d' shop/db.py
   pytest tests/test_repository.py                            # 1 failed
   mv shop/db.py.bak shop/db.py
   ```
   A review finding, made permanent by a test.
2. **The transaction bug.**
   ```bash
   SHOP_SERVICE=buggy pytest tests/test_order_service.py --tb=short   # assert 3 == 5
   SHOP_SERVICE=buggy pytest tests/test_api.py                        # 5 passed (!)
   ```
   The second line is the reading's "end-to-end tests do not catch it
   either" box. The API's validation blocks the trigger, so only the
   service-level integration test sees the leak.

Explain why the `stock` fixture opens a *new* connection. Without it, a
test would read its own uncommitted writes and miss exactly this class of
bug. `test_uncommitted_changes_are_invisible_to_other_connections` shows
the mechanism.

### Back in the Main Suite: Registration

**Files:** `tests/integration/` (from the project root),
`app/accounts/user_repository.py`

```bash
cd ../..
pytest -m integration -rx                                     # 3 passed, 1 xfailed
pytest -m "not integration"                                   # 72 passed, 2 xfailed, 1 failed
```

Two findings to tell the class about, both real:
- The `users` schema had only ever existed in a test fixture
  (`tests/accounts/conftest.py`). Writing integration tests forced a
  production `create_schema()` into `app/`.
- The strict `xfail`. If the mail server is down, `register()` has
  already committed the user, so the user is never welcomed and cannot
  retry. Read the `reason=` aloud. Exercise 4 asks students to fix it.
  Don't fix it in class; like the Week 1 and Week 3 bugs, it stays
  documented.

## Service Integration Testing

**Files:** `shop/payments.py`, `fakes/payment_provider.py`,
`tests/conftest.py` (`provider`), `tests/test_payments_live.py`,
`tests/test_order_service.py`

Back in `demos/integration_testing/`. Walk `charge()` and match each
line to a finding (timeout R7, retry, `Idempotency-Key` R6, never
parsing a 5xx body R5, 400/401 not retried R8). Then:

```bash
pytest tests/test_payments_live.py -v                         # 6 passed
pytest tests/test_order_service.py -v                         # 5 passed
```

Point out `make_server("127.0.0.1", 0, ...)`: port 0 means "any free
port", which is why these tests can run in parallel. The
`test_slow_provider_times_out` warning box is a good discussion opener:
the fake really does charge the card *after* the client gave up. Ask
what a production system should do. (Reconcile by `Idempotency-Key`;
the review records it as an open item.)

## Test Doubles in Integration Testing

**File:** `tests/test_payments_stubbed.py`

The payoff for the big-bang question from Section 4:

```bash
SHOP_PAYMENTS=v1 pytest tests/test_payments_stubbed.py -v     # 1 failed, 4 passed
SHOP_PAYMENTS=v1 pytest tests/test_payments_live.py --tb=line # 3 failed: 400 ... cents
```

Make sure the class notices **which** test passed: the loose stub. The
contract check names the field and both values:
`{'amount': '12.50'} != {'amount': 1250}`. Then the fake provider says
the same thing in PayFast's words. Compare with `assert 502 == 201`.

Contract testing (Pact) has no code here. Say that
`test_request_matches_the_provider_contract` is the consumer half of a
contract, written by hand.

## Integration Test Automation

**Files:** `pytest.ini` (the new `integration` marker),
`tests/integration/test_registration.py` (`pytestmark`)

Show the marker and the two `-m` runs above if you skipped them. The
GitHub Actions YAML in the reading is a sketch only; it is not committed
(pipelines are the Continuous Testing week). Close on the pyramid: 14
top-down tests cost almost nothing; only 5 tests assemble everything;
the whole demo runs in about a second.

## Common Integration Failures / Hands-On Walkthrough

No new code. The failure table's middle column is a list of things
already run today. The refunds walkthrough (Section 13) is Exercise 3.
If time allows, do Step 2 (the review) together and leave Steps 3–5 as
homework.

## Best Practices / Common Mistakes

No new code. Each mistake points at something already run today:
- Passing unit tests ≠ working system → the three runs of
  `test_order_service_unit.py`.
- Testing everything end-to-end → `assert 502 == 201`, and the buggy
  service passing `test_api.py`.
- Doubles from your own assumptions → the loose stub.
- Checking only the response → the `stock` fixture's second connection.
- Real external services in tests → the fake provider.
- Shared databases and fixed ports → `tmp_path` and port 0.

## Practice Exercises / Discussion Questions

Intentionally **not** implemented in the repository, the same way
Weeks 3–8 left their exercises. Hints:
- Exercise 3 (refunds): IT-R4 needs the fake to fail once and then
  succeed. Easiest is a counter in `create_provider()`, or a
  `responses` registry with a 503 followed by a 201, as in
  `test_retry_after_an_html_503_reuses_the_idempotency_key`.
- Exercise 4: removing the `xfail` marker is part of the answer.
  `strict=True` makes the test *fail* as soon as the fix lands
  ("XPASS(strict)"), which is the reminder to remove it.
- Exercise 5: today `charge()` raises `KeyError: 'id'`, a raw
  implementation error leaking across the interface. That matches the
  Week 3 negative-testing pattern in `pricing/shipping.py`.

---

## After class

From `demos/integration_testing/`: `git status .` should be clean, with
no `shop/db.py.bak`, and `shop/api.py` unchanged if you did the 404
break. Stop any `serve.py` still running (Ctrl-C). From the project
root, confirm `pytest -v` is still at **75 passed, 3 xfailed, 1 failed**.

## Extending this for the *next* lecture

1. Add new app code under `app/<some_subpackage>/`. Only create a new
   top-level `app/` subpackage if the feature doesn't fit under
   billing/pricing/reports/payments/accounts/notifications/orders.
2. Unit tests go under the mirroring `tests/<some_subpackage>/` path;
   tests that assemble several real components go under
   `tests/integration/` with `pytestmark = pytest.mark.integration`.
   Check `pytest --cov=app --cov-branch
   --cov-report=term-missing:skip-covered` still lists nothing.
3. Put deliberately incomplete or buggy illustrations under
   `demos/<short_topic_name>/`, where a plain `pytest` won't pick them
   up (`testpaths = tests` in `pytest.ini`). If a demo needs broken
   variants, consider `integration_testing/`'s environment-variable
   switch (`tests/variants.py`) instead of editing imports live.
4. Week 10 (System Testing) can start from `demos/integration_testing/`
   and `serve.py`: the shop already runs as a whole system over HTTP.
5. Copy this file as a starting template for the next lecture's guide.
