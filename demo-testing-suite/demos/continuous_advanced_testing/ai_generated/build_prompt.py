"""Build the exact prompt behind each AI-generated test suite (Week 14).

    python ai_generated/build_prompt.py from_code > prompt.txt
    python ai_generated/build_prompt.py from_spec > prompt.txt

Paste the output into any AI assistant, save its answer as a .py file in
this folder, and score it with evaluate.py. Both prompts ask for the
same thing -- tests for the shop's HTTP API, using the in-process
fixtures of tests/integration/conftest.py -- and differ only in what
the assistant is shown:

  from_code  the shop's SOURCE CODE, as it was before the three-amigos
             session: shop/pricing.py is today's shop/pricing_per_unit.py,
             with the comments that announce its defect removed (the
             developer did not know it had one).
  from_spec  the shop's SPECIFICATIONS: the API contract, the user stories
             with their agreed examples, and the system requirements.
"""

import re
import sys
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent

TASK = """\
You are helping to test a small online shop written in Python with Flask.
Write one pytest test module that thoroughly tests the shop's HTTP API:
POST /orders (including coupon codes), GET /orders/<id>, GET /products,
and GET /health.

Use the fixtures defined in tests/integration/conftest.py, shown below:
`client` is a Flask test client for the fully assembled shop (real
service, real SQLite database, fake payment provider over HTTP);
`provider` is the fake payment provider (set provider.config["MODE"] to
"decline" or "unavailable" to make it misbehave; provider.charges lists
the charges it made); `stock(sku)` reads a product's stock from the
database. Send the header X-API-Key: shop-key on every request except
/health. The database starts with MUG ($12.50, stock 5), STICKER ($3.00,
stock 100), and TEE ($20.00, stock 0).

Reply with the Python module only.
"""

SOURCES = {
    "from_code": [
        ("shop/api.py", "shop/api.py"),
        ("shop/service.py", "shop/service.py"),
        ("shop/pricing.py", "shop/pricing_per_unit.py"),   # the code as it then was
        ("shop/repository.py", "shop/repository.py"),
        ("shop/errors.py", "shop/errors.py"),
        ("tests/integration/conftest.py", "tests/integration/conftest.py"),
    ],
    "from_spec": [
        ("specs/shop_api.md", "specs/shop_api.md"),
        ("specs/user_stories.md", "specs/user_stories.md"),
        ("specs/system_requirements.md", "specs/system_requirements.md"),
        ("tests/integration/conftest.py", "tests/integration/conftest.py"),
    ],
}


def as_the_developer_had_it(source):
    """pricing_per_unit.py without the module docstring and the comments
    that say it is defective."""
    source = re.sub(r'\A""".*?"""\n+', "", source, flags=re.S)
    return re.sub(r"\s+# KNOWN DEFECT.*", "", source)


def build(kind):
    parts = [TASK]
    for shown_as, path in SOURCES[kind]:
        text = (DEMO / path).read_text()
        if path == "shop/pricing_per_unit.py":
            text = as_the_developer_had_it(text)
        parts.append(f"===== {shown_as} =====\n{text}")
    return "\n".join(parts)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in SOURCES:
        sys.exit(__doc__)
    print(build(sys.argv[1]))
