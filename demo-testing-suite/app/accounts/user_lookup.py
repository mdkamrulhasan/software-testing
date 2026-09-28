"""Callers that use their dependencies through Python's special operations.

These are the worked examples from the Week 5 reading *Mock vs.
MagicMock in Python*, transcribed so its MagicMock examples can run
against real code instead of a slide. See
tests/accounts/test_user_lookup.py.

Every function here uses a dependency through a *magic method* rather
than an ordinary method call -- len(), indexing, `in`, iteration, or a
`with` block -- which is exactly what a plain Mock cannot stand in for
and a MagicMock can. Contrast with app/accounts/registration_service.py
(Week 4), whose dependencies are used only through ordinary method
calls, so its tests get by with Mock / create_autospec.

Note: as with Week 4's app/orders/order_service.py, the reading's code
samples are a few small, independent functions rather than one class.
read_file() is not really about users; it is kept here because the
reading introduces all of these as one sequence of examples.
"""


def process_users(repository):
    """Return the first user in ``repository``, or "No users" if empty.

    Uses ``len(repository)`` (__len__) and ``repository[0]``
    (__getitem__). Reading: Example 2.
    """
    if len(repository) == 0:
        return "No users"
    first_user = repository[0]
    return first_user


def check_permission(user, permission):
    """Return whether ``permission`` is in ``user.permissions``.

    ``user`` is used only through ordinary attribute access;
    ``user.permissions`` is used with ``in`` (__contains__). Reading:
    Example 3.
    """
    return permission in user.permissions


def get_names(users):
    """Return the "name" of every user in ``users``.

    Uses ``for user in users`` (__iter__). Reading: Example 4.
    """
    return [user["name"] for user in users]


def read_file(file):
    """Return the contents of an already-opened ``file``.

    Uses ``with file as f`` (__enter__ / __exit__); ``f`` is whatever
    __enter__ returns. Reading: Example 5.
    """
    with file as f:
        return f.read()


def get_user_name(connection, user_id):
    """Return the name of the user with ``user_id``.

    ``connection.cursor()`` is an ordinary call, but its result is then
    used as a context manager, so the test double needs a MagicMock
    somewhere in the chain. Reading: Example 6.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT name FROM users WHERE id = %s",
            (user_id,)
        )
        row = cursor.fetchone()
    return row[0]
