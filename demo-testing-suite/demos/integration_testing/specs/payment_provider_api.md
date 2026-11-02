# PayFast Charges API, v2 (third-party provider)

The external payment provider the shop integrates with. This is the
provider's published contract: the shop does not control it, and the
tests may not change it. `fakes/payment_provider.py` implements it for
testing.

## `POST /v1/charges`

Create a charge.

**Headers**

| Header | Required | Value |
|---|---|---|
| `Authorization` | yes | `Bearer <secret key>` |
| `Content-Type` | yes | `application/json` |
| `Idempotency-Key` | recommended | Any unique string. A repeated request with the same key returns the original charge instead of charging again. |

**Body**

| Field | Type | Rules |
|---|---|---|
| `amount` | integer | **In cents** (minor units). Must be a positive integer: `1250` means $12.50. *Changed in v2: v1 took a decimal string of dollars, `"12.50"`.* |
| `currency` | string | `"USD"` only. |
| `reference` | string | The merchant's own reference, e.g. `"order-7"`. |

**Responses**

| Status | Body | Meaning |
|---|---|---|
| `201 Created` | `{"id": "ch_1", "amount": 1250, "currency": "USD", "status": "succeeded"}` | Charged. |
| `400 Bad Request` | `{"error": "<message>"}` | The request breaks a rule above. Do not retry. |
| `401 Unauthorized` | `{"error": "invalid_api_key"}` | Missing or wrong key. Do not retry. |
| `402 Payment Required` | `{"error": "card_declined"}` | The card was declined. Do not retry. |
| `5xx` | **Not guaranteed to be JSON** (may be an HTML page from a proxy) | Temporary failure. Safe to retry *with the same `Idempotency-Key`*. |

**Operational notes**

- Typical latency is under 300 ms. Clients should set a timeout and
  treat a timeout as "outcome unknown": the charge may or may not have
  been made. Retrying with the same `Idempotency-Key` is safe.
- Planned maintenance windows return `503`.
