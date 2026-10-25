#!/usr/bin/env python3
"""Build a versioned, one-directory LeoMoon QuickCrypt application with PyInstaller."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime
from importlib.metadata import version
from pathlib import Path


VERSION_PATTERN = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = PROJECT_ROOT / "build"
SPECIFICATION = PROJECT_ROOT / "packaging" / "pyinstaller" / "quickcrypt.spec"
MACOS_INFO_TEMPLATE = PROJECT_ROOT / "packaging" / "macos" / "Info.plist.in"
DISPLAY_NAME = "LeoMoon QuickCrypt"
ARTIFACT_SLUG = "leomoon-quickcrypt"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="Release version in MAJOR.MINOR.PATCH form.")
    parser.add_argument("--release-date", required=True, help="UTC ISO 8601 release date.")
    parser.add_argument("--commit", required=True, help="Source commit SHA.")
    parser.add_argument("--output-dir", type=Path, default=BUILD_ROOT / "pyinstaller", help="Dedicated build directory under build/.")
    parser.add_argument("--clean", action="store_true", help="Replace the dedicated output directory.")
    return parser.parse_args()


def resolved_output_directory(value: Path) -> Path:
    output_directory = value.resolve()
    build_root = BUILD_ROOT.resolve()
    if output_directory == build_root or build_root not in output_directory.parents:
        raise ValueError(f"--output-dir must be a dedicated directory below {build_root}.")
    return output_directory


def validate_arguments(args: argparse.Namespace) -> Path:
    if VERSION_PATTERN.fullmatch(args.version) is None:
        raise ValueError("--version must use MAJOR.MINOR.PATCH form.")
    parsed_date = datetime.fromisoformat(args.release_date.replace("Z", "+00:00"))
    if parsed_date.tzinfo is None:
        raise ValueError("--release-date must include a UTC or numeric offset.")
    if not re.fullmatch(r"[0-9a-fA-F]{7,64}", args.commit):
        raise ValueError("--commit must be a hexadecimal Git commit SHA.")
    return resolved_output_directory(args.output_dir)


def write_runtime_hook(path: Path, version_value: str) -> None:
    path.write_text("import os\n" f"os.environ.setdefault('LEOMOON_QUICKCRYPT_VERSION', {version_value!r})\n", encoding="utf-8")


def write_macos_info_plist(path: Path, version_value: str) -> None:
    template = MACOS_INFO_TEMPLATE.read_text(encoding="utf-8")
    path.write_text(template.replace("@VERSION@", version_value), encoding="utf-8")


def installed_versions() -> dict[str, str]:
    from PySide6 import QtCore, __version__ as pyside6_version

    return {
        "cryptography_version": version("cryptography"),
        "pyAesCrypt_version": version("pyAesCrypt"),
        "pyinstaller_version": version("pyinstaller"),
        "pyside6_version": pyside6_version,
        "python_version": platform.python_version(),
        "qt_version": QtCore.qVersion(),
    }


def build(args: argparse.Namespace, output_directory: Path) -> Path:
    if output_directory.exists():
        if not args.clean:
            raise FileExistsError(f"{output_directory} exists. Pass --clean to replace it.")
        shutil.rmtree(output_directory)
    output_directory.mkdir(parents=True)
    work_directory = output_directory / ".work"
    runtime_hook = work_directory / "set_build_version.py"
    work_directory.mkdir()
    write_runtime_hook(runtime_hook, args.version)

    environment = os.environ.copy()
    environment["LEOMOON_QUICKCRYPT_VERSION"] = args.version
    environment["LEOMOON_QUICKCRYPT_RUNTIME_HOOK"] = str(runtime_hook)
    if sys.platform == "darwin":
        info_plist = work_directory / "Info.plist"
        write_macos_info_plist(info_plist, args.version)
        environment["LEOMOON_QUICKCRYPT_MACOS_INFO_PLIST"] = str(info_plist)
    subprocess.run([
        sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "--distpath", str(output_directory),
        "--workpath", str(work_directory / "pyinstaller"), str(SPECIFICATION),
    ], check=True, cwd=PROJECT_ROOT, env=environment)
    application_directory = output_directory / ARTIFACT_SLUG
    if sys.platform == "darwin":
        bundle = output_directory / f"{DISPLAY_NAME}.app"
        executable = bundle / "Contents" / "MacOS" / DISPLAY_NAME
    else:
        executable_name = f"{DISPLAY_NAME}.exe" if sys.platform == "win32" else DISPLAY_NAME
        executable = application_directory / executable_name
    if not executable.is_file():
        raise FileNotFoundError("PyInstaller did not produce the expected application executable.")
    if sys.platform == "darwin":
        shutil.move(str(bundle), application_directory)
    return application_directory


def write_manifest(args: argparse.Namespace, output_directory: Path, application_directory: Path) -> Path:
    manifest = {
        "application": DISPLAY_NAME,
        "artifact_slug": ARTIFACT_SLUG,
        "version": args.version,
        "release_date": args.release_date,
        "commit": args.commit,
        "platform": sys.platform,
        "architecture": platform.machine(),
        "artifact_format": "pyinstaller-onedir",
        "application_directory": application_directory.name,
        **installed_versions(),
    }
    manifest_path = output_directory / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    try:
        args = arguments()
        output_directory = validate_arguments(args)
        application_directory = build(args, output_directory)
        manifest_path = write_manifest(args, output_directory, application_directory)
    except (FileExistsError, FileNotFoundError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(manifest_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
