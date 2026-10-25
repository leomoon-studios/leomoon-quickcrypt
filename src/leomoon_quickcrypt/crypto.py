"""Safe file operations for the legacy AES Crypt version 2 implementation."""

from __future__ import annotations

import os
import tempfile
from collections.abc import Callable
from pathlib import Path

import pyAesCrypt
from .paths import available_destination, existing_file


BUFFER_SIZE = 64 * 1024


def encrypted_output_path(source: Path) -> Path:
    """Return the conventional AES Crypt output path for *source*."""
    return source.with_name(f"{source.name}.aes")


def decrypted_output_path(source: Path) -> Path:
    """Return the plaintext path for a conventional AES Crypt file."""
    if source.suffix.lower() != ".aes" or source.name.lower() == ".aes":
        raise ValueError("Encrypted files must use the .aes suffix.")
    return source.with_suffix("")


def _atomic_transform(
    source: Path,
    destination: Path,
    transform: Callable[[object, object], None],
) -> Path:
    """Write through a temporary sibling and publish only after success."""
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with source.open("rb") as input_file, os.fdopen(descriptor, "wb") as output_file:
            transform(input_file, output_file)
            output_file.flush()
            os.fsync(output_file.fileno())
        os.replace(temporary_path, destination)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
    return destination


def encrypt_file(source: Path | str, password: str) -> Path:
    """Encrypt *source* into a new ``.aes`` file without overwriting output."""
    input_path = existing_file(source)
    if not password:
        raise ValueError("Password can not be empty!")
    output_path = available_destination(encrypted_output_path(input_path))
    return _atomic_transform(
        input_path,
        output_path,
        lambda input_file, output_file: pyAesCrypt.encryptStream(
            input_file, output_file, password, BUFFER_SIZE
        ),
    )


def decrypt_file(source: Path | str, password: str) -> Path:
    """Decrypt an AES Crypt version 2 file without overwriting plaintext."""
    input_path = existing_file(source)
    if not password:
        raise ValueError("Password can not be empty!")
    output_path = available_destination(decrypted_output_path(input_path))
    return _atomic_transform(
        input_path,
        output_path,
        lambda input_file, output_file: pyAesCrypt.decryptStream(
            input_file, output_file, password, BUFFER_SIZE
        ),
    )


def delete_source_after_success(source: Path | str, requested: bool) -> None:
    """Delete the source only after a caller has completed an operation."""
    if requested:
        Path(source).unlink()
