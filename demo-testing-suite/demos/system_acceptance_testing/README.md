# Week 11 demo: system testing and acceptance testing

A self-contained mini-project for the two Week 11 readings, *System
Testing: Testing the Whole System from the Outside* and *Acceptance
Testing: Building the Right Thing*. It is Week 10's shop
(`../integration_testing/`), grown into a system that runs on its own:
a health check, a product catalog, coupon codes, a database that
survives restarts, and a `serve.py` that the tests start as a separate
process. Every listing and output in the readings comes from running
these files with pytest 9.1, pytest-bdd 9.0, Flask 3.1, and requests
2.34.

Week 10's folder is unchanged: its reading quotes it line by line.

**Run every command from this folder**, not from `demo-testing-suite/`:

```bash
cd demos/system_acceptance_testing
pip install -r ../../requirements.txt     # adds pytest-bdd this week
```

```
                      ┌──────────────────── the system under test ─────────────────────┐
 test process         │                                                                 │
 (requests) ──HTTP──► │ serve.py: api.py ─► OrderService ─► OrderRepository ─► shop.db  │
     │                │                          │                                      │
     │                │                          └──► PaymentClient ──HTTP──┐           │
     │                └─────────────────────────────────────────────────────┼───────────┘
     └──── /_test/config, /_test/charges (test environment only) ──────► fake PayFast
```

| File | What it is |
|---|---|
| `specs/system_requirements.md` | SYS-1..9, NFR-1..3: the **system test basis** |
| `specs/system_test_plan.md` | Scope, environment, approach, entry/exit criteria, traceability, risks, findings |
| `specs/user_stories.md` | US-1..3 and their acceptance criteria: the **acceptance test basis** |
| `specs/shop_api.md` | The API contract, v1.1 |
| `specs/payment_provider_api.md` | PayFast's contract (unchanged from Week 10) |
| `specs/f1_week10_validation.patch` | Puts back Week 10's input validation, to reproduce finding F1 |
| `serve.py` | Runs the shop as one system; prints `READY shop=... provider=...` |
| `variants.py` | Picks correct or defective components from environment variables |
| `shop/pricing.py` | Coupons (US-3) |
| `shop/pricing_per_unit.py` | **Defective:** FLAT5 read as "$5 off each unit" |
| `shop/service_racy.py` | **Defective:** charges first, takes the stock after, from a stale read |
| `fakes/payment_provider.py` | Week 10's fake PayFast, plus test-only `/_test/` controls |

| Test folder | Level | How the shop runs | Tests |
|---|---|---|---|
| `tests/unit/` | unit (the developer's `price_order` tests) | not at all | 8 |
| `tests/integration/` | integration (Week 10's harness, carried over) | assembled inside the test process | 13 |
| `tests/system/` | system | **separate process**, HTTP only | 23 |
| `tests/acceptance/` | acceptance (Gherkin, pytest-bdd) | **separate process**, HTTP only | 14 |

A plain `pytest` in this folder reports **58 passed**, in about ten
seconds: each system and acceptance test starts its own server.
`pytest -m system` and `pytest -m acceptance` select one level.

## The demos, in the readings' order

```bash
pytest tests/unit tests/integration -q        # 21 passed: the levels below
pytest tests/system -v                        # 23 passed
pytest tests/acceptance -v                    # 14 passed
```

### Each defect is found at exactly one level

```bash
SHOP_SERVICE=racy pytest tests/unit tests/integration   # 21 passed
SHOP_SERVICE=racy pytest tests/system                   # 1 failed: the race for the last five mugs
SHOP_SERVICE=racy pytest tests/acceptance               # 14 passed

SHOP_COUPONS=per_unit pytest tests/unit tests/integration  # 21 passed
SHOP_COUPONS=per_unit pytest tests/system                  # 23 passed
SHOP_COUPONS=per_unit pytest tests/acceptance              # 2 failed: 2 mugs with FLAT5; 4 stickers with FLAT5
```

| | unit | integration | system | acceptance |
|---|---|---|---|---|
| `SHOP_SERVICE=racy` | pass | pass | **1 failed** | pass |
| `SHOP_COUPONS=per_unit` | pass | pass | pass | **2 failed** |

### Finding F1: hostile input crashed the Week 10 shop (System Testing reading)

```bash
patch -p1 < specs/f1_week10_validation.patch      # back to Week 10's validation
pytest tests/system/test_robustness_and_security.py   # 2 failed: an HTML 500 page
patch -R -p1 < specs/f1_week10_validation.patch   # and fixed again
```

## Trying the system by hand

```bash
python serve.py                    # shop on :8000, fake PayFast on :8001
```

In a second terminal:

```bash
curl -s http://127.0.0.1:8000/health                                        # no key needed
curl -s http://127.0.0.1:8000/products -H 'X-API-Key: shop-key'
curl -i -X POST http://127.0.0.1:8000/orders -H 'X-API-Key: shop-key' \
     -H 'Content-Type: application/json' \
     -d '{"sku": "MUG", "quantity": 2, "customer_email": "ana@example.com", "coupon": "FLAT5"}'
curl -s -X POST http://127.0.0.1:8001/_test/config -d '{"mode": "decline"}' \
     -H 'Content-Type: application/json'                                    # misbehave
curl -s http://127.0.0.1:8001/_test/charges                                 # what was charged
```

`python serve.py --db shop.db` keeps the database between runs (stop
with Ctrl-C, start again: the stock is where you left it). Delete
`shop.db` afterwards.

## Before you leave

```bash
git status .                       # nothing modified; no shop.db, no .orig/.rej files
```
