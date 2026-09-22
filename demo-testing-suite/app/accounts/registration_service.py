"""Registers a new user, then welcomes them by email.

Ties two Week 4 seams together in one class:
  - `user_repository`: lets tests mock UserRepository directly instead
    of a real sqlite3 connection -- exactly the use case
    app/accounts/user_repository.py's own docstring anticipated back in
    Week 2 ("A mocking lecture can mock UserRepository instead of
    sqlite3 itself.").
  - `email_client`: the same seam as PasswordResetService in
    app/notifications/password_reset.py.

See tests/accounts/test_registration_service.py.
"""


class UserRegistrationService:
    def __init__(self, user_repository, email_client):
        self.user_repository = user_repository
        self.email_client = email_client

    def register(self, name, email):
        """Register `name`, welcome them by email, and return their new id.

        Raises:
            ValueError: If a user named `name` already exists.
        """
        if self.user_repository.get_user_by_name(name) is not None:
            raise ValueError(f"user '{name}' already exists")

        user_id = self.user_repository.insert_user(name)
        self.email_client.send(email, f"Welcome, {name}!")
        return user_id
