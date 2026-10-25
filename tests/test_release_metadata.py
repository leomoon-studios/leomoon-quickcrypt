from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREPARE_RELEASE_METADATA = PROJECT_ROOT / "scripts" / "prepare_release_metadata.py"


def test_release_metadata_uses_a_semantic_tag(tmp_path: Path) -> None:
    windows_version_file = tmp_path / "version.txt"
    result = subprocess.run(
        [
            sys.executable,
            str(PREPARE_RELEASE_METADATA),
            "--tag",
            "v2.1.0",
            "--release-date",
            "2026-10-23T12:00:00Z",
            "--commit-sha",
            "a" * 40,
            "--allow-unverified-tag",
            "--windows-version-file",
            str(windows_version_file),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    metadata = json.loads(result.stdout)

    assert metadata == {
        "artifact_slug": "leomoon-quickcrypt",
        "commit_sha": "a" * 40,
        "display_name": "LeoMoon QuickCrypt",
        "linux_aarch64_appimage_filename": "leomoon-quickcrypt-2.1.0-linux-aarch64.AppImage",
        "linux_x86_64_appimage_filename": "leomoon-quickcrypt-2.1.0-linux-x86_64.AppImage",
        "macos_arm64_dmg_filename": "leomoon-quickcrypt-2.1.0-macos-arm64.dmg",
        "release_date": "2026-10-23T12:00:00Z",
        "release_manifest_filename": "leomoon-quickcrypt-2.1.0-manifest.json",
        "tag": "v2.1.0",
        "version": "2.1.0",
        "windows_arm64_setup_filename": "leomoon-quickcrypt-2.1.0-windows-arm64-setup.exe",
        "windows_file_version": "2.1.0.0",
        "windows_x64_setup_filename": "leomoon-quickcrypt-2.1.0-windows-x64-setup.exe",
    }
    version_text = windows_version_file.read_text(encoding="utf-8")
    assert "filevers=(2, 1, 0, 0)" in version_text
    assert "LeoMoon QuickCrypt.exe" in version_text


def test_release_metadata_rejects_a_malformed_tag() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(PREPARE_RELEASE_METADATA),
            "--tag",
            "2.1",
            "--release-date",
            "2026-10-23T12:00:00Z",
            "--commit-sha",
            "a" * 40,
            "--allow-unverified-tag",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "vMAJOR.MINOR.PATCH" in result.stderr


def test_release_metadata_uses_the_commit_date_for_a_lightweight_tag(monkeypatch) -> None:
    spec = importlib.util.spec_from_file_location("release_metadata", PREPARE_RELEASE_METADATA)
    assert spec is not None and spec.loader is not None
    release_metadata = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release_metadata)

    def fake_git(*arguments: str) -> str:
        if arguments == ("cat-file", "-t", "v2.1.0"):
            return "commit"
        if arguments == ("log", "-1", "--format=%cI", "v2.1.0^{commit}"):
            return "2026-10-24T07:36:00-07:00"
        raise AssertionError(arguments)

    monkeypatch.setattr(release_metadata, "git", fake_git)

    assert release_metadata.tag_date("v2.1.0") == "2026-10-24T14:36:00Z"


def test_release_metadata_uses_the_tagger_date_for_an_annotated_tag(monkeypatch) -> None:
    spec = importlib.util.spec_from_file_location("release_metadata", PREPARE_RELEASE_METADATA)
    assert spec is not None and spec.loader is not None
    release_metadata = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(release_metadata)

    def fake_git(*arguments: str) -> str:
        if arguments == ("cat-file", "-t", "v2.1.0"):
            return "tag"
        if arguments == ("for-each-ref", "refs/tags/v2.1.0", "--format=%(taggerdate:iso-strict)"):
            return "2026-10-24T07:36:00-07:00"
        raise AssertionError(arguments)

    monkeypatch.setattr(release_metadata, "git", fake_git)

    assert release_metadata.tag_date("v2.1.0") == "2026-10-24T14:36:00Z"
