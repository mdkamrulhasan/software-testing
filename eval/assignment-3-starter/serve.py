"""Run the course registration system as one process.

    python serve.py                     # on http://127.0.0.1:8000
    python serve.py --port 0            # any free port (the system tests do this)
    python serve.py --db reg.db         # keep the database between runs
    python serve.py --outbox out.jsonl  # where student notifications are written

When the server is listening it prints one line,

    READY url=http://127.0.0.1:8000 outbox=/path/to/outbox.jsonl

which is what tests/system/conftest.py waits for. A new database is
created and seeded with the catalog in SPEC.md; an existing one is used
as it is. Every request except GET /health needs the header
X-API-Key: registrar-key. Stop with Ctrl-C.
"""

import argparse
import logging
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from werkzeug.serving import make_server  # noqa: E402

import db  # noqa: E402
from api import create_app  # noqa: E402
from notifier import OutboxNotifier  # noqa: E402
from repository import RegistrationRepository  # noqa: E402
from service import RegistrationService  # noqa: E402

API_KEY = "registrar-key"


def prepare_database(path):
    """Create the schema; seed it only if it has no courses yet."""
    connection = db.connect(path)
    try:
        db.create_schema(connection)
        if connection.execute("SELECT COUNT(*) FROM courses").fetchone()[0] == 0:
            db.seed(connection)
    finally:
        connection.close()


class PerRequestService:
    """sqlite3 connections belong to one thread, and the server handles
    each request on its own thread: every call opens a connection, runs
    the real service on it, and closes it."""

    def __init__(self, db_path, notifier):
        self.db_path = db_path
        self.notifier = notifier

    def __getattr__(self, method):
        def call(*args):
            connection = db.connect(self.db_path)
            try:
                service = RegistrationService(
                    connection, RegistrationRepository(connection), self.notifier)
                return getattr(service, method)(*args)
            finally:
                connection.close()
        return call


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--db", help="database file (default: a new temporary one)")
    parser.add_argument("--outbox", help="notification file (default: a new temporary one)")
    args = parser.parse_args()
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    workdir = Path(tempfile.mkdtemp())
    db_path = Path(args.db) if args.db else workdir / "registration.db"
    outbox = Path(args.outbox) if args.outbox else workdir / "outbox.jsonl"
    outbox.touch()
    prepare_database(db_path)

    app = create_app(PerRequestService(db_path, OutboxNotifier(outbox)), API_KEY)
    server = make_server("127.0.0.1", args.port, app, threaded=True)
    print(f"READY url=http://127.0.0.1:{server.port} outbox={outbox}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
