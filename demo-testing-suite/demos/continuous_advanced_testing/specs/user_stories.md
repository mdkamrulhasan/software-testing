# Shop User Stories and Acceptance Criteria

The **test basis for acceptance testing** (Week 11 reading, *Acceptance
Testing*). Written with the product owner, in the customer's language:
dollars, not cents; "my card", not "PayFast returns 402".

Each acceptance criterion became one or more Gherkin scenarios in
`tests/acceptance/features/`. The scenario names are the traceability.

---

## US-1 Browse products

> **As a** shopper,
> **I want to** see each product's price and how many are in stock,
> **so that** I don't try to buy something that is sold out.

| AC | Acceptance criterion | Scenario (`browse_products.feature`) |
|---|---|---|
| US-1.1 | Every product is listed with its name, price in dollars, and stock. | *The catalog shows price and stock* |
| US-1.2 | A sold-out product is listed with a stock of 0. | *The catalog shows price and stock* |
| US-1.3 | After I buy something, the catalog shows the reduced stock. | *Buying reduces the stock shown* |

---

## US-2 Place an order

> **As a** customer,
> **I want to** order a product and get a confirmation showing what I paid,
> **so that** I know my order went through.

| AC | Acceptance criterion | Scenario (`place_order.feature`) |
|---|---|---|
| US-2.1 | When I order an in-stock product, my order is confirmed and I am charged the price times the quantity. | *A successful order is confirmed and charged* |
| US-2.2 | I can look my order up again later. | *A successful order is confirmed and charged* |
| US-2.3 | If there is not enough stock, I am told so and not charged. | *Ordering more than is in stock* |
| US-2.4 | If my card is declined, I am told so, I am not charged, and the stock is not used up. | *A declined card* |

---

## US-3 Coupon codes

> **As a** customer,
> **I want to** enter a coupon code when I order,
> **so that** I pay less.

Agreed with the product owner, Week 11 ("three amigos" session: product
owner, developer, tester). Questions raised in the session are recorded
under the table: each one became an example.

| AC | Acceptance criterion | Scenario (`coupons.feature`) |
|---|---|---|
| US-3.1 | `SAVE10` takes 10% off the order, rounded down to the cent. | *A valid coupon reduces the amount charged* (outline) |
| US-3.2 | `FLAT5` takes $5.00 off the **order**, once, however many units are in it. | *A valid coupon reduces the amount charged* (outline) |
| US-3.3 | `FLAT5` can only be used on an order of **$10.00 or more** (before the discount). | *A valid coupon reduces the amount charged*, *FLAT5 needs an order of at least $10.00* |
| US-3.4 | Codes are not case-sensitive: `save10` works. | *A valid coupon reduces the amount charged* (outline) |
| US-3.5 | An unknown code is rejected with a message, and I am not charged. | *An unknown coupon is rejected* |
| US-3.6 | The confirmation shows the price before the discount, the discount, and what I paid. | every scenario in the outline |

**Questions from the three-amigos session, and the answers:**

- *Tester:* "Is FLAT5 $5 off each mug, or off the whole order?" —
  *Product owner:* "The whole order. It's a $5 coupon, not a $5-per-item
  coupon." → the example *2 mugs with FLAT5 pay $20.00*.
- *Tester:* "Is the $10 minimum the price of one item, or of the order?"
  — *Product owner:* "The order. Four $3 stickers is $12, so FLAT5
  works." → the example *4 stickers with FLAT5 pay $7.00*.
- *Developer:* "What if 10% isn't a whole number of cents?" — *Product
  owner:* "Round the discount down; we never give away more than 10%."
  → the example *1 pen ($1.99) with SAVE10: discount $0.19, pay $1.80*.
- *Developer:* "Can two coupons be combined?" — *Product owner:* "Not
  this release." → `coupon` is a single string. (Out of scope, recorded.)
