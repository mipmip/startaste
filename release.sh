#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_FILE="$SCRIPT_DIR/VERSION"
CHANGELOG_FILE="$SCRIPT_DIR/CHANGELOG.md"

DRY_RUN=false
BUMP_TYPE=""

####################
# Argument parsing #
####################

usage() {
  echo "Usage: release.sh <major|minor|patch> [--dry-run]"
  exit 1
}

for arg in "$@"; do
  case "$arg" in
    major|minor|patch) BUMP_TYPE="$arg" ;;
    --dry-run) DRY_RUN=true ;;
    *) echo "Unknown argument: $arg"; usage ;;
  esac
done

if [[ -z "$BUMP_TYPE" ]]; then
  echo "Error: bump type required (major, minor, or patch)"
  usage
fi

####################
# Pre-flight checks #
####################

if [[ ! -f "$VERSION_FILE" ]]; then
  echo "Error: VERSION file not found at $VERSION_FILE"
  exit 1
fi

if [[ ! -f "$CHANGELOG_FILE" ]]; then
  echo "Error: CHANGELOG.md not found at $CHANGELOG_FILE"
  exit 1
fi

if ! grep -q '## \[Unreleased\]' "$CHANGELOG_FILE"; then
  echo "Error: CHANGELOG.md has no [Unreleased] section"
  exit 1
fi

# Check for content under [Unreleased]: extract lines between [Unreleased] and next ## heading
unreleased_content=$(sed -n '/^## \[Unreleased\]/,/^## \[/{/^## \[/d;p}' "$CHANGELOG_FILE" | grep -v '^[[:space:]]*$' || true)
if [[ -z "$unreleased_content" ]]; then
  echo "Error: no entries under [Unreleased] — nothing to release"
  exit 1
fi

for tool in jj git gh; do
  if ! command -v "$tool" &>/dev/null; then
    echo "Error: $tool is not on PATH"
    exit 1
  fi
done

####################
# Version bump     #
####################

current_version=$(cat "$VERSION_FILE" | tr -d '[:space:]')
IFS='.' read -r major minor patch <<< "$current_version"

case "$BUMP_TYPE" in
  major) major=$((major + 1)); minor=0; patch=0 ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  patch) patch=$((patch + 1)) ;;
esac

new_version="${major}.${minor}.${patch}"
release_date=$(date +%Y-%m-%d)

echo "Bumping $current_version → $new_version ($BUMP_TYPE)"

####################
# Dry run          #
####################

if [[ "$DRY_RUN" == true ]]; then
  echo ""
  echo "=== DRY RUN ==="
  echo ""
  echo "VERSION: $current_version → $new_version"
  echo "Date: $release_date"
  echo ""
  echo "Changelog entries to be released:"
  echo "$unreleased_content"
  echo ""
  echo "Commands that would run:"
  echo "  1. Write $new_version to VERSION"
  echo "  2. Update CHANGELOG.md: [Unreleased] → [$new_version] - $release_date"
  echo "  3. jj describe -m \"release v$new_version\""
  echo "  4. jj new"
  echo "  5. git tag v$new_version"
  echo "  6. jj git push --all"
  echo "  7. gh release create v$new_version --title \"v$new_version\" --notes <changelog section>"
  echo ""
  echo "No changes made."
  exit 0
fi

####################
# Changelog update #
####################

sed -i "s/^## \[Unreleased\]/## [Unreleased]\n\n## [$new_version] - $release_date/" "$CHANGELOG_FILE"

####################
# Write VERSION    #
####################

echo "$new_version" > "$VERSION_FILE"

####################
# VCS operations   #
####################

jj describe -m "release v$new_version"
jj new
git tag "v$new_version"

####################
# Push             #
####################

jj git push --all

####################
# GitHub release   #
####################

# Extract release notes: everything between this version's heading and the next ## heading
release_notes=$(sed -n "/^## \[$new_version\]/,/^## \[/{/^## \[/d;p}" "$CHANGELOG_FILE" | sed '/./,$!d' | sed -e :a -e '/^[[:space:]]*$/{ $d; N; ba; }')

gh release create "v$new_version" \
  --title "v$new_version" \
  --notes "$release_notes"

echo ""
echo "Released v$new_version"
