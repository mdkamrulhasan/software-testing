Feature: See my schedule
  As a student
  I want to see my schedule
  So that I know what I am taking and what I owe

  Background:
    Given the students and courses in SPEC.md

  # US-3.1 -- WORKED EXAMPLE (provided)
  Scenario: A student sees their courses, total credits, and fee
    When S14 looks at their schedule
    Then they see the courses MTH201, HIS105, PHY230 and ENG150
    And they see 15 credits and a fee of $1,425.00

