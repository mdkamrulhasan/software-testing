"""Score a test suite the way you would score one an AI wrote (Week 14).

    python ai_generated/evaluate.py ai_generated/suite_from_code.py ai_generated/suite_from_spec.py
    python ai_generated/evaluate.py tests/integration          # a human-written suite, for comparison
    python ai_generated/evaluate.py my_ai_suite.py --quick     # skip the mutants

For each suite it reports four things. None of them alone says the
suite is good; together they show what it can and cannot catch:

  correct shop   How many tests pass against the shop as specified. A test
                 that FAILS here is either broken or has the wrong expected
                 value (the oracle problem): a human must decide which.
  coverage       Branch coverage of shop/, from the passing run.
  known defects  Each deliberately defective variant (variants.py): caught
                 if a test that passes on the correct shop fails on it.
  mutants        Small, plausible code changes (MUTANTS below), each in a
                 fresh copy of this folder: killed if a test that passes on
                 the correct shop fails on the mutant.

Only tests that pass on the correct shop count toward the last two, as
in mutation testing: a test that always fails catches nothing.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent

VARIANTS = {
    "per_unit coupons": {"SHOP_COUPONS": "per_unit"},
    "racy service": {"SHOP_SERVICE": "racy"},
    "no Idempotency-Key": {"SHOP_PAYMENTS": "no_idempotency"},
}

# (name, file, original text, mutated text): each original must occur exactly once.
MUTANTS = [
    ("FLAT5 minimum: < becomes <=", "shop/pricing.py",
     "if subtotal < FLAT5_MINIMUM_CENTS:", "if subtotal <= FLAT5_MINIMUM_CENTS:"),
    ("SAVE10 rounds to nearest", "shop/pricing.py",
     "discount = subtotal // 10 ", "discount = round(subtotal / 10) "),
    ("coupon codes case-sensitive", "shop/pricing.py",
     "code = coupon.upper()", "code = coupon"),
    ("quantity 100 rejected", "shop/api.py",
     "not 1 <= body[\"quantity\"] <= MAX_QUANTITY", "not 1 <= body[\"quantity\"] < MAX_QUANTITY"),
    ("out of stock is 400, not 409", "shop/api.py",
     "return error(409, \"insufficient stock\")", "return error(400, \"insufficient stock\")"),
    ("no Retry-After on 503", "shop/api.py",
     "{\"Retry-After\": \"30\"}", "{}"),
    ("/health needs the key", "shop/api.py",
     "if request.path == \"/health\":", "if request.path == \"/healthz\":"),
    ("wrong Location header", "shop/api.py",
     "{\"Location\": f\"/orders/{order['id']}\"}", "{\"Location\": \"/orders\"}"),
    ("stock kept after a failed payment", "shop/service.py",
     "                self.repository.release_stock(sku, quantity)\n", ""),
    ("failed order left 'pending'", "shop/service.py",
     "update_order(order_id, \"payment_failed\")", "update_order(order_id, \"pending\")"),
    ("coupon stored as typed", "shop/service.py",
     "coupon=coupon.upper() if coupon else None", "coupon=coupon"),
    ("whole stock cannot be bought", "shop/repository.py",
     "AND stock >= ?", "AND stock > ?"),
    ("no Idempotency-Key header", "shop/payments.py",
     "            \"Idempotency-Key\": reference,\n", ""),
    ("no retry after a 5xx", "shop/payments.py",
     "retries=1, session=None", "retries=0, session=None"),
]


def run_pytest(folder, target, env_extra=None, coverage_json=None):
    """Run pytest on `target` in `folder`; return (passed ids, failed ids)."""
    report = Path(tempfile.mkdtemp()) / "report.xml"
    command = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
               target, "--junitxml", str(report)]
    if coverage_json:
        command += ["--cov", "--cov-config=.coveragerc", f"--cov-report=json:{coverage_json}"]
    env = {k: v for k, v in os.environ.items() if not k.startswith("SHOP_")}
    env.update(env_extra or {})
    subprocess.run(command, cwd=folder, env=env, capture_output=True, text=True)
    passed, failed = set(), set()
    if report.exists():
        for case in ET.parse(report).getroot().iter("testcase"):
            # module::test, so that ids match between this folder and a copy
            # (pytest's rootdir, and so the full classname, differs between them)
            test_id = f"{case.get('classname').rsplit('.', 1)[-1]}::{case.get('name')}"
            bad = case.find("failure") is not None or case.find("error") is not None
            (failed if bad else passed).add(test_id)
    shutil.rmtree(report.parent, ignore_errors=True)
    return passed, failed


def mutated_copy(file, original, mutated):
    workdir = Path(tempfile.mkdtemp())
    copy = workdir / DEMO.name
    shutil.copytree(DEMO, copy, ignore=shutil.ignore_patterns("reports", "__pycache__", ".coverage"))
    path = copy / file
    source = path.read_text()
    assert source.count(original) == 1, f"mutant for {file} does not apply: {original!r}"
    path.write_text(source.replace(original, mutated))
    return workdir, copy


def evaluate(target, quick=False):
    coverage_file = Path(tempfile.mkdtemp()) / "coverage.json"
    good, bad = run_pytest(DEMO, target, coverage_json=coverage_file)
    total = len(good) + len(bad)
    coverage = json.loads(coverage_file.read_text())["totals"]["percent_covered"]
    print(f"\n### {target}\n")
    print(f"correct shop   {len(good)}/{total} passed")
    for test_id in sorted(bad):
        print(f"                 FAILED on the correct shop: {test_id.split('::')[-1]}")
    print(f"coverage       {coverage:.0f}% of shop/ (branch coverage)")

    caught = []
    for name, env in VARIANTS.items():
        _, failed = run_pytest(DEMO, target, env)
        if failed & good:
            caught.append(name)
    print(f"known defects  {len(caught)}/{len(VARIANTS)} caught"
          + (f": {', '.join(caught)}" if caught else ""))

    if quick:
        return
    survived = []
    for name, file, original, mutated in MUTANTS:
        workdir, copy = mutated_copy(file, original, mutated)
        try:
            _, failed = run_pytest(copy, target)
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        if not failed & good:
            survived.append(name)
    killed = len(MUTANTS) - len(survived)
    print(f"mutants        {killed}/{len(MUTANTS)} killed")
    for name in survived:
        print(f"                 survived: {name}")


def main():
    args = [a for a in sys.argv[1:] if a != "--quick"]
    if not args:
        sys.exit(__doc__)
    for target in args:
        evaluate(target, quick="--quick" in sys.argv)


if __name__ == "__main__":
    main()
