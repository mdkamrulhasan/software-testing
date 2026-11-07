"""Connecting to the shop's SQLite database and creating its schema."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    sku            TEXT PRIMARY KEY,
    name           TEXT NOT NULL,
    price_cents    INTEGER NOT NULL CHECK (price_cents > 0),
    stock          INTEGER NOT NULL CHECK (stock >= 0)
);
CREATE TABLE IF NOT EXISTS orders (
    id             INTEGER PRIMARY KEY,
    sku            TEXT NOT NULL REFERENCES products (sku),
    quantity       INTEGER NOT NULL CHECK (quantity > 0),
    subtotal_cents INTEGER NOT NULL,
    discount_cents INTEGER NOT NULL DEFAULT 0,
    total_cents    INTEGER NOT NULL,
    coupon         TEXT,
    customer_email TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    charge_id      TEXT
);
"""


def connect(path):
    """Open the database at `path` (a file, or ":memory:").

    `check_same_thread=False` because the server hands each request its
    own connection, which may be closed by a different worker thread.
    """
    connection = sqlite3.connect(path, timeout=10, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")  # off by default in SQLite
    return connection


def create_schema(connection):
    """Create the tables. Safe to call on a database that already has them."""
    connection.executescript(SCHEMA)
