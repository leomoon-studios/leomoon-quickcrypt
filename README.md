# LeoMoon QuickCrypt

## Introduction

LeoMoon QuickCrypt is a desktop file-encryption application and password generator. It uses the AES Crypt version 2 file format through pyAesCrypt, with AES-256-CBC encryption, to create encrypted files that can be opened on Windows, Linux, and macOS.

The application is being modernized as a cross-platform Python and Qt 6 project. It supports Windows, macOS, and Linux with a shared codebase and native release packages for each platform.

## Features

- Encrypt and decrypt files in the AES Crypt version 2 format.
- Drag a file into the window or choose one with the file picker.
- Optionally remove the original file after a successful encryption or decryption.
- Generate passwords with configurable length, letter case, numbers, and special characters.
- Light and dark themes that follow the operating system preference, with `Ctrl+M` to toggle the theme.
- Windows Explorer context-menu actions for encryption and decryption.
- Bundled Vazir fonts and a native application icon.

## Usage

1. Download the package for your computer from the [GitHub releases page](https://github.com/leomoon-studios/leomoon-quickcrypt/releases). Windows provides x64 and ARM64 installers, Linux provides x86_64 and ARM64 AppImages, and macOS provides an ARM64 DMG.
2. Open LeoMoon QuickCrypt and select the **Encrypt** or **Decrypt** tab.
3. Choose or drag in a file, enter its password, then select **Encrypt** or **Decrypt**.
4. Use the **Password Generator** tab when you need a new password. Store the password safely: encrypted files cannot be recovered without it.

On Windows, the installer also adds **Encrypt with LeoMoon QuickCrypt** and **Decrypt with LeoMoon QuickCrypt** to the Explorer context menu for files.

## Security

QuickCrypt uses pyAesCrypt's AES Crypt version 2 implementation with AES-256-CBC encryption. Use a long, unique password and keep it in a password manager. Encryption does not make a weak or reused password safe, and forgotten passwords cannot be reset or recovered.

## Build

Requirements:

- Python 3.12 or newer
- A project-local `.venv`
- `uv` installed only inside that `.venv`

From the repository root:

```sh
python -m venv .venv
.venv/bin/python -m pip install "uv==0.13.5"
.venv/bin/uv sync --all-extras --locked
.venv/bin/python scripts/generate_qt.py
QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME=none .venv/bin/python -m pytest -q
```

Run the application during development with:

```sh
.venv/bin/python -m leomoon_quickcrypt
```

On Windows, use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.

## Packaging

Release packages are platform-specific: Windows uses x64 and ARM64 Inno Setup installers, Linux uses x86_64 and ARM64 AppImages, and macOS uses one native ARM64 DMG. Each package is built from the same PyInstaller one-directory application and includes release metadata and SHA-256 checksums.

The platform workflows install the locked dependencies in a project-local `.venv`, regenerate the Qt sources, run Ruff and pytest, build the native bundle, then package and smoke-test the final artifact. Linux AppImage tooling is downloaded with pinned SHA-256 checksums.

## Release builds

Use the **Release** GitHub Actions workflow for a non-publishing platform test. Pushing a `vMAJOR.MINOR.PATCH` tag builds the five packages, verifies their checksums and smoke tests, creates a GitHub release, and adds release notes with linked commits and contributors.

The application executable is named `LeoMoon QuickCrypt`. Release asset filenames use the stable `leomoon-quickcrypt` slug. Do not commit package outputs, virtual environments, certificates, private keys, tokens, or other signing credentials.

## Remove

Use the normal uninstall method for the installed package. Windows users can remove the Explorer context-menu entries by uninstalling LeoMoon QuickCrypt.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history.

## Third-party notices

The application includes Qt for Python, DarkDetect, pyAesCrypt, Cryptography, Vazir fonts, and icon assets. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for their notices and licenses.
