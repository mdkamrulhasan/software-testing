# Design and API Review: Shop Orders

Held **before** any integration test was written, on: the architecture
sketch (README.md), `shop_api.md`, `payment_provider_api.md`, and the
signatures in `shop/`. The goal is not to approve the design but to
find the integration points where two components could disagree, and
to turn each disagreement into a test.

## Integration points reviewed

| ID | From | To | Kind | Contract |
|---|---|---|---|---|
| IP1 | HTTP client | `api.py` | HTTP/JSON | `shop_api.md` |
| IP2 | `api.py` | `OrderService` | Python call + exceptions | `service.py`, `errors.py` |
| IP3 | `OrderService` | `OrderRepository` | Python call + transactions | `repository.py` |
| IP4 | `OrderRepository` | SQLite | SQL | `db.py` schema |
| IP5 | `OrderService` | `PaymentClient` | Python call + exceptions | `payments.py`, `errors.py` |
| IP6 | `PaymentClient` | PayFast | HTTP/JSON, Bearer auth | `payment_provider_api.md` |

## Checklist used

- **Interfaces:** do caller and callee agree on names, types, *units*, and optional/required fields?
- **Data formats:** JSON shapes, number formats, text encodings; what a 5xx body looks like.
- **Errors:** is every failure of the callee mapped to something the caller handles, and documented?
- **Authentication:** which credential, which header, what happens when it is wrong?
- **State and transactions:** what must change together? What if a step fails half-way?
- **Dependencies:** availability, latency, timeouts, retries, and whether a retry is safe.
- **Data flow:** does each value mean the same thing at every hop?

## Findings, and the tests they became

| # | Finding | IP | Integration test(s) |
|---|---|---|---|
| R1 | PayFast v2 changed `amount` from a dollars string (`"12.50"`) to integer cents (`1250`). Our client predates v2. | IP6 | `test_payments_stubbed.py::test_request_matches_the_provider_contract`, `test_payments_live.py::test_charge_succeeds_in_integer_cents` |
| R2 | The total is computed in the service and sent through the client; nothing checks the provider receives the same number we store. | IP3, IP5, IP6 | `test_order_service.py::test_successful_order_charges_exactly_the_order_total` |
| R3 | Reserving stock and creating the order must be atomic. | IP3, IP4 | `test_repository.py::test_rollback_undoes_every_statement_in_the_transaction`, `test_order_service.py::test_order_the_database_rejects_leaves_stock_untouched` |
| R4 | The charge cannot be inside the database transaction. If it fails, who gives the stock back? | IP3, IP5 | `test_order_service.py::test_declined_payment_gives_the_stock_back`, `::test_provider_outage_gives_the_stock_back`, `test_api.py::test_declined_card_is_402_and_the_stock_comes_back` |
| R5 | The provider's 5xx bodies are not guaranteed to be JSON. | IP6 | `test_payments_live.py::test_outage_is_retried_then_reported_as_unavailable`, `test_payments_stubbed.py::test_retry_after_an_html_503_reuses_the_idempotency_key` |
| R6 | The client retries a `POST` that moves money. Is a retry safe? | IP6 | `test_payments_stubbed.py::test_retry_after_an_html_503_reuses_the_idempotency_key`, `test_payments_live.py::test_same_reference_is_charged_only_once` |
| R7 | No timeout in the first design: a slow provider would hang every order. | IP6 | `test_payments_live.py::test_slow_provider_times_out` |
| R8 | Two credentials (`X-API-Key` in, `Bearer` out). A wrong *provider* key is our misconfiguration: 502, not "retry later". | IP1, IP6 | `test_api_topdown.py::test_missing_api_key_never_reaches_the_service`, `test_payments_live.py::test_wrong_api_key_is_our_error_and_is_not_retried`, `test_api.py::test_wrong_provider_key_is_502_not_503` |
| R9 | Every service exception needs a documented status; Flask's default errors are HTML. | IP1, IP2 | `test_api_topdown.py::test_service_errors_map_to_the_documented_status`, `::test_unknown_route_answers_in_json_not_html` |
| R10 | SQLite ignores `REFERENCES` unless each connection enables foreign keys. | IP4 | `test_repository.py::test_database_rejects_an_order_for_an_unknown_product` |
| R11 | Input validation: where does it happen, and does bad input ever reach the service? | IP1, IP2 | `test_api_topdown.py::test_invalid_bodies_never_reach_the_service` |

## Open item

- A **timeout** leaves the charge's outcome unknown: PayFast may have
  charged even though we gave up. The service currently releases the
  stock and marks the order `payment_failed`. A production system would
  reconcile later, by asking PayFast about the `Idempotency-Key`. Out of
  scope for this demo; see the reading, Section 9.
