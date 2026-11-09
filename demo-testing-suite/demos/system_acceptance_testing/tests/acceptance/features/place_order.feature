Feature: Place an order
  As a customer
  I want to order a product and get a confirmation showing what I paid
  So that I know my order went through

  Background:
    Given the shop sells:
      | sku | name       | price | stock |
      | MUG | Coffee mug | 12.50 | 5     |

  # US-2.1, US-2.2
  Scenario: A successful order is confirmed and charged
    When I order 2 "MUG"
    Then my order is confirmed
    And I am charged $25.00
    And I can look my order up again

  # US-2.3
  Scenario: Ordering more than is in stock
    When I order 6 "MUG"
    Then I am told "insufficient stock"
    And I am not charged

  # US-2.4
  Scenario: A declined card
    Given my card will be declined
    When I order 2 "MUG"
    Then I am told "payment declined"
    And I am not charged
    And the catalog shows 5 "MUG" in stock
