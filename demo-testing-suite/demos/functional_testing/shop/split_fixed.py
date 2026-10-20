def split_bill(total, people):
    cents = round(total * 100)
    base, extra = divmod(cents, people)
    return [(base + 1) / 100 if i < extra else base / 100
            for i in range(people)]
