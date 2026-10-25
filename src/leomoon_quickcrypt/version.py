"""Runtime access to the package version."""

from __future__ import annotations

import os


_build_version = os.environ.get("LEOMOON_QUICKCRYPT_VERSION")

if _build_version:
    __version__ = _build_version
else:
    try:
        from ._version import __version__
    except ImportError:
        from importlib.metadata import PackageNotFoundError, version

        try:
            __version__ = version("leomoon-quickcrypt")
        except PackageNotFoundError:
            __version__ = "0.0.0+unknown"
