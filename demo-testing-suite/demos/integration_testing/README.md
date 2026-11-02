# Week 10 demo: integration testing

A self-contained mini-project for the Week 10 reading, *Integration
Testing: Testing How Components Work Together*. It is a small shop
backend with six integration points, a third-party payment provider
(faked, but over real HTTP), and two deliberately broken components.
Every listing and output in the reading comes from running these files
with pytest 9.1, Flask 3.1, requests 2.34, and responses 0.26. The
reading (`reading_materials/w10_integration_testing.pdf`) prints the
key listings and summarizes the rest; the full code is all here.

**Run every command from this folder**, not from `demo-testing-suite/`:

```bash
cd demos/integration_testing
```

```
 HTTP client ──IP1──► api.py ──IP2──► OrderService ──IP3──► OrderRepository ──IP4──► SQLite
  (curl, tests)       (Flask)            │
                                         └──IP5──► PaymentClient ──IP6 (HTTP)──► PayFast
                                                                                 (third party)
```

| File | What it is |
|---|---|
| `specs/shop_api.md` | The shop's API contract (IP1) |
| `specs/payment_provider_api.md` | PayFast's published API (IP6): amounts in **integer cents** |
| `specs/design_review.md` | The design/API review: checklist, findings R1–R11, and the test each became |
| `shop/db.py`, `shop/repository.py` | Schema and all SQL (IP3, IP4) |
| `shop/payments.py` | The PayFast client: timeout, retry, `Idempotency-Key` (IP5, IP6) |
| `shop/payments_v1.py` | **Broken:** the same client, still sending v1's `"12.50"` dollars |
| `shop/service.py` | `OrderService`: one transaction for stock + order, compensation if the charge fails |
| `shop/service_buggy.py` | **Broken:** stock and order committed in two transactions |
| `shop/api.py` | The Flask API: validation, auth, error-to-status mapping (IP1, IP2) |
| `fakes/payment_provider.py` | A fake PayFast that enforces the provider's contract |
| `serve.py` | Runs the whole shop locally, for `curl` |
| `tests/variants.py` | Picks correct or broken components from environment variables |

| Test file | Integrates | Strategy step |
|---|---|---|
| `tests/test_order_service_unit.py` | nothing: every collaborator mocked | the unit-test baseline |
| `tests/test_repository.py` | repository + real SQLite (IP4) | bottom-up 1: the test is the **driver** |
| `tests/test_payments_stubbed.py` | client + `responses` stub (IP6) | stub at the HTTP layer |
| `tests/test_payments_live.py` | client + fake PayFast over HTTP (IP6) | real protocol, fake provider |
| `tests/test_order_service.py` | service + DB + fake PayFast (IP3, IP5) | bottom-up 2 |
| `tests/test_api_topdown.py` | real API + **stub** service (IP1, IP2) | top-down 1: lower layers stubbed |
| `tests/test_api.py` | everything (IP1–IP6) | the assembled system |

A plain `pytest` in this folder reports **46 passed**.

## The demos, in the reading's order

```bash
pytest tests/test_order_service_unit.py -v          # Section 3.1: 3 passed
pytest tests/test_repository.py -v                  # Section 8: 8 passed
pytest tests/test_api_topdown.py -v                 # Section 7.3: 14 passed
pytest tests/test_payments_stubbed.py tests/test_payments_live.py -v   # Sections 9-10: 11 passed
pytest tests/test_order_service.py tests/test_api.py -v                # Sections 7.4, 8.5, 9.3: 10 passed
```

### The incorrect-data-format defect (R1; Sections 4.1 and 10.1)

```bash
SHOP_PAYMENTS=v1 pytest tests/test_order_service_unit.py   # 3 passed: mocks can't see it
SHOP_PAYMENTS=v1 pytest tests/test_payments_stubbed.py     # 1 failed: {'amount': '12.50'} != {'amount': 1250}
                                                           #   (the *loose* stub test still passes)
SHOP_PAYMENTS=v1 pytest tests/test_payments_live.py        # 3 failed: 400 amount must be a positive integer number of cents
SHOP_PAYMENTS=v1 pytest tests/test_api.py                  # 2 failed: assert 502 == 201 -- *where* is the fault?
```

### The database-inconsistency defect (R3; Section 8.5)

```bash
SHOP_SERVICE=buggy pytest tests/test_order_service_unit.py # 3 passed: mocks have no transactions
SHOP_SERVICE=buggy pytest tests/test_order_service.py      # 1 failed: assert 3 == 5 (stock leaked)
SHOP_SERVICE=buggy pytest tests/test_api.py                # 5 passed: the API's validation hides it
```

### Removing a line the design review flagged (R10; Section 8.4)

```bash
sed -i.bak '/PRAGMA foreign_keys/d' shop/db.py
pytest tests/test_repository.py                     # 1 failed: unknown product accepted
mv shop/db.py.bak shop/db.py
```

## Trying the API by hand

```bash
python serve.py                    # shop on :8000, fake PayFast on :8001
```

In a second terminal:

```bash
curl -i -X POST http://127.0.0.1:8000/orders -H 'X-API-Key: shop-key' \
     -H 'Content-Type: application/json' \
     -d '{"sku": "MUG", "quantity": 2, "customer_email": "ana@example.com"}'   # 201
curl -i http://127.0.0.1:8000/orders/1 -H 'X-API-Key: shop-key'               # 200
# drop the X-API-Key header -> 401; "quantity": "2" -> 400; "sku": "TEE" -> 409
```

`python serve.py --provider-mode decline` (402) or `--provider-mode
unavailable` (503 with `Retry-After`) makes PayFast misbehave. Each run
starts from a fresh, seeded database.

## Before you leave

```bash
git status .                       # nothing modified, no .bak left
```

The environment variables only last for the command they prefix, so
there is nothing to switch back. `demos/` is outside the default
`pytest` run (`testpaths = tests` in `pytest.ini`).
