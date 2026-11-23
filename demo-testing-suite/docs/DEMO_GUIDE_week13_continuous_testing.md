# Demo Guide — Continuous Testing (Week 13)

Companion to the Week 13 reading, *Continuous Testing: Every Change,
Every Time*. Copied from `docs/DEMO_GUIDE_week11_system_acceptance_testing.md`'s
template, same shape, following the reading's section order. The
reading uses `demos/continuous_advanced_testing/` (shared with Week 14)
and the workflow at the repository root,
`.github/workflows/shop-pipeline.yml`.

**Slides:** none yet for this week. The section headings below are the
natural slide boundaries if a deck is made later.

**Two editions, one source.** Like Weeks 10–11:
- **Student edition:** `reading_materials/w13_continuous_testing.pdf`,
  the copy in the repository.
- **Instructor edition** (same length, plus an Instructor Note and an
  appendix of notes on every practice exercise). **Not in the
  repository**, because the repository is public; it is kept with the
  LaTeX source.

To rebuild: `pdflatex w13_continuous_testing.tex` (student) or
`pdflatex w13_continuous_testing_instructor.tex` (instructor; a
three-line wrapper that sets `\instructortrue` and `\input`s the
reading). Run `pdflatex` **three times** on a fresh build (the table of
contents fills two pages).

**Before class:**

```bash
pip install -r requirements.txt      # nothing new this week
pytest -v                            # 75 passed, 3 xfailed, 1 failed: unchanged
cd demos/continuous_advanced_testing
pytest                               # 67 passed, about 9 seconds
python pipeline.py                   # every stage passes, about 12 seconds
```

**Before the lecture, in GitHub** (once the workflow is on `main`):
*Actions → Shop pipeline → Run workflow*, choose `racy`, and run it. It
takes about a minute; you will open the red run in class. The button
appears only after the workflow file reaches the default branch.

---

## Where We Are

Put Week 11's "each defect caught at exactly one level" table up, and
ask: *what does that table assume?* (That somebody runs the system and
acceptance tests.) Then `SHOP_SERVICE=racy pytest tests/unit
tests/integration`: 21 passed. "Push it?"

## What Is Continuous Testing?

No code. CI, CD, continuous deployment, continuous testing; shift left
and right. Keep it short: the demo is the argument.

## The Deployment Pipeline

**Files:** `pipeline.py`, Figure 1

```bash
python pipeline.py --list
python pipeline.py
```

Show the `STAGES` list next to Figure 1. Point out the rule "one
definition of the pipeline": the workflow calls this file.

## Running the Pipeline in GitHub Actions

**Files:** `.github/workflows/shop-pipeline.yml`

Open the workflow and the latest run on the branch side by side (the
*Actions* tab). Walk: `on` (paths), `matrix`, `needs`,
`upload-artifact`. Open a job's log, then the run's summary table
(written by `pipeline.py` via `$GITHUB_STEP_SUMMARY`).

## Quality Gates

### Static analysis: the first run's finding

To reproduce the finding (the folder has the fix):

```bash
sed -i '/problem = "no attempt was made"/d' shop/payments.py
python -m pylint --errors-only shop               # E0606 at shop/payments.py:43
python -c "from shop.payments import PaymentClient
PaymentClient('http://127.0.0.1:9', 'k', retries=-1).charge(100, 'order-1')"
                                                  # UnboundLocalError
git checkout shop/payments.py                     # the fix again
```

The one-liner turns the warning into an `UnboundLocalError`. Ask the class which week's technique
this is (Week 6: use before definition).

### Coverage gate

```bash
python pipeline.py unit integration              # 82.63% >= 80%
```

Ask why not 100%.

### Each defect stops at the first stage that can see it

```bash
SHOP_SERVICE=racy python pipeline.py             # FAILED at system (22/23)
SHOP_COUPONS=per_unit python pipeline.py         # FAILED at acceptance (14/16)
SHOP_PAYMENTS=no_idempotency python pipeline.py  # FAILED at contract (4/7); Week 14 explains
```

Ask the class to predict each stage first. Then open the red GitHub run
you started before class, and its server-log artifact.

## Fast Feedback at Scale

```bash
pytest -m system -q                              # about 5 s
pytest -m system -q -n auto                      # about 3.5 s on 2 CPUs
```

Explain why this is safe (port 0, `tmp_path`, Week 11's harness).

## Flaky Tests

```bash
python tools/rerun.py 20 flaky_examples/flaky_timing.py                    # e.g. 18/20 or 19/20
python tools/rerun.py 10 flaky_examples/flaky_timing.py tests/system -n 2  # about half fail
pytest flaky_examples/flaky_order.py -q                                    # 2 passed
pytest flaky_examples/flaky_order.py -q -k look_the_order_up               # 1 failed: 404
pytest flaky_examples/flaky_order.py -q -n 2                               # 1 failed: 404
```

The timing example's pass rate depends on the machine: on a very fast
idle laptop it may pass 20/20 alone, which is itself a good point — run
the "busy" line. Ask what the right budget would be (NFR-1's 1 s).

## Shift Right

No code. `/health` (Week 11, NFR-3) is the bridge. CrowdStrike case
study: ask what stage was missing.

## Common Failures / Walkthrough / Best Practices / Common Mistakes

No new code. The walkthrough is Exercise 6 and is **not** implemented
in the repository.

## Practice Exercises / Discussion Questions

Intentionally **not** implemented in the repository, the same way Weeks
3–11 left their exercises. Notes on every exercise are in the
instructor edition's appendix.

---

## After class

From `demos/continuous_advanced_testing/`: `git status .` should be
clean (`reports/` is ignored; no `.coverage`, no `shop.db`, no edits to
`shop/payments.py`). From the project root, `pytest -v` is still at
**75 passed, 3 xfailed, 1 failed**.

## Extending this for the *next* lecture

1. Week 14 uses the same folder: `tests/contract/` and `ai_generated/`
   are already there. See `DEMO_GUIDE_week14_advanced_ai_testing.md`.
2. Copy this file as a starting template for the next lecture's guide.
