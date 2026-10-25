#!/usr/bin/env bash
set -euo pipefail

[[ $# -eq 3 ]] || { echo "Usage: $0 ARTIFACT_DIRECTORY VERSION arm64" >&2; exit 2; }
artifact_dir="$(cd "$1" && pwd)"
version="$2"
architecture="$3"
repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
dmg="$artifact_dir/leomoon-quickcrypt-$version-macos-$architecture.dmg"

(cd "$artifact_dir" && shasum -a 256 -c SHA256SUMS)
mount_dir="$(mktemp -d)"
copy_dir="$(mktemp -d)"
device=""
cleanup() { [[ -n "$device" ]] && hdiutil detach "$device" -quiet || true; rm -rf "$mount_dir" "$copy_dir"; }
trap cleanup EXIT
device="$(hdiutil attach -nobrowse -readonly -mountpoint "$mount_dir" "$dmg" | awk '/^\/dev\// {print $1; exit}')"
app="$mount_dir/LeoMoon QuickCrypt.app"
bash "$repo_dir/scripts/verify-macos-package.sh" "$app" "$dmg" "$version" "$architecture"
cp -a "$app" "$copy_dir/"
copied_app="$copy_dir/LeoMoon QuickCrypt.app"
xattr -d com.apple.quarantine "$copied_app" 2>/dev/null || true
"$copied_app/Contents/MacOS/LeoMoon QuickCrypt" --version | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+'

input="$copy_dir/input with spaces.txt"
encrypted="$copy_dir/input with spaces.txt.aes"
printf 'QuickCrypt DMG smoke input\n' > "$input"
printf 'AES' > "$encrypted"
for mode in -e -d; do
    target="$input"
    [[ "$mode" == -d ]] && target="$encrypted"
    "$copied_app/Contents/MacOS/LeoMoon QuickCrypt" "$mode" "$target" &
    process_id=$!
    sleep 3
    kill -0 "$process_id" 2>/dev/null || { echo "Copied application did not launch with $mode" >&2; exit 1; }
    kill "$process_id"
    wait "$process_id" || true
done
if grep -q '"signed": true' "$artifact_dir/release-manifest.json"; then spctl --assess --type execute "$copied_app"; fi
