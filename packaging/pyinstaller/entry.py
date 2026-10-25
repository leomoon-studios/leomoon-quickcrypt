"""PyInstaller entry point that preserves the application package context."""

from leomoon_quickcrypt.app import main


if __name__ == "__main__":
    raise SystemExit(main())
