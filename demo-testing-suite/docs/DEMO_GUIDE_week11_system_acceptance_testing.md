# Demo Guide — System Testing and Acceptance Testing

Companion to the two Week 11 readings, *System Testing: Testing the
Whole System from the Outside* and *Acceptance Testing: Building the
Right Thing*. Copied from `docs/DEMO_GUIDE_week10_integration_testing.md`'s
template, same shape, following the readings' section order. Both
readings use one demo folder, `demos/system_acceptance_testing/`.

**Slides:** none yet for this week. The section headings below are the
natural slide boundaries if decks are made later (suggested split: one
75-minute session per reading).

**Two editions, one source.** Like Week 10, each reading comes in two
editions built from the same LaTeX file, with identical section
numbering:
- **Student editions:** `reading_materials/w11.1_system_testing.pdf` and
  `reading_materials/w11.2_acceptance_testing.pdf`, the copies in the
  repository. Every section, concept, figure, exercise, and discussion
  question, with a few secondary listings omitted (the student finds
  them in the demo folder).
- **Instructor editions** (one or two pages longer): add the full
  traceability table, the `RunningShop` helper and second feature file
  listings, an Instructor Note in each reading, and an appendix of notes
  on every practice exercise. **Not in the repository**, because the
  repository is public; they are kept with the LaTeX source.

To rebuild: `pdflatex w11.1_system_testing.tex` (student) or
`pdflatex w11.1_system_testing_instructor.tex` (instructor; a two-line
wrapper that sets `\instructortrue` and `\input`s the reading); the same
for `w11.2_acceptance_testing`. Run `pdflatex` **three times** on a fresh
build: the table of contents fills two pages, so the second pass still
shifts the page numbers it lists. (`latexmk -pdf` or `tectonic` rerun as
needed on their own.) Instructor-only text is wrapped in
`\ifinstructor ... \fi`.

**Before class:** reinstall requirements (this week adds `pytest-bdd`)
and confirm the baseline:

```bash
pip install -r requirements.txt
pytest -v
```

You should still see **75 passed, 3 xfailed, 1 failed**, exactly Week
10's result: this week changes nothing in `app/` or `tests/`, only
`pytest.ini` (two new markers) and `requirements.txt`.

Most of the lecture runs inside the demo folder. **Its commands must be
run from that folder**:

```bash
cd demos/system_acceptance_testing
pytest                      # 58 passed, in about ten seconds
```

The extra time is the point of the week: each of the 37 system and
acceptance tests starts the shop as its own server process.
`demos/system_acceptance_testing/README.md` lists every command with its
expected result.

**Live HTTP:** `python serve.py` starts the shop on port 8000 and the
fake PayFast on 8001. Start it in a second terminal before the System
Under Test section if you want to use `curl`.

---

# Part 1: System Testing

## Where We Are / What Is System Testing?

**Files:** `../integration_testing/tests/test_api.py`, `tests/conftest.py`

Open Week 10's `test_api.py` next to this week's `tests/conftest.py`.
Ask the class what the Week 10 test never did (the reading's three:
never *ran* the shop, one customer at a time, reached inside via the
`stock` fixture and `provider.config`). Then show `_start()`:
`subprocess.Popen`, `--port 0`, the `READY` line. That is the whole
difference between the levels, in one function.

## The System Under Test

**Files:** `specs/system_requirements.md`, `serve.py`, Figure 1

```bash
python serve.py
```

In a second terminal, the README's `curl` commands: `/health` with no
key, `/products`, an order with `"coupon": "FLAT5"`, then
`/_test/config` to make PayFast decline. Point out that `/_test/` is on
the *provider's* port, not the shop's (Discussion Question 3 asks why
that matters).

Walk the requirements box: ask which lines are functional and which are
not, then the ISO/IEC 25010 table. Ask what makes NFR-1 testable (a
load, a condition, a threshold).

## Planning System Tests

**File:** `specs/system_test_plan.md`

Scroll through it once; it is one page. Spend the time on Section 5
(entry/exit criteria) and Section 8 (findings): F1 is a real finding,
and the next section shows where it came from.

## The Test Environment and Harness

**Files:** `tests/conftest.py`, `tests/integration/conftest.py`

Show the two conftests side by side: `stock` reads SQLite directly at
the integration level; `shop.stock()` calls `GET /products` at the
system level. The reading's comparison table is these two files.

## Functional System Testing: Scenarios

```bash
pytest tests/system/test_end_to_end_scenarios.py -v        # 4 passed
```

Point at the requirement IDs in the docstrings.

## Non-Functional System Testing

### Concurrency (the centerpiece)

```bash
pytest tests/system/test_concurrency_and_performance.py -v                 # 2 passed
SHOP_SERVICE=racy pytest tests/unit tests/integration -q                   # 21 passed
SHOP_SERVICE=racy pytest tests/system/test_concurrency_and_performance.py --tb=short
#   {'sold': 10, 'refused': 0, 'stock_left': 4, 'cards_charged': 10}
```

Let the failure message sit on the screen: ten mugs sold, ten cards
charged, five mugs owned, four still "in stock". Then open
`shop/service_racy.py` and ask the class to find the defect before you
draw Figure 2. Ask why no test in `tests/integration/` could be fixed to
catch it (Discussion Question 4).

Optional: delete the `start_line.wait()` line and set `delay=0`, run the
racy version a few times: it usually passes (Exercise 2). Restore with
`git checkout tests/system/test_concurrency_and_performance.py`.

Repeatability, if asked: each version was run eight times while this
demo was built; correct 8/8 pass, racy 8/8 fail.

### Performance

```bash
pytest tests/system/test_concurrency_and_performance.py -k within_a_second -s -q
#   latency: median ~0.15 s, max ~0.25 s
```

Numbers vary by machine; the budget is 1 s.

### Security and robustness: finding F1

```bash
pytest tests/system/test_robustness_and_security.py -v             # 14 passed
patch -p1 < specs/f1_week10_validation.patch                        # Week 10's validation
pytest tests/system/test_robustness_and_security.py --tb=short      # 2 failed: HTML 500 page
patch -R -p1 < specs/f1_week10_validation.patch                     # fixed again
```

Then open the server log the failing test wrote (its path is under
pytest's `tmp_path`, e.g. `/tmp/pytest-of-$USER/pytest-current/*/server.log`)
to show the `OverflowError` / `ProgrammingError` tracebacks. Stress
that this defect is **real** and is also present in Week 10's shop
(`demos/integration_testing/`), which is deliberately left as the Week
10 reading printed it. Ask: who decides the maximum quantity? (Not the
developer; Discussion Question 5.)

### Recoverability and operability

```bash
pytest tests/system/test_recovery.py -v                           # 3 passed
```

## System Tests in the Suite

```bash
pytest -m system -q                                               # 23 passed, 35 deselected
```

Then build the "one defect, four levels" table live, predicting each
cell before running it (the README's switch table). Save the acceptance
column of the `per_unit` row for Part 2.

---

# Part 2: Acceptance Testing

## Where We Are / What Is Acceptance Testing?

```bash
SHOP_COUPONS=per_unit pytest tests/unit tests/integration tests/system -q   # 44 passed
```

44 passing tests, and a defect. Don't say where yet.

## User Stories and Specification by Example

**File:** `specs/user_stories.md`

Before showing the three-amigos notes, put up the *first-draft* story
("FLAT5 gives $5 off orders over $10") and ask everyone to write down,
individually, the total for 2 mugs and for 4 stickers. The room usually
splits on at least one. That split is the reading's Section 5. Then
reveal the notes and the examples they produced.

## ATDD, BDD, and Gherkin

**Files:** `tests/acceptance/features/*.feature`

Read `coupons.feature` aloud as the product owner would. Point out:
dollars, not cents; "I", not "the client"; the `Background` table
creating the catalog.

## Automating Scenarios with pytest-bdd

**Files:** `tests/acceptance/conftest.py`, `tests/acceptance/test_*.py`

```bash
pytest tests/acceptance -v                                         # 14 passed
pytest tests/acceptance/test_place_order.py --gherkin-terminal-reporter -vv
```

Show that each test module is three lines, and that `start_shop` is the
*system* test harness. Then the step-pattern pitfall, live:

1. In `tests/acceptance/conftest.py`, change `"{sku:w}"` back to
   `"{sku}"` in the plain `I order ...` step.
2. Append the reading's "Two coupons cannot be combined" scenario to
   `coupons.feature`.
3. `pytest tests/acceptance/test_coupons.py -k combined -vv --tb=line`:
   it fails on `unknown sku: MUG" with coupons "SAVE10" and "FLAT5`.
4. Restore `{sku:w}` and rerun: now `StepDefinitionNotFoundError`, the
   honest ATDD red.
5. `git checkout tests/acceptance/` to restore both files.

## The Defect Only Acceptance Testing Found

```bash
SHOP_COUPONS=per_unit pytest tests/unit -v                         # 8 passed
SHOP_COUPONS=per_unit pytest tests/acceptance -q --tb=line          # 2 failed
SHOP_COUPONS=per_unit pytest tests/acceptance/test_coupons.py -k "MUG-2-FLAT5" \
    --gherkin-terminal-reporter -vv --tb=line
```

Point out that the two failures are exactly the two tester questions.
Then `SHOP_SERVICE=racy pytest tests/acceptance` (14 passed): acceptance
tests do not replace system tests.

## Operational Acceptance Testing

No new code; the OAT table points at Part 1's recovery tests. The
Knight Capital box has no code: ask what `/health` could report that
would have exposed the eighth server (Exercise 5: a version).

## Common Failures / Walkthroughs / Best Practices / Common Mistakes

No new code. Each reading's walkthrough (restocking; order history) is
its Exercise 6 and is **not** implemented in the repository.

## Practice Exercises / Discussion Questions

Intentionally **not** implemented in the repository, the same way Weeks
3–10 left their exercises. Notes on every exercise are in the
instructor editions' appendices.

---

## After class

From `demos/system_acceptance_testing/`: `git status .` should be clean
(no `shop.db`, no `.orig`/`.rej` files from `patch`, no edits to
`conftest.py` or the feature files). Stop any `serve.py` (Ctrl-C).
From the project root, confirm `pytest -v` is still at **75 passed, 3
xfailed, 1 failed**.

## Extending this for the *next* lecture

1. Week 12+ (Continuous Testing) can start from this folder: the
   `unit`/`integration`/`system`/`acceptance` split and the markers map
   directly onto pipeline stages (fast on every push, slow before
   release).
2. The system and acceptance harness (`tests/conftest.py`) is reusable
   as is; a CI job needs only `pip install -r requirements.txt` and
   `pytest -m "system or acceptance"` from this folder.
3. Copy this file as a starting template for the next lecture's guide.
