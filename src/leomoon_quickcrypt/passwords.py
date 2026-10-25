"""Password-generation helpers."""

from __future__ import annotations

import secrets


PASSWORD_PUSHER_CHARACTERS = "!#%+23456789:=?@ABCDEFGHJKLMNPRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
UPPERCASE_CHARACTERS = "ABCDEFGHIJLKMNOPQRSTUVWXYZ"
LOWERCASE_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
NUMBER_CHARACTERS = "01234567890"
SPECIAL_CHARACTERS = "`~@#$%^&*()_+-=[]\\{|}\"',.<>/?"


def generate_password(
    length: int,
    *,
    password_pusher: bool = False,
    uppercase: bool = False,
    lowercase: bool = False,
    numbers: bool = False,
    special: bool = False,
) -> str:
    """Generate a password from the selected character sets."""
    if length < 1:
        raise ValueError("Password length must be at least one character.")
    if password_pusher:
        characters = PASSWORD_PUSHER_CHARACTERS
    else:
        characters = "".join(
            character_set
            for enabled, character_set in (
                (uppercase, UPPERCASE_CHARACTERS),
                (lowercase, LOWERCASE_CHARACTERS),
                (numbers, NUMBER_CHARACTERS),
                (special, SPECIAL_CHARACTERS),
            )
            if enabled
        )
    if not characters:
        raise ValueError("Select at least one character set.")
    return "".join(secrets.choice(characters) for _ in range(length))
