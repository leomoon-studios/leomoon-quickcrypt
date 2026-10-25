from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
INSTALLER = PROJECT_ROOT / "packaging" / "windows" / "quickcrypt.iss"
PACKAGE_SCRIPT = PROJECT_ROOT / "scripts" / "package-windows.ps1"
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify-windows-package.ps1"
SMOKE_SCRIPT = PROJECT_ROOT / "scripts" / "smoke-windows-installer.ps1"


def test_windows_installer_uses_native_application_closing_and_default_setup_icon() -> None:
    installer = INSTALLER.read_text(encoding="utf-8")

    assert "CloseApplications=yes" in installer
    assert "SetupIconFile" not in installer
    assert "istask.dll" not in installer


def test_windows_installer_uses_per_user_aes_associations_and_context_menu_commands() -> None:
    installer = INSTALLER.read_text(encoding="utf-8")

    assert 'Root: HKCU; Subkey: "Software\\Classes\\.aes"' in installer
    assert 'LeoMoonQuickCryptEncrypt\\command' in installer
    assert 'LeoMoonQuickCryptDecrypt\\command' in installer
    assert '"""{app}\\{#AppExeName}"" -e ""%1"""' in installer
    assert '"""{app}\\{#AppExeName}"" -d ""%1"""' in installer


def test_windows_packaging_rejects_legacy_runtime_dlls_and_writes_release_metadata() -> None:
    verifier = VERIFY_SCRIPT.read_text(encoding="utf-8")
    package_script = PACKAGE_SCRIPT.read_text(encoding="utf-8")

    assert '"msvcp100.dll"' in verifier
    assert '"msvcr100.dll"' in verifier
    assert '"istask.dll"' in verifier
    assert "THIRD_PARTY_NOTICES.md" in package_script
    assert "release-manifest.json" in package_script
    assert "SHA256SUMS" in package_script


def test_windows_installer_smoke_checks_install_upgrade_registry_and_uninstall() -> None:
    smoke_script = SMOKE_SCRIPT.read_text(encoding="utf-8")

    assert "LeoMoon QuickCrypt.exe" in smoke_script
    assert "file with spaces.txt" in smoke_script
    assert "LeoMoonQuickCryptEncrypt" in smoke_script
    assert "unins000.exe" in smoke_script
    assert 'ValidateSet("x64", "arm64")' in smoke_script
