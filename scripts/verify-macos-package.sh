#!/usr/bin/env bash
set -euo pipefail

[[ $# -eq 4 ]] || { echo "Usage: $0 APP_BUNDLE DMG VERSION arm64" >&2; exit 2; }
app="$1"
dmg="$2"
version="$3"
architecture="$4"
executable="$app/Contents/MacOS/LeoMoon QuickCrypt"

[[ -d "$app" && -x "$executable" && -f "$app/Contents/Info.plist" ]] || { echo "Invalid macOS application bundle" >&2; exit 1; }
[[ -s "$dmg" && "$(basename "$dmg")" == "leomoon-quickcrypt-$version-macos-$architecture.dmg" ]] || { echo "Unexpected DMG artifact" >&2; exit 1; }
[[ "$(plutil -extract CFBundleIdentifier raw "$app/Contents/Info.plist")" == "com.leomoon.QuickCrypt" ]] || { echo "Unexpected bundle identifier" >&2; exit 1; }
[[ "$(plutil -extract CFBundleShortVersionString raw "$app/Contents/Info.plist")" == "$version" ]] || { echo "Unexpected bundle version" >&2; exit 1; }
[[ "$(plutil -extract LSMinimumSystemVersion raw "$app/Contents/Info.plist")" == "12.0" ]] || { echo "Unexpected minimum macOS version" >&2; exit 1; }
[[ "$(plutil -extract CFBundleDocumentTypes.0.CFBundleTypeExtensions.0 raw "$app/Contents/Info.plist")" == "aes" ]] || { echo "Missing AES Crypt document association" >&2; exit 1; }

while IFS= read -r -d '' binary; do
    architectures="$(lipo -archs "$binary")"
    [[ "$architecture" == arm64 && "$architectures" == arm64 ]] || { echo "Application contains a non-ARM64 Mach-O payload: $binary" >&2; exit 1; }
done < <(find "$app/Contents" -type f -print0 | while IFS= read -r -d '' candidate; do file "$candidate" | grep -q 'Mach-O' && printf '%s\0' "$candidate"; done)
hdiutil imageinfo "$dmg" >/dev/null
if [[ -n "${LEOMOON_QUICKCRYPT_MACOS_CODESIGN_IDENTITY:-}" ]]; then codesign --verify --deep --strict --verbose=2 "$app"; fi
if [[ -n "${LEOMOON_QUICKCRYPT_MACOS_NOTARY_PROFILE:-}" ]]; then xcrun stapler validate "$dmg"; fi
