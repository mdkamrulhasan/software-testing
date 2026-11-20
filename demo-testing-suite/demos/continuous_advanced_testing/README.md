# Weeks 13–14 demo: continuous testing, contract testing, AI-assisted testing

A self-contained mini-project for two readings, *Continuous Testing:
Every Change, Every Time* (Week 13) and *Advanced Testing, Emerging
Techniques, and AI-Assisted Testing* (Week 14). It is Week 11's shop
(`../system_acceptance_testing/`), now with:

- a **pipeline** (`pipeline.py`) that runs every test level in order,
  cheapest first, on your machine and in GitHub Actions
  (`.github/workflows/shop-pipeline.yml` at the repository root);
- a **consumer-driven contract** between the shop and PayFast
  (`contracts/`, `tests/contract/`);
- two **deliberately flaky tests** and a rerun tool (`flaky_examples/`,
  `tools/rerun.py`);
- two **AI-generated test suites**, their prompts, and an evaluator
  (`ai_generated/`).

Every listing and output in the readings comes from running these files
with Python 3.13, pytest 9.1, pytest-xdist 3.8, pytest-cov 7.1 (coverage
7.17), pytest-bdd 9.0, Flask 3.1, and requests 2.34. Week 11's folder is
unchanged: its readings quote it line by line.

**Run every command from this folder**, not from `demo-testing-suite/`:

```bash
cd demos/continuous_advanced_testing
pip install -r ../../requirements.txt
```

A plain `pytest` here reports **67 passed** (Week 11's 60, plus 7
contract tests). The flaky examples and the AI-generated suites are not
collected by default (their file names do not start with `test_`); run
them by path.

## What is new since Week 11

| File | What it is |
|---|---|
| `pipeline.py` | The pipeline: `static`, `unit`, `integration` (with an 80% coverage gate), `contract`, `system`, `acceptance`. Stops at the first failing stage. |
| `.coveragerc` | Coverage of `shop/` only, without the defective variants; also measures the shop inside the server processes the system tests start. |
| `contracts/shop-payfast.json` | What the shop sends PayFast and what it uses from PayFast's answers |
| `tests/contract/` | Both sides of the contract: `test_shop_consumer.py` (does the shop keep it?) and `test_payfast_provider.py` (does PayFast keep it?) |
| `fakes/payfast_sandbox_next.py` | A stand-in for PayFast's real sandbox after its next release: a charge's `id` is now `charge_id` |
| `shop/payments_no_idempotency.py` | **Defective:** a refactoring dropped the `Idempotency-Key` header |
| `flaky_examples/` | Two tests that are flaky on purpose: a timing assumption, and an order dependency |
| `tools/rerun.py` | Runs the same tests N times and counts the outcomes |
| `ai_generated/` | Two suites an AI assistant wrote for the shop's API (from the code, and from the specs), the script that rebuilds their prompts, and `evaluate.py`, which scores any suite |
| `shop/payments.py` | One-line fix for pylint's E0606, found by the pipeline's first run (below) |

`serve.py` gained `--payfast sandbox-next`; `variants.py` gained
`SHOP_PAYMENTS=no_idempotency`.

## Week 13: the pipeline

```bash
python pipeline.py --list
python pipeline.py                       # every stage, about 12 seconds
python pipeline.py unit integration      # just these
```

| Stage | Command (abridged) | Catches |
|---|---|---|
| static | `pylint --errors-only shop fakes ...` | code that would crash when run |
| unit | `pytest tests/unit --cov` | |
| integration | `pytest tests/integration --cov --cov-append --cov-fail-under=80` | the components disagreeing; too little coverage |
| contract | `pytest tests/contract` | the shop and PayFast disagreeing |
| system | `pytest -m system -n auto` | the race (`SHOP_SERVICE=racy`) |
| acceptance | `pytest -m acceptance -n auto` | the coupon misreading (`SHOP_COUPONS=per_unit`) |

Each defect stops the pipeline at the first stage that can see it:

```bash
SHOP_SERVICE=racy python pipeline.py               # FAILED at system (22/23)
SHOP_COUPONS=per_unit python pipeline.py           # FAILED at acceptance (14/16)
SHOP_PAYMENTS=no_idempotency python pipeline.py    # FAILED at contract
```

In GitHub, the same stages run on every push and pull request that
touches this folder: a **fast** job (static to contract, on Python 3.12
and 3.13) and, only if both pass, a **slow** job (system and
acceptance). After the workflow reaches the default branch, *Actions →
Shop pipeline → Run workflow* can run it against one of the defects.

### The first pipeline run failed (for a real reason)

```text
************* Module shop.payments
shop/payments.py:43:37: E0606: Possibly using variable 'problem' before assignment
```

With `retries=-1`, `PaymentClient.charge()` raised `UnboundLocalError`
instead of `PaymentUnavailable`: Week 6's use-before-definition anomaly,
in the shop since Week 10, found by the first automated static check.
Fixed in this folder only.

### Parallel tests, and flaky ones

```bash
pytest -m system                    # 23 passed, about 5.5 s
pytest -m system -n auto            # 23 passed, about 3.9 s (2 CPUs)

python tools/rerun.py 20 flaky_examples/flaky_timing.py                    # e.g. 18/20 passed: FLAKY
python tools/rerun.py 10 flaky_examples/flaky_timing.py tests/system -n 2  # e.g. 5/10 passed under load
pytest flaky_examples/flaky_order.py                                       # 2 passed
pytest flaky_examples/flaky_order.py -k look_the_order_up                  # 1 failed: 404
pytest flaky_examples/flaky_order.py -n 2                                  # 1 failed: 404
```

## Week 14: contract testing

```bash
pytest tests/contract -v                                              # 7 passed

# The shop breaks the contract; every other test still passes
SHOP_PAYMENTS=no_idempotency pytest                                   # 3 failed, 64 passed
#   E  'request 1: header Idempotency-Key: missing'

# PayFast breaks the contract; every other test still passes (they use our fake)
PAYFAST=sandbox-next pytest tests/contract/test_payfast_provider.py   # 1 failed
#   E  ['response body.id: missing']
```

What PayFast's change would have done in production (second terminal):

```bash
python serve.py --payfast sandbox-next
curl -s -X POST localhost:8000/orders -H 'X-API-Key: shop-key' -H 'Content-Type: application/json' \
     -d '{"sku": "MUG", "quantity": 2, "customer_email": "ana@example.com"}'   # {"error":"internal error"}
curl -s localhost:8001/_test/charges                                         # ...but the customer was charged
curl -s localhost:8000/orders/1 -H 'X-API-Key: shop-key'                     # and the order is stuck "pending"
```

## Week 14: AI-generated tests

```bash
python ai_generated/build_prompt.py from_code      # the exact prompt behind suite_from_code.py
python ai_generated/build_prompt.py from_spec      # ... and behind suite_from_spec.py

pytest ai_generated/suite_from_code.py             # 2 failed, 39 passed  <- on the CORRECT shop
SHOP_COUPONS=per_unit pytest ai_generated/suite_from_code.py   # 41 passed <- on the buggy one
pytest ai_generated/suite_from_spec.py             # 46 passed
SHOP_COUPONS=per_unit pytest ai_generated/suite_from_spec.py   # 3 failed

python ai_generated/evaluate.py ai_generated/suite_from_code.py ai_generated/suite_from_spec.py
python ai_generated/evaluate.py tests              # the human-written suite, for comparison (about 3 min)
```

| Suite | Tests | Pass on the correct shop | Branch coverage | Known defects caught (of 3) | Mutants killed (of 14) |
|---|---|---|---|---|---|
| `tests/unit` | 8 | 8 | 18% | 0 | 2 |
| `tests/integration` | 13 | 13 | 80% | 0 | 5 |
| `tests/contract` | 7 | 7 | 21% | 1 (no Idempotency-Key) | 2 |
| `tests/system` | 23 | 23 | 85% | 1 (racy) | 7 |
| `tests/acceptance` | 16 | 16 | 82% | 1 (per_unit) | 4 |
| **all of `tests/`** | 67 | 67 | 92% | **3** | 11 |
| AI, from the code | 41 | **39** | 94% | **0** | 10 |
| AI, from the specs | 46 | 46 | 94% | 1 (per_unit) | 12 |

Paste either prompt into any assistant, save its answer in this folder
as a `.py` file, and score it the same way.

## Before you leave

```bash
git status .            # nothing modified; no shop.db, no .coverage; reports/ is ignored
```
