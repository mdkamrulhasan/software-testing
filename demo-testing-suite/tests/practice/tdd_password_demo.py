"""
Test-Driven Development (TDD) Demo: Strong Password Validation

This example walks through the RED-GREEN-REFACTOR cycle.
The test and implementation snippets are kept as comments to illustrate
how the solution evolves at each cycle.
"""

# ---------------------------------------------------------------------
# Cycle 1: RED
# Write a test for a password we know should be rejected.
# ---------------------------------------------------------------------
def test_rejects_short_password():
    assert is_strong_password("Ab1") is False


# Fake implementation
def is_strong_password(password):
    return False


# ---------------------------------------------------------------------
# Cycle 2: RED
# Write a test for a password we know should be accepted, forcing
# the fake implementation to break.
# ---------------------------------------------------------------------
# def test_accepts_long_password_with_digit_and_uppercase():
#     assert is_strong_password("Abcdefg1") is True


# ---------------------------------------------------------------------
# Cycle 2: GREEN
# This test now fails against `return False`, forcing real logic.
# ---------------------------------------------------------------------
# def is_strong_password(password):
#     if len(password) < 8:
#         return False
#     return True


# ---------------------------------------------------------------------
# Cycle 3: RED
# This passes both prior tests, but nothing yet checks the digit rule.
# ---------------------------------------------------------------------
# def test_rejects_password_without_digit():
#     assert is_strong_password("Abcdefgh") is False


# ---------------------------------------------------------------------
# Cycle 3: GREEN
# Fix the function to enforce the digit requirement.
# ---------------------------------------------------------------------
# def is_strong_password(password):
#     if len(password) < 8:
#         return False
#     if not any(char.isdigit() for char in password):
#         return False
#     return True


# ---------------------------------------------------------------------
# Cycle 4: RED
# Nothing yet checks the uppercase requirement.
# ---------------------------------------------------------------------
# def test_rejects_password_without_uppercase():
#     assert is_strong_password("abcdefg1") is False


# ---------------------------------------------------------------------
# Cycle 4: GREEN
# Add the uppercase requirement.
# ---------------------------------------------------------------------
# def is_strong_password(password):
#     if len(password) < 8:
#         return False
#     if not any(char.isdigit() for char in password):
#         return False
#     if not any(char.isupper() for char in password):
#         return False
#     return True


# # ---------------------------------------------------------------------
# # Refactor
# # All four tests pass. Now clean up the implementation.
# # ---------------------------------------------------------------------
# def is_strong_password(password):
#     """Return True when password meets the demo's three strength rules."""
#     rules_satisfied = [
#         len(password) >= 8,
#         any(char.isdigit() for char in password),
#         any(char.isupper() for char in password),
#     ]
#     return all(rules_satisfied)


# # Final tests (uncomment/run with pytest)
# def test_rejects_short_password():
#     assert is_strong_password("Ab1") is False


# def test_accepts_long_password_with_digit_and_uppercase():
#     assert is_strong_password("Abcdefg1") is True


# def test_rejects_password_without_digit():
#     assert is_strong_password("Abcdefgh") is False


# def test_rejects_password_without_uppercase():
#     assert is_strong_password("abcdefg1") is False
