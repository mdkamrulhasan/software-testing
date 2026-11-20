"""Run the same tests many times and count the outcomes: a flaky-test detector.

    python tools/rerun.py 20 flaky_examples/flaky_timing.py
    python tools/rerun.py 20 tests/system -n 2

Everything after the run count is passed to pytest unchanged. A test
that both passes and fails on the same code is flaky; a test that
always fails is broken; only one that always passes can be trusted.
"""

import subprocess
import sys
from collections import Counter


def main():
    if len(sys.argv) < 3 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    runs, pytest_args = int(sys.argv[1]), sys.argv[2:]
    outcomes = Counter()
    for number in range(1, runs + 1):
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *pytest_args],
            capture_output=True, text=True)
        last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "?"
        outcome = "passed" if result.returncode == 0 else "FAILED"
        outcomes[outcome] += 1
        print(f"run {number:>3}: {outcome:<6}  {last_line}", flush=True)
    verdict = ("stable (always passed)" if outcomes["FAILED"] == 0 else
               "broken (always failed)" if outcomes["passed"] == 0 else "FLAKY")
    print(f"\n{outcomes['passed']}/{runs} passed, {outcomes['FAILED']}/{runs} failed: {verdict}")
    return 0 if verdict.startswith("stable") else 1


if __name__ == "__main__":
    sys.exit(main())
