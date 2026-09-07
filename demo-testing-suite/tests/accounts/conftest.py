"""The db_connection fixture, at function scope -- the default, and the
recommended choice (see demos/module_scope_db/ for the scope="module"
variant from "The Four Scopes" slide, and demos/scope_pitfall/ for a
worked example of why a wider, mutable-state scope can misbehave).

Deliberately named to match the slides exactly, and deliberately using a
raw sqlite3 connection (not app.accounts.user_repository.UserRepository)
so what's on screen during lecture matches this fixture verbatim.
test_user_repository.py in this directory exercises both styles.
"""

import sqlite3

import pytest


@pytest.fixture
def db_connection():
    """An in-memory SQLite connection, pre-populated with a `users` table.

    Setup runs before `yield`; teardown (closing the connection) runs
    after -- and runs even if the test raises. See "yield Fixtures:
    Setup + Teardown in One Function" and "The yield Fixture Timeline".
    """
    connection = sqlite3.connect(":memory:")  # setup
    connection.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
    )
    yield connection  # hand off to the test
    connection.close()  # teardown -- always runs, pass or fail
