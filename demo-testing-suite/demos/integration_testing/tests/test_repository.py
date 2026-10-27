"""IP4: OrderRepository against a real SQLite database.

Bottom-up integration, step 1. These test functions are the *drivers*:
they call the repository the way OrderService eventually will, before
anything above the repository is trusted. The database is a real file
(tmp_path), so constraints, foreign keys, and transactions all behave
as they will in production -- which no mock of the repository can do.
"""

import sqlite3

import pytest

from shop import db


def count_orders(connection):
    return connection.execute("SELECT COUNT(*) FROM orders").fetchone()[0]


# -- connectivity and schema ----------------------------------------------
def test_schema_has_both_tables(connection):
    rows = connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
    assert {row["name"] for row in rows} == {"products", "orders"}


def test_create_schema_is_safe_to_run_again(connection):
    db.create_schema(connection)  # e.g. on every application start
    assert connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 2


# -- CRUD -------------------------------------------------------------------
def test_order_create_read_update_delete(connection, repository):
    with connection:
        order_id = repository.create_order("MUG", 2, 2500, "ana@example.com")
    assert repository.get_order(order_id) == {
        "id": order_id, "sku": "MUG", "quantity": 2, "total_cents": 2500,
        "customer_email": "ana@example.com", "status": "pending", "charge_id": None,
    }

    with connection:
        repository.update_order(order_id, "paid", "ch_9")
    assert repository.get_order(order_id)["status"] == "paid"
    assert repository.get_order(order_id)["charge_id"] == "ch_9"

    with connection:
        assert repository.delete_order(order_id)
    assert repository.get_order(order_id) is None


def test_reserve_stock_refuses_to_oversell(connection, repository, stock):
    with connection:
        assert repository.reserve_stock("MUG", 5)
        assert not repository.reserve_stock("MUG", 1)
    assert stock("MUG") == 0


# -- constraints: rules the database enforces, whoever calls it ---------------
def test_database_rejects_negative_stock(connection):
    with pytest.raises(sqlite3.IntegrityError, match="CHECK constraint failed"):
        with connection:
            connection.execute("UPDATE products SET stock = -1 WHERE sku = 'MUG'")


def test_database_rejects_an_order_for_an_unknown_product(connection, repository):
    """R10: SQLite ignores foreign keys unless each connection turns them
    on. db.connect() does; this test fails if that line is removed."""
    with pytest.raises(sqlite3.IntegrityError, match="FOREIGN KEY constraint failed"):
        with connection:
            repository.create_order("NOPE", 1, 100, "ana@example.com")


# -- transactions -------------------------------------------------------------
def test_uncommitted_changes_are_invisible_to_other_connections(connection, repository, stock):
    repository.reserve_stock("MUG", 2)   # opens a transaction; not committed yet
    assert stock("MUG") == 5             # another connection still sees 5
    connection.commit()
    assert stock("MUG") == 3


def test_rollback_undoes_every_statement_in_the_transaction(connection, repository, stock):
    """R3: stock and order are saved together or not at all."""
    with pytest.raises(RuntimeError):
        with connection:
            repository.reserve_stock("MUG", 2)
            repository.create_order("MUG", 2, 2500, "ana@example.com")
            raise RuntimeError("something failed before the commit")
    assert stock("MUG") == 5
    assert count_orders(connection) == 0
