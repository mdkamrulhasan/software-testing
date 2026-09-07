"""Percentage-discount pricing logic.

Used across this lecture to demonstrate, in slide order: plain asserts,
assertion rewriting on failure, pytest.approx for floats, and
pytest.raises for error paths. See tests/pricing/test_discounts.py.
"""


def calculate_discounted_price(price, discount_percent):
    """Return ``price`` after applying ``discount_percent`` percent off.

    Args:
        price: The original price. Any numeric type.
        discount_percent: A percentage in the range [0, 100].

    Returns:
        The discounted price.

    Raises:
        ValueError: If ``discount_percent`` is outside [0, 100].

    LIVE DEMO HOOK -- "The Payoff: Assertion Rewriting" slide:
        To reproduce that slide's failure output live, temporarily swap
        which line below is commented out (the second forgets to divide
        by 100 -- the exact bug on the slide), then run:

            pytest tests/pricing/test_discounts.py::test_ten_percent_discount -v

        and revert immediately afterward. Every other test in this
        project assumes the correct version is active.
    """
    if not 0 <= discount_percent <= 100:
        raise ValueError("discount_percent must be between 0 and 100")

    return price * (1 - discount_percent / 100)
    # return price * (1 - discount_percent)  # DEMO ONLY -- forgets / 100
