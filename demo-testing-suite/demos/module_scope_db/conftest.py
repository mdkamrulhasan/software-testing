"""The scope="module" variant of db_connection, from "The Four Scopes"
slide. Contrast with tests/accounts/conftest.py, which uses the default
(and recommended) scope="function".

Run this folder on its own: pytest demos/module_scope_db -v
"""

import sqlite3

import pytest


@pytest.fixture(scope="module")
def db_connection():
    """One connection, reused by every test in this module -- faster
    than reconnecting per test, but now every test in the module shares
    the same table's contents unless each test accounts for that.
    """
    connection = sqlite3.connect(":memory:")
    connection.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
    )
    yield connection
    connection.close()
