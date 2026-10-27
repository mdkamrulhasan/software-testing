# Weeks 8–9 demo: functional testing

A self-contained mini-project for the Weeks 8–9 reading, *Functional
Testing: Designing Tests from the Specification*. Every listing and
output in the reading comes from running these files with pytest 9.1,
Hypothesis 6.170 and allpairspy 2.5. The layout is the reading's own
(`shop/shipping.py`, `tests/test_order.py`, ...), so its imports and
commands work as printed.

**Run every command from this folder**, not from `demo-testing-suite/`:

```bash
cd demos/functional_testing
```

| File | What it is |
|---|---|
| `shop/shipping.py` | `shipping_fee`, REQ-1..4, correct version |
| `shop/shipping_buggy.py` | The rule-priority bug: free shipping checked before express |
| `shop/order.py` | The `Order` state machine, REQ-5..7 |
| `shop/split.py` | `split_bill`, REQ-8: the reading's **buggy** first version |
| `shop/split_fixed.py` | The fix: work in integer cents |
| `tests/test_shipping_dt.py` | Decision table, one test per rule (R1..R5) |
| `tests/test_shipping_bva.py` | The $50 boundary (49.99 / 50.0) |
| `tests/test_order.py` | 5 valid + 15 invalid transitions + 2 refund tests |
| `tests/test_checkout_pairwise.py` | The 10 pairwise rows as pytest cases (skipped: no oracle yet) |
| `tests/test_split_pbt.py` | The Hypothesis property for REQ-8 |
| `pairwise.py` | Prints the `AllPairs` rows and checks that all 45 pairs are covered |

Note that the two "switch" demos go in opposite directions, following
the slides: `test_shipping_dt.py` imports the **correct** shipping code
and you switch it to the buggy one; `test_split_pbt.py` imports the
**buggy** `split.py` and you switch it to the fix. A plain `pytest` in
this folder therefore reports `1 failed, 29 passed, 10 skipped`, and
the one failure is REQ-8's, on purpose.

## The demos, in the reading's order

```bash
pytest tests/test_shipping_bva.py -v           # Section 5:   2 passed
pytest tests/test_shipping_dt.py -v            # Section 6.4: 5 passed

# Section 6.5: in tests/test_shipping_dt.py, change the import to
#   from shop.shipping_buggy import shipping_fee
pytest tests/test_shipping_dt.py               # FAILED ...[R1-member-express]; 1 failed, 4 passed
# (switch the import back afterwards)

pytest tests/test_order.py -v                  # Section 7.5: 22 passed

python pairwise.py                             # Section 8.2: 10 rows; pairs needed: 45  covered: 45
pytest tests/test_checkout_pairwise.py -v      # 10 skipped -- each row still needs an oracle

rm -rf .hypothesis
pytest tests/test_split_pbt.py                 # Section 9.1: fails, shrunk to total_cents=1, people=2

# Section 9.2: in tests/test_split_pbt.py, change the import to
#   from shop.split_fixed import split_bill
pytest tests/test_split_pbt.py                 # 1 passed
# (switch the import back afterwards)
```

`.hypothesis/` is Hypothesis's example database: failing inputs are
saved there and retried first on the next run. Delete it to watch
Hypothesis search from scratch.

## The $50 boundary mutant (Section 5)

The reading says the boundary test catches `>= 50` changed to `> 50`.
To show it, edit `shop/shipping.py`, run, and restore:

```bash
sed -i.bak 's/amount >= 50/amount > 50/' shop/shipping.py
pytest tests/test_shipping_bva.py              # FAILED [50.0-0.0]: assert 7.99 == 0.0
mv shop/shipping.py.bak shop/shipping.py
```

## Before you leave

```bash
git status .                                   # nothing modified, no .bak left
rm -rf .hypothesis
```
