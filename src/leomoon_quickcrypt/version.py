"""Package version helpers."""

from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("leomoon-quickcrypt")
except PackageNotFoundError:
    __version__ = "0.0.0+unknown"
