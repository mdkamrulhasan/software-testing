"""PROVIDED -- the system test harness. You do not need to change it.

The `system` fixture starts serve.py as a separate process, with a new
database and outbox in pytest's tmp_path, waits for its READY line, and
stops it when the test ends. Your system tests talk to it only over HTTP:

    def test_something(system):
        response = system.enroll("S01", "SE413")       # POST /enrollments
        assert response.status_code == 201
        system.get("/students/S01/schedule")           # any GET, with the API key
        system.delete("/enrollments/S01/SE413")
        system.outbox()                                # notifications sent so far
        system.url                                     # for requests you build yourself

Each test gets its own server and data, seeded as in SPEC.md, so tests
can run in any order. If the server fails to start, the failure message
includes its log.
"""

import json
import queue
import subprocess
import sys
import threading
from pathlib import Path

import pytest
import requests

PROJECT_ROOT = Path(__file__).resolve().parents[2]
API_KEY = "registrar-key"


class RunningSystem:
    def __init__(self, process, url, outbox_path):
        self.process = process
        self.url = url
        self.outbox_path = Path(outbox_path)
        self.http = requests.Session()
        self.http.headers["X-API-Key"] = API_KEY

    def enroll(self, student_id, course_code):
        return self.http.post(f"{self.url}/enrollments", timeout=10,
                              json={"student_id": student_id, "course_code": course_code})

    def get(self, path, **kwargs):
        return self.http.get(self.url + path, timeout=10, **kwargs)

    def delete(self, path, **kwargs):
        return self.http.delete(self.url + path, timeout=10, **kwargs)

    def outbox(self):
        """Every notification the system has sent, oldest first."""
        lines = self.outbox_path.read_text().splitlines()
        return [json.loads(line) for line in lines if line.strip()]


@pytest.fixture
def system(tmp_path):
    log_path = tmp_path / "server.log"
    with open(log_path, "w") as log:
        process = subprocess.Popen(
            [sys.executable, "serve.py", "--port", "0",
             "--db", str(tmp_path / "registration.db"),
             "--outbox", str(tmp_path / "outbox.jsonl")],
            cwd=PROJECT_ROOT, stdout=subprocess.PIPE, stderr=log, text=True)
    lines = queue.Queue()
    threading.Thread(target=lambda: lines.put(process.stdout.readline()),
                     daemon=True).start()
    try:
        line = lines.get(timeout=10)
    except queue.Empty:
        line = ""
    if not line.startswith("READY"):
        process.kill()
        pytest.fail(f"serve.py did not start:\n{log_path.read_text()}")
    fields = dict(part.split("=", 1) for part in line.split()[1:])
    running = RunningSystem(process, fields["url"], fields["outbox"])
    yield running
    running.http.close()
    process.terminate()
    process.wait(timeout=5)
