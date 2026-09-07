"""A tiny SQLite-backed user store.

The lecture's slide demos a bare sqlite3 connection directly inside a
fixture and a test -- that is reproduced as-is in
tests/accounts/conftest.py (the db_connection fixture) and
tests/accounts/test_user_repository.py, so what students see on screen
during lecture matches this class exactly.

This class exists one layer up from that raw-connection demo, as the
natural next step once a suite is doing more than one query. It gives
later lectures and the final project something concrete to build on:
  - A mocking lecture can mock UserRepository instead of sqlite3 itself.
  - An integration-testing lecture can swap ":memory:" for a real test
    database without touching any test that only talks to UserRepository.
  - The final project can add methods here (update_user, delete_user,
    list_users, ...) the same way this lecture added insert/get.
"""


class UserRepository:
    """Wraps a sqlite3 connection that already has a `users` table."""

    def __init__(self, connection):
        """Store the connection. The caller owns the connection's
        lifecycle (opening and closing it) -- this class only issues
        queries against it."""
        self._connection = connection

    def insert_user(self, name):
        """Insert a new user and return their generated id."""
        cursor = self._connection.execute(
            "INSERT INTO users (name) VALUES (?)", (name,)
        )
        self._connection.commit()
        return cursor.lastrowid

    def get_user_by_name(self, name):
        """Return the first matching user as an (id, name) tuple, or
        None if no such user exists."""
        return self._connection.execute(
            "SELECT id, name FROM users WHERE name = ?", (name,)
        ).fetchone()
