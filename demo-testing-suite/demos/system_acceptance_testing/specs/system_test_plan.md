# System Test Plan: Shop, Week 11

A one-page plan in the spirit of ISO/IEC/IEEE 29119-3's test plan,
scaled to a classroom system. Section numbers are referred to by the
Week 11 reading, *System Testing*.

## 1. Scope

**In scope:** the shop as deployed by `serve.py`: its HTTP API, its
SQLite database file, and its connection to PayFast, tested only
through external interfaces.

**Out of scope:** PayFast itself (third party; replaced by the fake);
browsers and user interfaces (the shop has none); load beyond 10
concurrent customers; anything already covered at a lower level and not
visible from outside (e.g. which SQL a repository method issues).

## 2. Test basis

`system_requirements.md` (SYS-1 to SYS-9, NFR-1 to NFR-3) and
`shop_api.md` v1.1. Coupon rules (SYS-9) are tested at the acceptance
level, from `user_stories.md`.

## 3. Test environment

| Item | Test environment | Production (assumed) |
|---|---|---|
| Shop | `serve.py`, one process per test, port chosen by the OS | the same `serve.py` behind a load balancer |
| Database | a new SQLite file per test (`tmp_path`) | one SQLite file on disk |
| PayFast | `fakes/payment_provider.py` over real HTTP, with `/_test/` controls | PayFast v2 |
| Client | `requests`, from the test process | any HTTP client |
| Concurrency | real threads, real sockets | real threads, real sockets |

The environment is as close to production as the classroom allows; the
two known differences (the fake provider; one test machine) are the
main residual risks (Section 7).

## 4. Approach

| Test type | Technique | File |
|---|---|---|
| Functional | Use-case scenarios (main success + alternative flows) | `tests/system/test_end_to_end_scenarios.py` |
| Security / robustness | Negative and hostile inputs; access control per endpoint | `tests/system/test_robustness_and_security.py` |
| Concurrency | Simultaneous customers for scarce stock | `tests/system/test_concurrency_and_performance.py` |
| Performance | Latency under 10 simultaneous customers | `tests/system/test_concurrency_and_performance.py` |
| Recoverability / operability | Dependency outage and recovery; restart; health probe | `tests/system/test_recovery.py` |

Every system test starts the shop as a separate process and uses only
HTTP. A test may use the fake provider's `/_test/` endpoints, because
they belong to the *test environment*, not to the system under test.

## 5. Entry and exit criteria

**Entry:** all unit and integration tests pass (`pytest tests/unit
tests/integration`); `serve.py` starts and `/health` answers `200`.

**Exit:** every requirement in Section 6 has at least one passing system
test; no open finding of severity *high*; any open *medium* finding is
recorded with a decision.

## 6. Traceability

| Requirement | System test(s) |
|---|---|
| SYS-1 | `test_browse_order_and_look_the_order_up` |
| SYS-2 | `test_browse_order_and_look_the_order_up`, `test_sold_out_product_is_refused_and_nothing_is_charged`, `test_hostile_input_gets_a_json_4xx[quantity-just-over-the-limit]` |
| SYS-3 | `test_browse_order_and_look_the_order_up` |
| SYS-4 | `test_several_customers_one_after_another`, **`test_ten_customers_race_for_the_last_five_mugs`** |
| SYS-5 | `test_sold_out_product_is_refused_and_nothing_is_charged`, `test_declined_card_charges_nothing_and_returns_the_stock` |
| SYS-6 | `test_every_endpoint_except_health_needs_the_key` (x3), `test_health_needs_no_key` |
| SYS-7 | `test_hostile_input_gets_a_json_4xx` (x8), `test_body_that_is_not_json_gets_a_json_400`, `test_unknown_route_answers_in_json` |
| SYS-8 | `test_orders_and_stock_survive_a_restart` |
| SYS-9 | acceptance: `tests/acceptance/features/coupons.feature` |
| NFR-1 | `test_ten_simultaneous_orders_each_answered_within_a_second` |
| NFR-2 | `test_orders_work_again_after_a_provider_outage` |
| NFR-3 | `test_health_needs_no_key`, `test_health_stays_ok_during_a_provider_outage` |

## 7. Risks

| Risk | Mitigation |
|---|---|
| The fake PayFast behaves better than the real one. | It enforces the published contract (Week 10); contract checks at the integration level. |
| Timing-based tests (NFR-1, the race) are flaky on a slow machine. | Generous budget (1 s for ~0.1 s of work); the race uses a barrier and a 0.2 s provider delay, so it does not depend on luck. Re-run 8 times before relying on it. |
| One test machine is not production hardware. | NFR-1 is a smoke-level check, not a capacity test; a real capacity test needs production-like hardware (reading, Section 8). |

## 8. Findings

| ID | Found by | Severity | Description | Status |
|---|---|---|---|---|
| **F1** | `test_hostile_input_gets_a_json_4xx[sku-is-a-list]`, `[quantity-too-big-for-sqlite]` | Medium | A `sku` sent as a JSON list, or a `quantity` too large for SQLite (`10**30`), crashed the request: Flask answered with its HTML `500` page, breaking SYS-7. Present in the Week 10 shop. | **Fixed** in Week 11: `sku` must be a string, `quantity` at most 100 (product owner's decision; SYS-2 updated), and a JSON handler for any `500`. Reproduce with `patch -p1 < specs/f1_week10_validation.patch`. |

**Demonstration defects** (deliberate, switched in with environment
variables; see README.md): `SHOP_SERVICE=racy` (found only by
`test_ten_customers_race_for_the_last_five_mugs`) and
`SHOP_COUPONS=per_unit` (found only by the acceptance tests).
