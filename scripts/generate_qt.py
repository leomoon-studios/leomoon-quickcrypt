#!/usr/bin/env python3
"""Regenerate the PySide6 modules from the tracked Qt Designer source files."""

from __future__ import annotations

import os
import subprocess
import sysconfig
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
UI_DIRECTORY = PROJECT_ROOT / "src" / "gui"


def pyside_tool(name: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    executable = Path(sysconfig.get_path("scripts")) / f"{name}{suffix}"
    if not executable.is_file():
        raise FileNotFoundError(
            f"{executable} was not found. Install PySide6 in the active Python environment."
        )
    return executable


def run(*command: Path | str) -> None:
    subprocess.run([str(part) for part in command], check=True, cwd=PROJECT_ROOT)


def normalize_trailing_newline(path: Path) -> None:
    path.write_text(path.read_text(encoding="utf-8").rstrip() + "\n", encoding="utf-8")


def main() -> None:
    run(
        pyside_tool("pyside6-rcc"),
        UI_DIRECTORY / "resources.qrc",
        "-o",
        UI_DIRECTORY / "resources_rc.py",
    )
    run(
        pyside_tool("pyside6-uic"),
        "--from-imports",
        UI_DIRECTORY / "guiMain.ui",
        "-o",
        UI_DIRECTORY / "guiMain.py",
    )
    normalize_trailing_newline(UI_DIRECTORY / "guiMain.py")
    normalize_trailing_newline(UI_DIRECTORY / "resources_rc.py")


if __name__ == "__main__":
    main()
