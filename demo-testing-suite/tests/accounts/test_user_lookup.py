"""Mock vs. MagicMock -- the Week 5 reading's worked examples, runnable.

Each test below fakes a dependency that the code under test uses
through a *magic method* (len, indexing, `in`, iteration, `with`), so a
MagicMock is the natural double. Where the code only uses ordinary
attribute access or method calls, a plain Mock is kept on purpose --
per the reading, the choice is made per object, not per test.

The first two tests show why: a plain Mock raises TypeError on len()
unless the magic method is attached by hand, which is exactly what
MagicMock does for you.

Contrast with tests/accounts/test_registration_service.py (Week 4),
whose dependencies are only ever used through ordinary method calls.
"""

from unittest.mock import MagicMock, Mock

import pytest

from app.accounts.user_lookup import (
    check_permission,
    get_names,
    get_user_name,
    process_users,
    read_file,
)


# --- Why MagicMock exists ----------------------------------------------------


def test_plain_mock_raises_type_error_on_len():
    """Reading: "A Comparable Example" -- a plain Mock passed to a
    function that calls len() fails immediately."""
    with pytest.raises(TypeError):
        process_users(Mock())


def test_plain_mock_works_once_the_magic_method_is_attached_by_hand():
    """Reading: the footnote to the core-difference table. MagicMock
    simply does this configuration for you."""
    repository = Mock()
    repository.__len__ = Mock(return_value=0)

    assert process_users(repository) == "No users"


# --- Example 2: len() and indexing ------------------------------------------


def test_process_users_returns_the_first_user():
    repository = MagicMock()
    repository.__len__.return_value = 10
    repository.__getitem__.return_value = {"id": 1, "name": "Alice"}

    assert process_users(repository) == {"id": 1, "name": "Alice"}
    repository.__getitem__.assert_called_once_with(0)


def test_process_users_never_indexes_an_empty_repository():
    """Reading: the Example 2 tip box -- magic methods on a MagicMock
    are mocks themselves, so they support call assertions too."""
    repository = MagicMock()
    repository.__len__.return_value = 0

    assert process_users(repository) == "No users"
    repository.__getitem__.assert_not_called()


# --- Example 3: the `in` operator -------------------------------------------


def test_check_permission_mixes_mock_and_magicmock():
    user = Mock()  # only attribute access -> Mock is enough
    user.permissions = MagicMock()  # used with `in` -> needs __contains__
    user.permissions.__contains__.return_value = True

    assert check_permission(user, "admin") is True
    user.permissions.__contains__.assert_called_once_with("admin")


# --- Example 4: iteration ---------------------------------------------------


def test_get_names_iterates_over_the_configured_users():
    users = MagicMock()
    users.__iter__.return_value = [
        {"name": "Alice"},
        {"name": "Bob"},
        {"name": "Charlie"},
    ]

    assert get_names(users) == ["Alice", "Bob", "Charlie"]


def test_list_return_value_survives_iterating_twice():
    """Reading: the Example 4 pitfall box, safe version. A list gives
    MagicMock a fresh iterator on every loop."""
    users = MagicMock()
    users.__iter__.return_value = [{"name": "Alice"}]

    assert get_names(users) == ["Alice"]
    assert get_names(users) == ["Alice"]


def test_iter_return_value_is_silently_empty_the_second_time():
    """Reading: the Example 4 pitfall box, unsafe version. This test
    PASSES -- that is the pitfall. An iterator can only be consumed
    once, so the second loop quietly sees nothing instead of failing."""
    users = MagicMock()
    users.__iter__.return_value = iter([{"name": "Alice"}])

    assert get_names(users) == ["Alice"]
    assert get_names(users) == []  # silently empty, not an error


# --- Example 5: context managers --------------------------------------------


def test_read_file_uses_the_object_returned_by_enter():
    file = MagicMock()
    file.__enter__.return_value.read.return_value = "Hello World"

    assert read_file(file) == "Hello World"
    file.__enter__.assert_called_once()
    file.__exit__.assert_called_once()


# --- Example 6: database connection -----------------------------------------


def test_get_user_name_queries_through_the_cursor():
    connection = MagicMock()
    cursor = connection.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = ("Alice",)

    assert get_user_name(connection, 1) == "Alice"
    cursor.execute.assert_called_once_with(
        "SELECT name FROM users WHERE id = %s",
        (1,)
    )
