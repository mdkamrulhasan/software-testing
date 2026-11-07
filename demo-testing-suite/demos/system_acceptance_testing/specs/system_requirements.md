# Shop System Requirements Specification (excerpt)

The **test basis for system testing** (Week 11 reading, *System
Testing*). It describes the shop as one system, from the outside: what
a customer, an operator, or an attacker can observe through its HTTP
interface. It says nothing about classes, tables, or modules. The
detailed request and response formats are in `shop_api.md`; coupon
rules are in `user_stories.md`.

Every requirement has an ID so that tests can trace to it
(`specs/system_test_plan.md`, Section 6).

## Functional requirements

| ID | Requirement |
|---|---|
| **SYS-1** | A customer can list the products, with each product's name, price, and current stock. |
| **SYS-2** | A customer can order 1 to 100 units of one product. The shop charges the order total through PayFast and records the order as `paid`. *(The upper limit of 100 was added in Week 11; see "Change history" below.)* |
| **SYS-3** | A customer can fetch a placed order by its id. |
| **SYS-4** | The shop never sells stock it does not have: for every product, the units in `paid` orders plus the units in stock always equal the units the shop started with, **even when many customers order at the same time**. |
| **SYS-5** | If an order cannot be paid (card declined, provider down, provider rejects the request), the customer is not charged, the stock is returned, and the response says why (`shop_api.md`). |
| **SYS-6** | Every request except `GET /health` requires the shop's API key. |
| **SYS-7** | Every response, including every error, is JSON. The shop never returns an HTML page, a stack trace, or other internal details, whatever the request contains. |
| **SYS-8** | Orders and stock survive a restart of the shop. |
| **SYS-9** | Coupon codes can be applied to an order (`user_stories.md`, US-3). |

## Non-functional requirements

| ID | Quality | Requirement |
|---|---|---|
| **NFR-1** | Performance | With 10 customers ordering at the same moment, and PayFast answering each charge in 100 ms, every customer gets a response within **1 second**. |
| **NFR-2** | Recoverability | When PayFast recovers from an outage, the shop accepts orders again **without being restarted**. |
| **NFR-3** | Operability | `GET /health` answers `200` within 1 second while the shop and its database are working, needs no API key, and stays `200` during a PayFast outage (the shop itself is still healthy). |

## Environment

The shop runs as one process (`serve.py`), with a SQLite database file
and PayFast reached over HTTP. In the test environment PayFast is the
fake in `fakes/payment_provider.py`, which also offers test-only
control endpoints (`/_test/...`) so that tests can make it slow,
decline cards, or go down.

## Change history

| Version | Change |
|---|---|
| Week 10 | SYS-1 to SYS-9 did not exist as a system specification; the shop had only its API contract (`shop_api.md` v1). |
| Week 11 | Written for system testing. **SYS-2's upper limit (100 units) and SYS-7's "whatever the request contains"** were added after system test `test_hostile_input_gets_a_json_4xx` crashed the Week 10 shop with an HTML `500` page (see `system_test_plan.md`, Section 8, finding F1). |
