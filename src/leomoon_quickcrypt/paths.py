"""Path validation shared by QuickCrypt's user interface and file operations."""

from __future__ import annotations

from pathlib import Path


def existing_file(path: Path | str) -> Path:
    """Return a file path or raise a clear error for invalid input."""
    candidate = Path(path)
    if not candidate.exists():
        raise FileNotFoundError("Selected file does not exist.")
    if not candidate.is_file():
        raise IsADirectoryError("Please select a file, not a folder.")
    return candidate


def available_destination(path: Path) -> Path:
    """Return an output path only when it will not overwrite a file."""
    if path.exists():
        raise FileExistsError(f"Destination already exists: {path.name}")
    return path
