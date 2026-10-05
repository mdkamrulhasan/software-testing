"""All-Defs does not subsume branch coverage.

Week 6 reading: *Data-Flow Testing and Coverage Concepts*, "How the
Criteria Relate", third bullet: "All-Defs is satisfied as soon as each
definition reaches *one* use, which can happen without ever exercising
both outcomes of a nearby branch." The reading's own example
(sum_positive) happens not to show this; this function does.

Def/use events:

    L1  def total_with_tax(amount, show_breakdown)  def amount, show_breakdown
    L2  tax = round(amount * 0.06, 2)                c-use amount; def tax
    L3  total = amount + tax                         c-use amount, tax; def total
    L4  if show_breakdown:                           p-use show_breakdown
    L5      print(...)                               c-use amount, tax
    L6  return total                                 c-use total

One call with show_breakdown=False gives every definition a use:
amount -> L2, tax -> L3, total -> L6, show_breakdown -> L4 (false).
That is All-Defs. But the True branch, and the DU pairs amount -> L5,
tax -> L5, and show_breakdown -> L4 (true), are never exercised:
All-Uses is not met, and branch coverage is 50%.

This code is correct; the point is what the test set leaves untested.
See test_receipt.py.
"""


def total_with_tax(amount, show_breakdown):
    tax = round(amount * 0.06, 2)
    total = amount + tax
    if show_breakdown:
        print(f"subtotal={amount:.2f} tax={tax:.2f}")
    return total
