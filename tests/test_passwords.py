from __future__ import annotations

from itertools import product

import pytest

from leomoon_quickcrypt.passwords import (
    LOWERCASE_CHARACTERS,
    NUMBER_CHARACTERS,
    PASSWORD_PUSHER_CHARACTERS,
    SPECIAL_CHARACTERS,
    UPPERCASE_CHARACTERS,
    generate_password,
)


@pytest.mark.parametrize("uppercase,lowercase,numbers,special", list(product([False, True], repeat=4)))
def test_every_non_empty_character_set_combination_and_requested_length(
    uppercase: bool, lowercase: bool, numbers: bool, special: bool
) -> None:
    if not any((uppercase, lowercase, numbers, special)):
        pytest.skip("The empty selection is tested separately.")
    selection = {
        "uppercase": uppercase,
        "lowercase": lowercase,
        "numbers": numbers,
        "special": special,
    }
    allowed = "".join(
        character_set
        for enabled, character_set in (
            (uppercase, UPPERCASE_CHARACTERS),
            (lowercase, LOWERCASE_CHARACTERS),
            (numbers, NUMBER_CHARACTERS),
            (special, SPECIAL_CHARACTERS),
        )
        if enabled
    )
    password = generate_password(96, **selection)

    assert len(password) == 96
    assert set(password) <= set(allowed)


def test_password_pusher_mode_overrides_other_selections() -> None:
    password = generate_password(96, password_pusher=True, uppercase=True, lowercase=True)

    assert len(password) == 96
    assert set(password) <= set(PASSWORD_PUSHER_CHARACTERS)


@pytest.mark.parametrize("length", [0, -1])
def test_invalid_password_length_is_rejected(length: int) -> None:
    with pytest.raises(ValueError, match="length"):
        generate_password(length, lowercase=True)


def test_no_character_set_is_rejected() -> None:
    with pytest.raises(ValueError, match="character set"):
        generate_password(12)
