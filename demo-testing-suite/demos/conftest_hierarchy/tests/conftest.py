"""Top-level conftest.py -- visible to every test file below this
directory, including tests/checkout/.

This little tree exists purely to be LOOKED AT during the "conftest.py
Hierarchy" slide -- open the file explorer / `tree` output and point at
real folders instead of only the diagram.

Run: pytest demos/conftest_hierarchy -v
"""

import pytest


@pytest.fixture
def sample_cart():
    return {"items": [{"name": "widget", "price": 9.99, "quantity": 3}]}
