from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = PROJECT_ROOT / ".github" / "workflows"


def test_windows_workflow_uses_native_x64_and_arm64_runners() -> None:
    workflow = (WORKFLOWS / "windows.yml").read_text(encoding="utf-8")

    assert "windows-2022" in workflow
    assert "windows-11-vs2026-arm" in workflow
    assert '"x64","arm64"' in workflow
    assert "package-windows.ps1" in workflow
    assert "smoke-windows-installer.ps1" in workflow
    assert "openssl:arm64-windows" in workflow
    assert "CARGO_TARGET_AARCH64_PC_WINDOWS_MSVC_LINKER" in workflow
    assert "installed\\arm64-windows\\bin" in workflow
    assert workflow.index("Configure MSVC dependency tools") < workflow.index("Create locked project environment")


def test_linux_workflow_uses_native_x86_64_and_arm64_appimage_builds() -> None:
    workflow = (WORKFLOWS / "linux.yml").read_text(encoding="utf-8")

    assert "ubuntu-24.04" in workflow
    assert "ubuntu-24.04-arm" in workflow
    assert '"x86_64","aarch64"' in workflow
    assert "--appimagetool-version 1.9.1" in workflow
    assert "package-linux.sh" in workflow
    assert "smoke-linux-appimage.sh" in workflow


def test_macos_workflow_builds_only_the_native_arm64_dmg() -> None:
    workflow = (WORKFLOWS / "macos.yml").read_text(encoding="utf-8")

    assert "runs-on: macos-15" in workflow
    assert "macos-15-intel" not in workflow
    assert "universal" not in workflow.lower()
    assert "package-macos.sh" in workflow
    assert "smoke-macos-dmg.sh" in workflow


def test_platform_workflows_use_pinned_node_24_compatible_action_revisions() -> None:
    for name in ("windows.yml", "linux.yml", "macos.yml"):
        workflow = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert "actions/checkout@fbc6f3992d24b796d5a048ff273f7fcc4a7b6c09 # v5" in workflow
        assert "actions/setup-python@6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 # v7" in workflow
        assert "actions/upload-artifact@b7c566a772e6b6bfb58ed0dc250532a479d7789f # v6" in workflow


def test_platform_workflows_only_check_deterministic_generated_ui_output() -> None:
    for name in ("windows.yml", "linux.yml", "macos.yml"):
        workflow = (WORKFLOWS / name).read_text(encoding="utf-8")
        assert "git diff --exit-code -- src/leomoon_quickcrypt/_generated/main_window.py" in workflow
        assert "resources_rc.py" not in workflow


def test_release_orchestrates_platform_workflows_and_limits_write_permission() -> None:
    release = (WORKFLOWS / "release.yml").read_text(encoding="utf-8")

    assert "workflow_dispatch:" in release
    assert 'tags: ["v*.*.*"]' in release
    assert "./.github/workflows/linux.yml" in release
    assert "./.github/workflows/windows.yml" in release
    assert "./.github/workflows/macos.yml" in release
    assert "name: Publish GitHub release" in release
    assert "permissions:\n      contents: write" in release
    assert "Generate release notes with commit list" in release
    assert "gh api" in release
    assert "https://github.com/%s/commit/%s" in release
    assert "https://github.com/%s" in release


def test_release_asset_collector_requires_exactly_five_expected_assets() -> None:
    collector = (PROJECT_ROOT / "scripts" / "collect-release-assets.sh").read_text(encoding="utf-8")

    assert '"leomoon-quickcrypt-$version-linux-x86_64.AppImage"' in collector
    assert '"leomoon-quickcrypt-$version-linux-aarch64.AppImage"' in collector
    assert '"leomoon-quickcrypt-$version-windows-x64-setup.exe"' in collector
    assert '"leomoon-quickcrypt-$version-windows-arm64-setup.exe"' in collector
    assert '"leomoon-quickcrypt-$version-macos-arm64.dmg"' in collector
    assert "Expected exactly one release asset" in collector
