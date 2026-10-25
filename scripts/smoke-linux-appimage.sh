#!/usr/bin/env bash
set -euo pipefail

if (( $# != 1 )); then
    echo "Usage: $0 APPIMAGE" >&2
    exit 2
fi

appimage="$(realpath "$1")"
[[ -x "$appimage" ]] || { echo "AppImage is not executable: $appimage" >&2; exit 1; }
work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT
input="$work_dir/input with spaces.txt"
encrypted="$work_dir/input with spaces.txt.aes"
printf 'QuickCrypt AppImage smoke input\n' > "$input"
printf 'AES' > "$encrypted"

env -i HOME="$work_dir/home" PATH=/usr/bin:/bin TMPDIR="$work_dir" QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME=none APPIMAGE_EXTRACT_AND_RUN=1 \
    "$appimage" --version | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+'

for mode in -e -d; do
    target="$input"
    [[ "$mode" == -d ]] && target="$encrypted"
    set +e
    env -i HOME="$work_dir/home" PATH=/usr/bin:/bin TMPDIR="$work_dir" QT_QPA_PLATFORM=offscreen QT_QPA_PLATFORMTHEME=none APPIMAGE_EXTRACT_AND_RUN=1 \
        timeout 3s "$appimage" "$mode" "$target"
    status=$?
    set -e
    [[ "$status" == 124 ]] || { echo "AppImage did not remain open for $mode input" >&2; exit 1; }
done

echo "Linux AppImage launch and argument handling check passed"
