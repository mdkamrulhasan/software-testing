"""PROVIDED -- the test harness shared by tests/system/ and tests/acceptance/.
You do not need to change it.

`start_system()` starts serve.py as a separate process, with a new
database and outbox in pytest's tmp_path, waits for its READY line, and
stops it when the test ends. Tests talk to it only over HTTP:

    def test_something(start_system):
        system = start_system()
        system.enroll("S01", "SE413")                   # POST /enrollments
        system.join_waitlist("S04", "SE499")            # POST /waitlist
        system.withdraw("S01", "SE499")                 # DELETE /enrollments/S01/SE499
        system.leave_waitlist("S04", "SE499")           # DELETE /waitlist/S04/SE499
        system.get("/students/S01/schedule")            # any GET, with the API key
        system.post(path, json=...), system.delete(path) # anything else
        system.outbox()                                 # notifications sent so far
        system.restart()                                # stop, start again on the same data
        system.url                                      # for requests you build yourself

The `system` fixture is `start_system()` already called. Each test gets
its own server and data, seeded as in SPEC.md, so tests can run in any
order. If the server fails to start, the failure message includes its log.
"""

import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
API_KEY = "registrar-key"


class RunningSystem:
    def __init__(self, workdir):
        self.workdir = Path(workdir)
        self.db_path = self.workdir / "registration.db"
        self.outbox_path = self.workdir / "outbox.jsonl"
        self.log_path = self.workdir / "server.log"
        self.process = None
        self.url = None
        self.http = requests.Session()
        self.http.headers["X-API-Key"] = API_KEY

    # -- process control -----------------------------------------------------
    def start(self):
        with open(self.log_path, "a") as log:
            self.process = subprocess.Popen(
                [sys.executable, "serve.py", "--port", "0",
                 "--db", str(self.db_path), "--outbox", str(self.outbox_path)],
                cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=log, text=True)
        lines = queue.Queue()
        threading.Thread(target=lambda: lines.put(self.process.stdout.readline()),
                         daemon=True).start()
        try:
            line = lines.get(timeout=10)
        except queue.Empty:
            line = ""
        if not line.startswith("READY"):
            self.process.kill()
            pytest.fail(f"serve.py did not start:\n{self.log_path.read_text()}")
        fields = dict(part.split("=", 1) for part in line.split()[1:])
        self.url = fields["url"]
        return self

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process.wait(timeout=5)

    def restart(self):
        """Stop the server and start it again on the same database and
        outbox (what an operator does after a deployment or a crash)."""
        self.stop()
        return self.start()

    # -- HTTP --------------------------------------------------------------------
    def get(self, path, **kwargs):
        return self.http.get(self.url + path, timeout=10, **kwargs)

    def post(self, path, **kwargs):
        return self.http.post(self.url + path, timeout=10, **kwargs)

    def delete(self, path, **kwargs):
        return self.http.delete(self.url + path, timeout=10, **kwargs)

    def enroll(self, student_id, course_code):
        return self.post("/enrollments",
                         json={"student_id": student_id, "course_code": course_code})

    def withdraw(self, student_id, course_code):
        return self.delete(f"/enrollments/{student_id}/{course_code}")

    def join_waitlist(self, student_id, course_code):
        return self.post("/waitlist",
                         json={"student_id": student_id, "course_code": course_code})

    def leave_waitlist(self, student_id, course_code):
        return self.delete(f"/waitlist/{student_id}/{course_code}")

    # -- the outbox --------------------------------------------------------------
    def outbox(self):
        """Every notification the system has sent, oldest first."""
        lines = self.outbox_path.read_text().splitlines()
        return [json.loads(line) for line in lines if line.strip()]


@pytest.fixture
def start_system(tmp_path):
    started = []

    def start():
        workdir = tmp_path / f"system{len(started)}"
        workdir.mkdir()
        running = RunningSystem(workdir).start()
        started.append(running)
        return running

    yield start
    for running in started:
        running.http.close()
        running.stop()


@pytest.fixture
def system(start_system):
    return start_system()
