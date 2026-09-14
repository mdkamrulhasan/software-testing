"""Weight-based shipping-cost calculation.

This is the running example for Lecture 3 (Equivalence Partitioning,
Boundary-Value Analysis, and Negative Testing). The implementation below
is deliberately shipped with one boundary bug -- see KNOWN BUG -- so
that boundary-value analysis has something real to find, the same way
Lecture 1's late-fee bug gives negative testing something real to find.

Specification: given a package weight in kilograms, return the shipping
cost: $5.00 for 0 < weight <= 1 kg, $10.00 for 1 < weight <= 5 kg, and
$20.00 for 5 < weight <= 20 kg. Weights of 0 kg or less, or above 20 kg,
are invalid and should raise a ValueError.
"""


def determine_shipping_cost(weight_kg):
    """Return the shipping cost (in dollars) for a package of ``weight_kg``.

    Args:
        weight_kg: Package weight in kilograms. Must be > 0 and <= 20.

    Returns:
        The shipping cost as a float: 5.00, 10.00, or 20.00.

    Raises:
        ValueError: If ``weight_kg`` is <= 0 or > 20.

    KNOWN BUG (deliberate, for the BVA slide):
        The second branch below compares with a strict ``<`` instead of
        ``<=``. Per the specification, weight == 5.0 belongs to the
        1 < weight <= 5 class and should cost $10.00, but the strict
        comparison lets it fall through to the $20.00 branch instead.
        tests/pricing/test_shipping.py documents this with
        @pytest.mark.xfail rather than silently fixing it -- do not
        "fix" this without first reading that test file.

    KNOWN ISSUE (deliberate, for the negative-testing slide):
        Passing a non-numeric value (e.g. None, a string) is not
        validated up front, so it surfaces as a raw, implementation-level
        TypeError from the comparison below instead of a clear,
        documented error. See tests/pricing/test_shipping.py for the
        negative test that captures this.
    """
    if weight_kg <= 0:
        raise ValueError("weight_kg must be positive")
    if weight_kg > 20:
        raise ValueError("packages over 20kg require freight shipping")
    if weight_kg <= 1:
        return 5.00
    elif weight_kg < 5:  # KNOWN BUG -- should be <=, see docstring above
        return 10.00
    else:
        return 20.00
