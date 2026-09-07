"""Exercises the db_connection fixture two ways:
  1. Directly, with raw SQL -- exactly as shown on the "yield Fixtures:
     Setup + Teardown in One Function" slide.
  2. Through app.accounts.user_repository.UserRepository -- the "one
     layer up" version described in that module's docstring, which
     later lectures (mocking, integration testing) and the final
     project are expected to build on.
"""

from app.accounts.user_repository import UserRepository


def test_insert_and_query_user_raw_sql(db_connection):
    # Matches the slide verbatim.
    db_connection.execute("INSERT INTO users (name) VALUES ('Alice')")
    db_connection.commit()
    row = db_connection.execute("SELECT name FROM users").fetchone()
    assert row[0] == "Alice"


def test_insert_and_query_user_via_repository(db_connection):
    repo = UserRepository(db_connection)

    user_id = repo.insert_user("Bob")

    assert repo.get_user_by_name("Bob") == (user_id, "Bob")
