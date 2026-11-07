"""Fixtures for your integration tests (Section 4 of the assignment).

Your integration tests assemble the REAL repository and service on a
REAL SQLite database file -- inside the test process. Suggested fixtures
(write them here):

  - a connection to a new database file in pytest's `tmp_path`, with
    db.create_schema() applied and a few students and courses added
    through the repository (or with db.seed());
  - a RegistrationRepository on that connection;
  - a fake notifier: a small class of your own that records every
    send_confirmation / send_rejection call in a list, so a test can
    check what was sent;
  - a RegistrationService built from the three.
"""

# TODO: implement your fixtures here.
