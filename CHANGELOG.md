# Changelog

## 3.0.0 2026-10-24

- Modernized the application around Python 3.12, PySide6, and a standard `src` package layout.
- Replaced unmaintained and vendored dependencies with maintained, locked PyPI packages.
- Added regression tests, Ruff checks, dependency auditing, and reproducible project-local `.venv` builds with uv.
- Strengthened encryption and decryption file handling, including safe replacement and source-file deletion only after a successful operation.
- Added deterministic PyInstaller bundles and native packaging for Windows x64 and ARM64, Linux x86_64 and ARM64 AppImages, and macOS ARM64 DMG releases.
- Added GitHub Actions platform builds and tag-based GitHub releases with SHA-256 checksums, linked commits, and contributor profiles.
- Removed obsolete build scripts, old installers, and bundled runtime artifacts.
- Fixed deterministic Qt generation checks so release runners do not reject timestamp-only resource changes.
- Fixed macOS application-bundle staging to match the maintained SubFix packaging flow.
- Fixed Windows Qt drag-and-drop path assertions across native path separators.
- Fixed native Windows ARM64 Cryptography source builds by using the MSVC ARM64 linker and ARM64 OpenSSL dependencies.

## 2.0.8 2021-10-05

- Added cross-platform automatic dark mode.
- Added `Ctrl+M` to toggle dark mode.
- Updated dependencies.

## 2.0.7 2020-12-19

- Fixed compatibility with macOS Big Sur.
- Changed the minimum supported macOS version to 10.14 Mojave.
- Fixed the uninstall icon for the Windows setup package.
- Updated dependencies.

## 2.0.6 2020-11-16

- Minor improvements.
- Small bug fixes.

## 2.0.5 2020-05-20

- Fixed a crash caused by Windows 10 update 1909.
- Updated dependencies.

## 2.0.4

- Crash fix.

## 2.0.3

- Optimized the encryption algorithm.
- Updated the core and dependencies.
- Embedded the main font in the application.
- Converted the main logo and banner to SVG.
- Fixed occasional DPI-scaling issues.
- Changed the minimum supported macOS version to 10.13.

## 2.0.2

- Minor changes.
- Digitally signed the Windows binary.

## 2.0.1

- Minor user-interface changes.

## 2.0.0

- Rewrote QuickCrypt to support macOS.

## 1.22

- Minor changes.

## 1.0

- Initial release.
