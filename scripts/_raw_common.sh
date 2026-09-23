#!/usr/bin/env bash
# _raw_common.sh — shared bits for seal-raw / intake-raw / verify-raw.
# Sourced, not run. Kept deliberately small and readable.

set -euo pipefail

# The raw-data directory and its fingerprint file. Each script may pass a
# directory as its first positional argument; otherwise RAW_DIR, otherwise
# ./data/raw. take_dir_arg() is called by the scripts after they strip flags.
RAW_DIR="${RAW_DIR:-data/raw}"
# NOTE the explicit "return 0": these scripts run under `set -e`, and a bare call
# whose last test fails (no argument given) would otherwise kill the script.
take_dir_arg() {
  if [ -n "${1:-}" ] && [ -d "$1" ]; then
    RAW_DIR="$1"
    MANIFEST="${RAW_DIR%/}.manifest.sha256"
  fi
  return 0
}
MANIFEST="${MANIFEST:-${RAW_DIR%/}.manifest.sha256}"

die() { printf '%s\n' "ERROR: $*" >&2; exit 1; }
say() { printf '%s\n' "$*"; }

# sha256 of one file, portable across macOS (shasum) and Linux (sha256sum).
if command -v shasum >/dev/null 2>&1; then
  hash_of() { shasum -a 256 "$1" | awk '{print $1}'; }
elif command -v sha256sum >/dev/null 2>&1; then
  hash_of() { sha256sum "$1" | awk '{print $1}'; }
else
  die "no shasum or sha256sum on PATH — cannot fingerprint."
fi

# Every file under RAW_DIR, relative to it, sorted, NUL-safe on the find side.
raw_files() { (cd "$RAW_DIR" && find . -type f ! -name '.DS_Store' | sed 's|^\./||' | LC_ALL=C sort); }

# The paths the manifest records, sorted the same way raw_files() sorts.
manifest_paths() { sed -n 's/^[0-9a-f]\{64\}  //p' "$MANIFEST" | LC_ALL=C sort; }

# Write the fingerprint manifest: one "<sha256>  <relative path>" line per file.
write_manifest() {
  local tmp; tmp="$(mktemp)"
  {
    echo "# raw-data fingerprint manifest"
    echo "# dir: $RAW_DIR"
    echo "# written: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
    local f
    while IFS= read -r f; do
      [ -n "$f" ] || continue
      printf '%s  %s\n' "$(hash_of "$RAW_DIR/$f")" "$f"
    done < <(raw_files)
  } > "$tmp"
  mv "$tmp" "$MANIFEST"
  chmod 644 "$MANIFEST"
}

# Make raw data read-only. Files 444, directories 555 (so nothing can be
# created or deleted inside them either).
apply_seal() {
  find "$RAW_DIR" -type f -exec chmod 444 {} +
  find "$RAW_DIR" -type d -exec chmod 555 {} +
}

# Make raw data writable again by its owner — the deliberate, temporary step.
lift_seal() {
  find "$RAW_DIR" -type d -exec chmod u+w {} + 2>/dev/null || true
  find "$RAW_DIR" -type f -exec chmod u+w {} + 2>/dev/null || true
}

# Is the raw dir owned by somebody other than us (i.e. sealed --hard)? Asked this
# way rather than "is it root-owned", so it stays correct for a user who IS root.
is_hard_sealed() {
  [ "$(find "$RAW_DIR" -maxdepth 0 ! -user "$(id -un)" 2>/dev/null | wc -l)" -gt 0 ]
}
