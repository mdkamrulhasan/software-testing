"""Generate the reading's pairwise checkout set and check it (Section 8.2).

Prints the AllPairs rows, then counts every (parameter, parameter, value,
value) pair the four options produce and how many of them the rows cover.
Run from this folder:  python pairwise.py
"""
from itertools import combinations, product

from allpairspy import AllPairs

params = [
    ["card", "paypal", "gift_card"],
    ["standard", "express", "pickup"],
    ["member", "guest"],
    ["none", "SAVE10", "FLAT5"],
]

if __name__ == "__main__":
    rows = list(AllPairs(params))
    for i, row in enumerate(rows, 1):
        print(i, list(row))

    need = {(a, b, x, y)
            for a, b in combinations(range(len(params)), 2)
            for x, y in product(params[a], params[b])}
    have = {(a, b, r[a], r[b])
            for r in rows
            for a, b in combinations(range(len(params)), 2)}
    print("pairs needed:", len(need), " covered:", len(need & have),
          " tests:", len(rows))
