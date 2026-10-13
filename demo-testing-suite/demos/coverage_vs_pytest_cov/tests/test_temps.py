# Deliberately thin: describe() is tested only with a "mild" value, so
# lines 7 ("freezing") and 10 ("hot") stay uncovered (67% branch).
# report.py covers those two lines, but misses line 9 -- the two runs
# only reach 100% when combined (coverage run --append).
from tempconv.temps import describe, to_fahrenheit


def test_boiling():
    assert to_fahrenheit(100) == 212


def test_mild():
    assert describe(20) == "mild"
