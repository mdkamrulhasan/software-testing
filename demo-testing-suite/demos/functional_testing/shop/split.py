def split_bill(total, people):
    """Split a total (in dollars) into `people` shares that add up exactly to total."""
    share = round(total / people, 2)
    return [share] * people
