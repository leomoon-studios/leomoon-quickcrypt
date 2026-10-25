from __future__ import annotations

from pathlib import Path

import pytest

from leomoon_quickcrypt.cli import parse_arguments
from leomoon_quickcrypt.version import __version__


def test_encrypt_and_decrypt_arguments_preserve_unicode_paths() -> None:
    source = Path("نمونه input.txt")

    assert parse_arguments(["-e", str(source)]).encrypt == source
    assert parse_arguments(["-d", str(source)]).decrypt == source


def test_version_argument_exits_successfully(capsys) -> None:
    with pytest.raises(SystemExit) as result:
        parse_arguments(["--version"])

    assert result.value.code == 0
    assert capsys.readouterr().out.strip() == __version__
