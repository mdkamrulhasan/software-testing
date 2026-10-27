# Shop Orders API, v1

The shop's own HTTP API, implemented in `shop/api.py`. Every request
needs the header `X-API-Key: <key>`. Every error response is JSON of the
form `{"error": "<message>"}`, never an HTML page.

## `POST /orders`

Place an order: reserve stock, charge the customer through PayFast
(`payment_provider_api.md`), and record the order.

**Body** (`Content-Type: application/json`)

| Field | Type | Rules |
|---|---|---|
| `sku` | string | An existing product. |
| `quantity` | integer | `>= 1` |
| `customer_email` | string | Must contain `@`. |

**Responses**

| Status | When | Extra |
|---|---|---|
| `201 Created` | The order was placed and paid. | Body: the order. Header `Location: /orders/<id>`. |
| `400 Bad Request` | Body is not a JSON object, a field is missing, or a field breaks a rule. | |
| `401 Unauthorized` | `X-API-Key` missing or wrong. | |
| `402 Payment Required` | The provider declined the card. | Stock is released. |
| `404 Not Found` | Unknown `sku`. | |
| `409 Conflict` | Not enough stock. | Nothing is charged. |
| `502 Bad Gateway` | The provider rejected our request (400/401 from PayFast: a bug or misconfiguration on our side). | Stock is released. |
| `503 Service Unavailable` | The provider is down or timed out. | Header `Retry-After: 30`. Stock is released. |

**The order resource**

```json
{"id": 1, "sku": "MUG", "quantity": 2, "total_cents": 2500,
 "customer_email": "ana@example.com", "status": "paid", "charge_id": "ch_1"}
```

`status` is one of `pending`, `paid`, `payment_failed`.

## `GET /orders/<id>`

`200 OK` with the order resource, or `404 Not Found`.
