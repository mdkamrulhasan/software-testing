# Week 7 demo: coverage reports, reproduced

A self-contained mini-project for the Week 7 reading, *Coverage-Based
Testing: Measuring and Interpreting Coverage with `coverage.py` and
`pytest-cov`*. Every report in the reading comes from running these
files with coverage.py 7.16. They are laid out the same way as the
reading (`checkout_app/checkout.py`, `tests/test_checkout_v1.py`, ...),
so the file names and line numbers in each report match the reading
exactly.

**Run every command from this folder**, not from `demo-testing-suite/`:

```bash
cd demos/coverage_reports
```

| File | What it shows |
|---|---|
| `checkout_app/checkout.py` | The reading's running example, verbatim. Do not add a docstring or reformat it, because every `Missing` line number in the reading refers to this file. |
| `tests/test_checkout_v1.py` | The thin first suite: 74% statement, 66% with `--branch` |
| `tests/test_checkout_coupons_only.py` | The `16->18` arrow example: 41% |
| `tests/test_checkout_v2.py` | Each gap turned into a behavior-level test: 100% |
| `tests/test_checkout_noassert.py` | Limitation 1: 100% coverage, zero assertions |
| `coverage_settings.toml` | The reading's `[tool.coverage.*]` block (Section 6.6) |

## Why `coverage_settings.toml` and not `pyproject.toml`

The reading puts its configuration in `pyproject.toml`. If this folder
had one, *every* run would pick it up automatically: branch measurement,
`source`, and `fail_under = 90` would all be on from the first command,
and the reading's step-by-step progression (81% → 74% → 66%) could
not be shown. So the same settings live under a name nothing reads by
default, and the "Making Settings Permanent" step passes them
explicitly:

```bash
coverage run --rcfile=coverage_settings.toml -m pytest tests/test_checkout_v1.py
coverage report --rcfile=coverage_settings.toml     # exits 2: total of 66 < 90
```

In a real project, name the file `pyproject.toml` and drop the flag.

## The reading's runs, in order

```bash
coverage run -m pytest tests/test_checkout_v1.py && coverage report     # 81%: tests included
coverage run --source=checkout_app -m pytest tests/test_checkout_v1.py
coverage report -m                                                       # 74%, 8, 16-17, 24, 28
coverage run --branch --source=checkout_app -m pytest tests/test_checkout_v1.py
coverage report -m                                                       # 66%, BrPart 3
coverage html                                                            # htmlcov/index.html

pytest tests/test_checkout_v1.py --cov=checkout_app --cov-branch --cov-report=term-missing
pytest tests/test_checkout_v1.py --cov=checkout_app --cov-branch --cov-fail-under=80   # exit 1

coverage run --branch --source=checkout_app -m pytest tests/test_checkout_coupons_only.py
coverage report -m                                                       # 41%, 16->18

pytest tests/test_checkout_v2.py       --cov=checkout_app --cov-branch --cov-report=term-missing  # 100%
pytest tests/test_checkout_noassert.py --cov=checkout_app --cov-branch --cov-report=term-missing  # 100%
```

Limitation 3 (the boundary mutant) is a live edit. Change line 22's
`amount >= 50` to `amount > 50`, re-run the v2 suite (it still passes,
at 100%), then undo the edit:

```bash
git checkout -- checkout_app/checkout.py
```

`demos/` is outside the default `pytest` run (`testpaths = tests` in
`pytest.ini`), so nothing here affects the main suite's baseline.
`.coverage`, `htmlcov/`, `coverage.xml`, and `coverage.json` are all
git-ignored.
