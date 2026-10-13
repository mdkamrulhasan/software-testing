"""Password-reset emails, with a seam for the email transport.

This is the running example from the Week 4 reading's "Dependency
Isolation and Seams" section, transcribed here so its
dependency-injection example can be run against real code instead of
just a slide -- the same way Week 3's app/pricing/shipping.py let
students run EP/BVA against a real file.

The reading's "before" version constructs its own smtplib connection
directly inside send_reset_email(): a hard-coded dependency that makes
the method untestable without a real (or realistic fake) mail server.
That version is intentionally not reproduced here as runnable code --
only PasswordResetService, the "after" version, is.

The reading's separate "Test Double Taxonomy" section illustrates the
five doubles with a different running example (an order_service) -- see
app/orders/order_service.py and tests/orders/test_order_service.py for
that. This file's own tests
(tests/notifications/test_password_reset_service.py) stick to proving
the `email_client` seam works and to the "Mocks that lie" pitfall --
plus, since Week 7 (coverage-based testing), SmtpEmailClient's own
behavior, tested against a patched smtplib.
"""


class EmailClient:
    """The interface PasswordResetService depends on.

    Not meant to be instantiated directly -- it exists so
    unittest.mock.create_autospec has a real interface to constrain a
    mock to (see the "mocks that lie" tests), and so SmtpEmailClient has
    something explicit to implement.
    """

    def send(self, to, message):
        # Excluded on purpose (Week 7 reading, "Exclude sparingly and
        # visibly"): an abstract method has no behavior to test, and every
        # real client overrides it.
        raise NotImplementedError  # pragma: no cover


class SmtpEmailClient(EmailClient):
    """The real, production implementation -- wraps smtplib.

    Never sent through a real mail server by any test in this suite:
    that would need a real (or realistic fake) server, which is exactly
    the problem dependency injection and test doubles solve. See the
    Week 4 reading's "Dependency Isolation and Seams" section.

    Until Week 7 this class was simply left uncovered (63% for the
    file). The Week 7 coverage report turned that gap into a question
    about behavior -- does the connection get closed even when sending
    fails? -- which a test can answer by patching smtplib.SMTP, with no
    server at all. See tests/notifications/test_password_reset_service.py.
    """

    def __init__(self, host="smtp.example.com"):
        self._host = host

    def send(self, to, message):
        import smtplib

        server = smtplib.SMTP(self._host)
        try:
            server.sendmail("noreply@example.com", to, message)
        finally:
            server.quit()


class PasswordResetService:
    """Builds a password-reset email and hands it to an injected email client.

    `email_client` is the seam: production code supplies a real
    SmtpEmailClient; a test can supply any object with a
    `.send(to, message)` method -- see
    tests/notifications/test_password_reset_service.py. `logger` is
    accepted but never called by send_reset_email.
    """

    def __init__(self, email_client, logger):
        self.email_client = email_client
        self.logger = logger

    def send_reset_email(self, user_email, reset_token):
        message = f"Subject: Password Reset\n\nYour reset code is {reset_token}"
        self.email_client.send(user_email, message)
