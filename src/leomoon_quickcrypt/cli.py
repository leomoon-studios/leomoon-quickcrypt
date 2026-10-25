"""Command-line parsing for LeoMoon QuickCrypt."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .version import __version__


def parse_arguments(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse QuickCrypt's GUI and Windows context-menu arguments."""
    parser = argparse.ArgumentParser(prog="leomoon-quickcrypt")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-e", "--encrypt", metavar="FILE", type=Path)
    mode.add_argument("-d", "--decrypt", metavar="FILE", type=Path)
    parser.add_argument("--version", action="version", version=__version__)
    return parser.parse_args(arguments)
