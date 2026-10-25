#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
stage_dir=""
dist_dir=""
version=""
release_date=""
commit=""
architecture=""
appimagetool=""
appimagetool_version=""
appimagetool_sha256=""
runtime_file=""
runtime_version=""
runtime_sha256=""

usage() {
    echo "Usage: $0 --stage-dir DIR --dist-dir DIR --version VERSION --release-date DATE --commit SHA --architecture x86_64|aarch64 --appimagetool PATH --appimagetool-version VERSION --appimagetool-sha256 SHA256 --runtime-file PATH --runtime-version VERSION --runtime-sha256 SHA256" >&2
}

while (( $# )); do
    case "$1" in
        --stage-dir) stage_dir="$2"; shift 2 ;;
        --dist-dir) dist_dir="$2"; shift 2 ;;
        --version) version="$2"; shift 2 ;;
        --release-date) release_date="$2"; shift 2 ;;
        --commit) commit="$2"; shift 2 ;;
        --architecture) architecture="$2"; shift 2 ;;
        --appimagetool) appimagetool="$2"; shift 2 ;;
        --appimagetool-version) appimagetool_version="$2"; shift 2 ;;
        --appimagetool-sha256) appimagetool_sha256="$2"; shift 2 ;;
        --runtime-file) runtime_file="$2"; shift 2 ;;
        --runtime-version) runtime_version="$2"; shift 2 ;;
        --runtime-sha256) runtime_sha256="$2"; shift 2 ;;
        *) usage; exit 2 ;;
    esac
done

[[ -n "$stage_dir" && -n "$dist_dir" && -n "$version" && -n "$release_date" && -n "$commit" && -n "$architecture" && -n "$appimagetool" && -n "$appimagetool_version" && -n "$appimagetool_sha256" && -n "$runtime_file" && -n "$runtime_version" && -n "$runtime_sha256" ]] || { usage; exit 2; }
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] || { echo "Version must be MAJOR.MINOR.PATCH" >&2; exit 2; }
[[ "$release_date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T ]] || { echo "Release date must be ISO 8601" >&2; exit 2; }
[[ "$commit" =~ ^[0-9a-fA-F]{7,64}$ ]] || { echo "Commit must be a Git SHA" >&2; exit 2; }
[[ "$architecture" == x86_64 || "$architecture" == aarch64 ]] || { echo "Architecture must be x86_64 or aarch64" >&2; exit 2; }

stage_dir="$(realpath "$stage_dir")"
dist_dir="$(realpath -m "$dist_dir")"
appimagetool="$(realpath "$appimagetool")"
runtime_file="$(realpath "$runtime_file")"
[[ -x "$appimagetool" ]] || { echo "AppImage tool is not executable: $appimagetool" >&2; exit 1; }
[[ -f "$runtime_file" ]] || { echo "AppImage runtime is missing: $runtime_file" >&2; exit 1; }
[[ -f "$stage_dir/LeoMoon QuickCrypt" ]] || { echo "Stage directory must contain LeoMoon QuickCrypt" >&2; exit 1; }
[[ "$dist_dir" != / && "$dist_dir" != "$repo_dir" ]] || { echo "Refusing to replace unsafe artifact directory: $dist_dir" >&2; exit 1; }
[[ "$(sha256sum "$appimagetool" | awk '{print $1}')" == "$appimagetool_sha256" ]] || { echo "AppImage tool checksum does not match the pinned SHA-256" >&2; exit 1; }
[[ "$(sha256sum "$runtime_file" | awk '{print $1}')" == "$runtime_sha256" ]] || { echo "AppImage runtime checksum does not match the pinned SHA-256" >&2; exit 1; }

package_dir="$repo_dir/build/package/linux/$architecture"
app_dir="$package_dir/AppDir"
rm -rf "$package_dir"
mkdir -p "$app_dir/usr/bin" "$app_dir/usr/lib" "$app_dir/usr/share/applications" "$app_dir/usr/share/icons/hicolor/256x256/apps" "$app_dir/usr/share/mime/packages" "$app_dir/usr/share/doc/leomoon-quickcrypt"
cp -a "$stage_dir" "$app_dir/usr/lib/leomoon-quickcrypt"
install -m 0755 "$repo_dir/packaging/linux/AppRun" "$app_dir/AppRun"
install -m 0755 "$repo_dir/packaging/linux/leomoon-quickcrypt" "$app_dir/usr/bin/leomoon-quickcrypt"
install -m 0644 "$repo_dir/packaging/linux/com.leomoon.QuickCrypt.desktop" "$app_dir/usr/share/applications/com.leomoon.QuickCrypt.desktop"
install -m 0644 "$repo_dir/packaging/linux/mime/com.leomoon.QuickCrypt.xml" "$app_dir/usr/share/mime/packages/com.leomoon.QuickCrypt.xml"
install -m 0644 "$repo_dir/src/leomoon_quickcrypt/assets/icons/main.png" "$app_dir/usr/share/icons/hicolor/256x256/apps/com.leomoon.QuickCrypt.png"
install -m 0644 "$repo_dir/THIRD_PARTY_NOTICES.md" "$app_dir/usr/share/doc/leomoon-quickcrypt/THIRD_PARTY_NOTICES.md"
ln -s "usr/share/applications/com.leomoon.QuickCrypt.desktop" "$app_dir/com.leomoon.QuickCrypt.desktop"
ln -s "usr/share/icons/hicolor/256x256/apps/com.leomoon.QuickCrypt.png" "$app_dir/com.leomoon.QuickCrypt.png"

rm -rf "$dist_dir"
mkdir -p "$dist_dir"
appimage="$dist_dir/leomoon-quickcrypt-$version-linux-$architecture.AppImage"
ARCH="$architecture" APPIMAGE_EXTRACT_AND_RUN=1 "$appimagetool" --runtime-file "$runtime_file" "$app_dir" "$appimage"
chmod +x "$appimage"
bash "$repo_dir/scripts/verify-linux-appimage.sh" "$appimage" "$version" "$architecture"

cat > "$dist_dir/release-manifest.json" <<EOF
{
  "application": "LeoMoon QuickCrypt",
  "version": "$version",
  "release_date": "$release_date",
  "commit": "$commit",
  "platform": "linux",
  "architecture": "$architecture",
  "artifact_format": "AppImage",
  "appimagetool_version": "$appimagetool_version",
  "appimagetool_sha256": "$appimagetool_sha256",
  "runtime_version": "$runtime_version",
  "runtime_sha256": "$runtime_sha256"
}
EOF
(
    cd "$dist_dir"
    sha256sum ./* > SHA256SUMS
)
echo "Linux release artifacts are ready in $dist_dir"
