# Shop Orders API, v1.1

The shop's own HTTP API, implemented in `shop/api.py`. Every request
except `GET /health` needs the header `X-API-Key: <key>`. Every error
response is JSON of the form `{"error": "<message>"}`, never an HTML
page.

**Changed since v1 (Week 10):** new `GET /health` and `GET /products`;
`POST /orders` takes an optional `coupon` and limits `quantity` to 100;
the order resource has three new fields; any unexpected failure is a
JSON `500`.

## `GET /health`

No API key. `200 OK` with `{"status": "ok"}` while the shop can reach
its database; `503 Service Unavailable` with `{"status": "unavailable"}`
otherwise. It does **not** check PayFast: a PayFast outage does not make
the shop unhealthy (orders get a `503`, browsing still works).

## `GET /products`

`200 OK` with a JSON list, ordered by `sku`:

```json
[{"sku": "MUG", "name": "Coffee mug", "price_cents": 1250, "stock": 5}, ...]
```

## `POST /orders`

Place an order: price it, reserve stock, charge the customer through
PayFast (`payment_provider_api.md`), and record the order.

**Body** (`Content-Type: application/json`)

| Field | Type | Rules |
|---|---|---|
| `sku` | string | An existing product. |
| `quantity` | integer | `1` to `100`. |
| `customer_email` | string | Must contain `@`. |
| `coupon` | string, optional | A coupon code (`user_stories.md`, US-3). Case-insensitive. |

**Responses**

| Status | When | Extra |
|---|---|---|
| `201 Created` | The order was placed and paid. | Body: the order. Header `Location: /orders/<id>`. |
| `400 Bad Request` | Body is not a JSON object, a field is missing, a field breaks a rule, or the coupon is unknown or does not apply. | Nothing is charged. |
| `401 Unauthorized` | `X-API-Key` missing or wrong. | |
| `402 Payment Required` | The provider declined the card. | Stock is released. |
| `404 Not Found` | Unknown `sku`. | |
| `409 Conflict` | Not enough stock. | Nothing is charged. |
| `502 Bad Gateway` | The provider rejected our request (a bug or misconfiguration on our side). | Stock is released. |
| `503 Service Unavailable` | The provider is down or timed out. | Header `Retry-After: 30`. Stock is released. |
| `500 Internal Server Error` | Anything unexpected. | Body `{"error": "internal error"}`, no details. |

**The order resource**

```json
{"id": 1, "sku": "MUG", "quantity": 2, "subtotal_cents": 2500,
 "discount_cents": 0, "total_cents": 2500, "coupon": null,
 "customer_email": "ana@example.com", "status": "paid", "charge_id": "ch_1"}
```

`total_cents = subtotal_cents - discount_cents` is the amount charged.
`coupon` is the code as applied, upper-cased, or `null`. `status` is one
of `pending`, `paid`, `payment_failed`.

## `GET /orders/<id>`

`200 OK` with the order resource, or `404 Not Found`.
