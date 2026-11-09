"""Connecting to the registration database, creating its schema, and
seeding it with a small catalog."""

import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS courses (
    code          TEXT PRIMARY KEY,
    title         TEXT NOT NULL,
    credits       INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 4),
    capacity      INTEGER NOT NULL CHECK (capacity >= 0),
    seats_taken   INTEGER NOT NULL DEFAULT 0
                  CHECK (seats_taken >= 0 AND seats_taken <= capacity),
    prerequisite  TEXT REFERENCES courses (code)
);
CREATE TABLE IF NOT EXISTS completed (
    student_id    TEXT NOT NULL REFERENCES students (id),
    course_code   TEXT NOT NULL REFERENCES courses (code),
    PRIMARY KEY (student_id, course_code)
);
CREATE TABLE IF NOT EXISTS enrollments (
    student_id    TEXT NOT NULL REFERENCES students (id),
    course_code   TEXT NOT NULL REFERENCES courses (code),
    PRIMARY KEY (student_id, course_code)
);
"""

# The catalog serve.py starts with (SPEC.md, "Seed data").
DEFAULT_SEED = {
    "courses": [
        # code,    title,                      credits, capacity, prerequisite
        ("CIS350", "Intro to Software Engineering", 4, 40, None),
        ("SE413",  "Software Testing",              3, 30, "CIS350"),
        ("SE499",  "Capstone Seminar",              3, 3,  "CIS350"),
        ("MTH201", "Calculus I",                    4, 40, None),
        ("HIS105", "World History",                 4, 40, None),
        ("PHY230", "Physics I",                     4, 40, None),
        ("CHM110", "Chemistry I",                   4, 40, None),
        ("ENG150", "Academic Writing",              3, 40, None),
        ("ART101", "Drawing Studio",                1, 1,  None),
    ],
    # S01-S12: completed CIS350, enrolled in nothing yet.
    # S13: completed nothing.
    # S14: completed CIS350, already enrolled in 15 credits.
    "students": [(f"S{n:02d}", f"Student {n}") for n in range(1, 15)],
    "completed": [(f"S{n:02d}", "CIS350") for n in range(1, 13)] + [("S14", "CIS350")],
    "enrollments": [("S14", "MTH201"), ("S14", "HIS105"), ("S14", "PHY230"),
                    ("S14", "ENG150")],
}


def connect(path):
    """Open the database at `path` (a file, or ":memory:")."""
    connection = sqlite3.connect(path, timeout=10, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")  # off by default in SQLite
    return connection


def create_schema(connection):
    """Create the tables. Safe to call on a database that already has them."""
    connection.executescript(SCHEMA)


def seed(connection, data=DEFAULT_SEED):
    """Insert `data` (shaped like DEFAULT_SEED) in one transaction."""
    with connection:
        connection.executemany(
            "INSERT INTO courses (code, title, credits, capacity, prerequisite) "
            "VALUES (?, ?, ?, ?, ?)", data["courses"])
        connection.executemany("INSERT INTO students VALUES (?, ?)", data["students"])
        connection.executemany("INSERT INTO completed VALUES (?, ?)", data["completed"])
        for student_id, course_code in data["enrollments"]:
            connection.execute("INSERT INTO enrollments VALUES (?, ?)",
                               (student_id, course_code))
            connection.execute("UPDATE courses SET seats_taken = seats_taken + 1 "
                               "WHERE code = ?", (course_code,))
