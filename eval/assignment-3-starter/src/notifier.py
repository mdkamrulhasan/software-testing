"""How students are told the outcome of a registration request.

The service only needs an object with these two methods:

    send_confirmation(student_id, course_code, fee)
    send_rejection(student_id, course_code, reason)

In production that would be an email gateway. serve.py uses
OutboxNotifier, which appends each message as one JSON line to an
"outbox" file -- the system's outgoing mail, which a system test can read
the way a student would read their inbox. In integration tests, use a
test double of your own (see the assignment).
"""

import json
import threading


class OutboxNotifier:
    _lock = threading.Lock()  # several request threads may write at once

    def __init__(self, path):
        self.path = path

    def _write(self, message):
        with self._lock, open(self.path, "a") as outbox:
            outbox.write(json.dumps(message) + "\n")

    def send_confirmation(self, student_id, course_code, fee):
        self._write({"type": "confirmation", "student_id": student_id,
                     "course_code": course_code, "fee": fee})

    def send_rejection(self, student_id, course_code, reason):
        self._write({"type": "rejection", "student_id": student_id,
                     "course_code": course_code, "reason": reason})
