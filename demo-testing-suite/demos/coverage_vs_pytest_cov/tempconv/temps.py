def to_fahrenheit(c):
    return c * 9 / 5 + 32


def describe(c):
    if c < 0:
        return "freezing"
    elif c < 25:
        return "mild"
    return "hot"
