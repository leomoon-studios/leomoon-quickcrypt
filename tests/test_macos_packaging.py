from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INFO_PLIST = PROJECT_ROOT / "packaging" / "macos" / "Info.plist.in"
PACKAGE_SCRIPT = PROJECT_ROOT / "scripts" / "package-macos.sh"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify-macos-package.sh"
SMOKE_SCRIPT = PROJECT_ROOT / "scripts" / "smoke-macos-dmg.sh"


def test_macos_info_plist_declares_arm64_application_and_aes_document_type() -> None:
    info_plist = INFO_PLIST.read_text(encoding="utf-8")

    assert "com.leomoon.QuickCrypt" in info_plist
    assert "LeoMoon QuickCrypt" in info_plist
    assert "LSMinimumSystemVersion</key><string>12.0" in info_plist
    assert "CFBundleTypeExtensions</key><array><string>aes</string>" in info_plist
    assert "@VERSION@" in info_plist


def test_macos_packaging_is_arm64_only_and_uses_standard_dmg_presentation() -> None:
    package_script = PACKAGE_SCRIPT.read_text(encoding="utf-8")
    verifier = VERIFY_SCRIPT.read_text(encoding="utf-8")

    assert '"$architecture" == arm64' in package_script
    assert "hdiutil create" in package_script
    assert "custom installer" not in package_script.lower()
    assert "lipo -archs" in verifier
    assert "non-ARM64 Mach-O payload" in verifier


def test_macos_smoke_checks_checksums_quarantine_and_arguments() -> None:
    smoke_script = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "shasum -a 256 -c SHA256SUMS" in smoke_script
    assert "com.apple.quarantine" in smoke_script
    assert '"$copied_app/Contents/MacOS/LeoMoon QuickCrypt" --version' in smoke_script
    assert '"$copied_app/Contents/MacOS/LeoMoon QuickCrypt" "$mode" "$target"' in smoke_script
