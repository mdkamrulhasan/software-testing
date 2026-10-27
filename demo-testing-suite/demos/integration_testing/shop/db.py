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
    total_cents    INTEGER NOT NULL,
    customer_email TEXT NOT NULL,
    status         TEXT NOT NULL DEFAULT 'pending',
    charge_id      TEXT
);
"""


def connect(path):
    """Open the database at `path` (a file, or ":memory:")."""
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")  # off by default in SQLite
    return connection


def create_schema(connection):
    """Create the tables. Safe to call on a database that already has them."""
    connection.executescript(SCHEMA)
