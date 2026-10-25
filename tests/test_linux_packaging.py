from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DESKTOP_FILE = PROJECT_ROOT / "packaging" / "linux" / "com.leomoon.QuickCrypt.desktop"
MIME_FILE = PROJECT_ROOT / "packaging" / "linux" / "mime" / "com.leomoon.QuickCrypt.xml"
PACKAGE_SCRIPT = PROJECT_ROOT / "scripts" / "package-linux.sh"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify-linux-appimage.sh"
SMOKE_SCRIPT = PROJECT_ROOT / "scripts" / "smoke-linux-appimage.sh"


def test_linux_desktop_entry_and_mime_definition_use_stable_metadata() -> None:
    desktop_file = DESKTOP_FILE.read_text(encoding="utf-8")
    mime_file = MIME_FILE.read_text(encoding="utf-8")

    assert "Exec=leomoon-quickcrypt %F" in desktop_file
    assert "Icon=com.leomoon.QuickCrypt" in desktop_file
    assert "MimeType=application/x-aescrypt;" in desktop_file
    assert "Categories=Utility;" in desktop_file
    assert 'glob pattern="*.aes"' in mime_file


def test_linux_packaging_requires_pinned_tooling_and_writes_release_artifacts() -> None:
    package_script = PACKAGE_SCRIPT.read_text(encoding="utf-8")

    assert "--appimagetool-version" in package_script
    assert "--appimagetool-sha256" in package_script
    assert "--runtime-version" in package_script
    assert "--runtime-sha256" in package_script
    assert "Refusing to replace unsafe artifact directory" in package_script
    assert "release-manifest.json" in package_script
    assert "SHA256SUMS" in package_script


def test_linux_appimage_verifier_checks_layout_mime_and_architecture() -> None:
    verifier = VERIFY_SCRIPT.read_text(encoding="utf-8")

    assert "com.leomoon.QuickCrypt.desktop" in verifier
    assert "com.leomoon.QuickCrypt.xml" in verifier
    assert "LeoMoon QuickCrypt" in verifier
    assert "Unexpected architecture" in verifier


def test_linux_appimage_smoke_uses_only_the_appimage_and_argument_paths() -> None:
    smoke_script = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "env -i" in smoke_script
    assert '"$appimage" --version' in smoke_script
    assert '"$appimage" "$mode" "$target"' in smoke_script
