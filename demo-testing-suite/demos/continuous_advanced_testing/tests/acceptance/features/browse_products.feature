Feature: Browse products
  As a shopper
  I want to see each product's price and how many are in stock
  So that I don't try to buy something that is sold out

  Background:
    Given the shop sells:
      | sku | name       | price | stock |
      | MUG | Coffee mug | 12.50 | 5     |
      | TEE | T-shirt    | 20.00 | 0     |

  # US-1.1, US-1.2
  Scenario: The catalog shows price and stock
    When I look at the catalog
    Then I see:
      | sku | name       | price | stock |
      | MUG | Coffee mug | 12.50 | 5     |
      | TEE | T-shirt    | 20.00 | 0     |

  # US-1.3
  Scenario: Buying reduces the stock shown
    When I order 2 "MUG"
    Then the catalog shows 3 "MUG" in stock
