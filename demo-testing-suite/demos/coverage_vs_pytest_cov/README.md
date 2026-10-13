# Demo: `coverage.py` vs. `pytest-cov`

A self-contained mini-project for the standalone 10-slide deck
*`coverage.py` vs. `pytest-cov`: How They Relate and When to Use Which*.
It is independent of the Week 7 reading's `checkout_app` (that one lives
in `../coverage_reports/`). Every output below was produced by running
these files with coverage.py 7.16, pytest-cov 7.1, and pytest-xdist.

**Run every command from this folder**, so report paths
(`tempconv/temps.py`) match the slides:

```bash
cd demos/coverage_vs_pytest_cov
```

| File | What it is |
|---|---|
| `tempconv/temps.py` | The code under test: `to_fahrenheit()` and `describe()`. Don't reformat it; the `Missing` line numbers (7, 9, 10) refer to this file. |
| `tests/test_temps.py` | A deliberately thin suite: 67% branch, missing lines 7 and 10. |
| `report.py` | A command-line tool that pytest never runs. Measured with `coverage run`, it misses only line 9. |
| `coverage_settings.toml` | The slide's `[tool.coverage.*]` config (see below). |

Slide 8 needs `pytest-xdist`, which is in `requirements.txt` at the
suite root (`pip install -r requirements.txt`).

## Why `coverage_settings.toml` and not `pyproject.toml`

The slide puts the config in `pyproject.toml`. If this folder had one,
every run would pick it up, and `source = ["tempconv"]` would hide the
"forget `--source`" pitfall on slide 10. So, as in `../coverage_reports/`,
the settings live under a name nothing reads by default. Pass the file
explicitly:

```bash
pytest --cov --cov-config=coverage_settings.toml                  # exit 1: 66.67% < 80
coverage run --rcfile=coverage_settings.toml -m pytest
coverage report --rcfile=coverage_settings.toml                   # exit 2: 67 < 80
```

In a real project, name the file `pyproject.toml` and drop the flags.

## The deck's runs, slide by slide

Start each slide's demo clean with `coverage erase`.

**Slide 4: same measurement, two ways** (both print `67%   7, 10`)

```bash
pytest --cov=tempconv --cov-branch --cov-report=term-missing
coverage run --branch --source=tempconv -m pytest
coverage report -m
```

**Slide 5: one data file, one config**

```bash
pytest --cov=tempconv --cov-branch
ls -a                     # .coverage is here
coverage report -m        # same 67% table, no tests re-run
coverage html             # open htmlcov/index.html
```

Then the config run from the section above.

**Slide 7: when to use `coverage.py` directly**

```bash
coverage erase
coverage run --branch --source=tempconv report.py -5 30    # prints two lines
coverage report -m                                          # 83%, missing 9
coverage run --append --branch --source=tempconv -m pytest
coverage report -m                                          # 100%: script + tests
```

**Slide 8: when to use `pytest-cov`**

```bash
pytest -n 2 --cov=tempconv --cov-branch                    # 67%: workers measured
coverage erase
coverage run --branch --source=tempconv -m pytest -n 2
coverage report                                             # 0% + "No data was collected"
pytest --cov=tempconv --cov-branch --cov-fail-under=90     # tests pass, exit 1
echo $?
```

The 0% is the point of the slide: `coverage run` traced only the main
pytest process, and the tests ran in xdist worker processes it never
saw. (Raw coverage.py can measure subprocesses with extra setup;
pytest-cov does it for you.)

**Slide 10: pitfalls**

```bash
coverage erase
coverage run -m pytest && coverage report                   # TOTAL 85%: test files inflate it
pytest --cov=tempconv.nothere                               # warnings only, tests green
```

The `__init__.py` rows (0 statements) also appear in the 85% table;
the slide omits them for space.

## After the demo

```bash
coverage erase && rm -rf htmlcov
```

`.coverage`, `htmlcov/`, `coverage.xml`, and `coverage.json` are
git-ignored. `demos/` is outside the default `pytest` run
(`testpaths = tests` in `pytest.ini`), so nothing here affects the main
suite's baseline.
