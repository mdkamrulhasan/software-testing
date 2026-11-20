"""The shop's test pipeline: the same stages on your machine and in CI.

    python pipeline.py                      # every stage, in order; stop at the first failure
    python pipeline.py unit integration     # only these stages (in pipeline order)
    python pipeline.py --list               # what each stage runs

The GitHub Actions workflow (.github/workflows/shop-pipeline.yml, at the
repository root) runs these stages by calling this file, so "it passed
on my machine" and "it passed in CI" mean the same thing.

Stages are ordered from cheapest to most expensive, and the pipeline
stops at the first failure: a typo should fail in seconds, not after
the system tests have started a server for every test.

Every stage writes a JUnit XML report to reports/<stage>.xml, and the
system and acceptance stages keep each test's server log under
reports/tmp/<stage>/. In CI, both are uploaded when a stage fails.
"""

import argparse
import os
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPORTS = HERE / "reports"
PYTEST = [sys.executable, "-m", "pytest", "-p", "no:cacheprovider", "-q"]
COVERAGE_GATE = 80  # percent of shop/, measured by the unit and integration stages


@dataclass
class Stage:
    name: str
    purpose: str
    command: list

    def run(self):
        started = time.perf_counter()
        result = subprocess.run(self.command, cwd=HERE)
        return result.returncode, time.perf_counter() - started


def junit(stage):
    """pytest's own JUnit report for a stage, or None."""
    return ["--junitxml", str(REPORTS / f"{stage}.xml")]


def server_logs(stage):
    """Keep tmp_path (and so each test's server.log) where CI can upload it."""
    return ["--basetemp", str(REPORTS / "tmp" / stage)]


STAGES = [
    Stage("static", "pylint, errors only: crashes waiting to happen, no style",
          [sys.executable, "-m", "pylint", "--errors-only",
           "shop", "fakes", "serve.py", "variants.py", "pipeline.py"]),
    Stage("unit", "tests/unit: the developer's tests (coverage starts here)",
          [*PYTEST, "tests/unit", *junit("unit"),
           "--cov", "--cov-config=.coveragerc", "--cov-report="]),
    Stage("integration", f"tests/integration, plus the coverage gate ({COVERAGE_GATE}%)",
          [*PYTEST, "tests/integration", *junit("integration"),
           "--cov", "--cov-config=.coveragerc", "--cov-append",
           "--cov-report=term", f"--cov-fail-under={COVERAGE_GATE}"]),
    Stage("contract", "tests/contract: the shop and PayFast keep their contract (Week 14)",
          [*PYTEST, "tests/contract", *junit("contract")]),
    Stage("system", "-m system: the running shop, tests in parallel",
          [*PYTEST, "-m", "system", "-n", "auto", *junit("system"), *server_logs("system")]),
    Stage("acceptance", "-m acceptance: the customer's examples",
          [*PYTEST, "-m", "acceptance", "-n", "auto",
           *junit("acceptance"), *server_logs("acceptance")]),
]
BY_NAME = {stage.name: stage for stage in STAGES}


def counts(stage):
    """(tests, failures) from a stage's JUnit report, if it wrote one."""
    path = REPORTS / f"{stage}.xml"
    if not path.exists():
        return None
    suite = ET.parse(path).getroot()
    suite = suite.find("testsuite") if suite.tag == "testsuites" else suite
    failed = int(suite.get("failures", 0)) + int(suite.get("errors", 0))
    return int(suite.get("tests", 0)) - int(suite.get("skipped", 0)), failed


def summarize(rows):
    lines = ["| Stage | Result | Tests | Seconds |", "|---|---|---|---|"]
    for name, result, seconds in rows:
        found = counts(name)
        tests = "-" if found is None else f"{found[0] - found[1]}/{found[0]} passed"
        lines.append(f"| {name} | {result} | {tests} | {seconds} |")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stages", nargs="*", metavar="stage",
                        help=f"default: all of {', '.join(BY_NAME)}")
    parser.add_argument("--list", action="store_true", help="show the stages and exit")
    args = parser.parse_args(argv)

    if args.list:
        for stage in STAGES:
            print(f"{stage.name:<12} {stage.purpose}")
        return 0
    unknown = [name for name in args.stages if name not in BY_NAME]
    if unknown:
        parser.error(f"unknown stage(s): {', '.join(unknown)}")
    chosen = [s for s in STAGES if not args.stages or s.name in args.stages]

    variant = {k: v for k, v in os.environ.items() if k.startswith("SHOP_") and v}
    if variant:
        # A defective variant replaces one of the measured modules, so the
        # gate would fail for that reason alone: it measures the shop as shipped.
        gated = BY_NAME["integration"].command
        gated[:] = [arg for arg in gated if not arg.startswith("--cov-fail-under")]
        print(f"Running a defective variant ({', '.join(f'{k}={v}' for k, v in variant.items())}):"
              " coverage is reported, but not gated.")

    (REPORTS / "tmp").mkdir(parents=True, exist_ok=True)   # pytest creates only the last level
    for stage in chosen:
        (REPORTS / f"{stage.name}.xml").unlink(missing_ok=True)
    (HERE / ".coverage").unlink(missing_ok=True)

    rows, failed = [], None
    for stage in chosen:
        if failed:
            rows.append((stage.name, "skipped", "-"))
            continue
        print(f"\n=== {stage.name}: {stage.purpose}", flush=True)
        code, seconds = stage.run()
        rows.append((stage.name, "passed" if code == 0 else "**FAILED**", f"{seconds:.1f}"))
        if code != 0:
            failed = stage.name

    table = summarize(rows)
    print("\n" + table)
    print(f"\nPipeline {'FAILED at ' + failed if failed else 'passed'}.")
    if os.environ.get("GITHUB_STEP_SUMMARY"):          # shown on the run's page in GitHub
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as summary:
            variant = ", ".join(f"{k}={v}" for k, v in sorted(os.environ.items())
                                if k.startswith("SHOP_") and v) or "the correct shop"
            summary.write(f"### Shop pipeline ({variant})\n\n{table}\n\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
