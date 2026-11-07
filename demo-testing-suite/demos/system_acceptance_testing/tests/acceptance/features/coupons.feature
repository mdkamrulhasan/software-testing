Feature: Coupon codes at checkout
  As a customer
  I want to enter a coupon code when I order
  So that I pay less

  Background:
    Given the shop sells:
      | sku     | name           | price | stock |
      | MUG     | Coffee mug     | 12.50 | 10    |
      | STICKER | Laptop sticker | 3.00  | 100   |
      | PEN     | Gel pen        | 1.99  | 50    |

  # US-3.1 to US-3.4, US-3.6. Each row is an example agreed with the
  # product owner; the comment says which question it answers.
  Scenario Outline: A valid coupon reduces the amount charged
    When I order <quantity> "<sku>" with coupon "<code>"
    Then my order is confirmed
    And my confirmation shows a subtotal of $<subtotal>, a discount of $<discount>, and a total of $<total>
    And I am charged $<total>

    Examples:
      | sku     | quantity | code   | subtotal | discount | total |
      | MUG     | 1        | SAVE10 | 12.50    | 1.25     | 11.25 |
      | MUG     | 3        | SAVE10 | 37.50    | 3.75     | 33.75 |
      | PEN     | 1        | SAVE10 | 1.99     | 0.19     | 1.80  |
      | MUG     | 1        | FLAT5  | 12.50    | 5.00     | 7.50  |
      | MUG     | 2        | FLAT5  | 25.00    | 5.00     | 20.00 |
      | STICKER | 4        | FLAT5  | 12.00    | 5.00     | 7.00  |
      | MUG     | 1        | save10 | 12.50    | 1.25     | 11.25 |

  # US-3.3
  Scenario: FLAT5 needs an order of at least $10.00
    When I order 3 "STICKER" with coupon "FLAT5"
    Then I am told "FLAT5 requires an order of at least $10.00"
    And I am not charged
    And the catalog shows 100 "STICKER" in stock

  # US-3.5
  Scenario: An unknown coupon is rejected
    When I order 1 "MUG" with coupon "FREESTUFF"
    Then I am told "unknown coupon code: FREESTUFF"
    And I am not charged
