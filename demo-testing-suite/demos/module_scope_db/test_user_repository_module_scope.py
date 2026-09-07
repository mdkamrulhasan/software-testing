"""Both tests below share the SAME db_connection (scope="module"), so
each is written to be aware of what earlier tests in this file already
inserted, rather than assuming an empty table. Compare the extra care
required here with tests/accounts/test_user_repository.py's
function-scoped version -- that difference in code is the real cost of
choosing a wider scope, not just an abstract warning on a slide.
"""


def test_insert_alice(db_connection):
    db_connection.execute("INSERT INTO users (name) VALUES ('Alice')")
    db_connection.commit()
    row = db_connection.execute(
        "SELECT name FROM users WHERE name = 'Alice'"
    ).fetchone()
    assert row[0] == "Alice"


def test_insert_bob_alongside_alice(db_connection):
    # Because the connection (and its table) persists across both tests
    # in this module, Alice's row from the previous test is still here.
    # This test deliberately checks for that instead of being surprised
    # by it -- the discipline a wider scope demands.
    db_connection.execute("INSERT INTO users (name) VALUES ('Bob')")
    db_connection.commit()
    names = {row[0] for row in db_connection.execute("SELECT name FROM users")}
    assert names == {"Alice", "Bob"}
