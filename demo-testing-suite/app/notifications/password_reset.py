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
the `email_client` seam works and to the "Mocks that lie" pitfall.
"""


class EmailClient:
    """The interface PasswordResetService depends on.

    Not meant to be instantiated directly -- it exists so
    unittest.mock.create_autospec has a real interface to constrain a
    mock to (see the "mocks that lie" tests), and so SmtpEmailClient has
    something explicit to implement.
    """

    def send(self, to, message):
        raise NotImplementedError


class SmtpEmailClient(EmailClient):
    """The real, production implementation -- wraps smtplib.

    Deliberately not exercised by any test in this suite: testing it for
    real would require a real (or realistic fake) mail server, which is
    exactly the problem dependency injection and test doubles solve. See
    the reading's "Dependency Isolation and Seams" section.
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
