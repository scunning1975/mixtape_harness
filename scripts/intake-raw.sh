#!/usr/bin/env bash
# intake-raw.sh — the one sanctioned door for getting data into a sealed raw dir.
#
# WHY. Once the raw directory is sealed, nothing can write to it — that is the
# point. But you still need a deliberate way to add the next batch of source
# files. This is that door: it lifts the seal, copies your files in, re-seals,
# and refreshes the fingerprint manifest, in one motion. The friction is the
# feature. Adding raw data should be a decision you make on purpose, not a
# keystroke an agent slips in.
#
# It refuses to overwrite a file that is already sealed in. Raw data is
# write-once; a new version of a source file is a NEW file with a new name, so
# the old fingerprints stay meaningful.
#
# USAGE
#   scripts/intake-raw.sh ~/Downloads/qcew_2019.csv
#   scripts/intake-raw.sh --hard ~/Downloads/*.csv     (for a root-owned seal)

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/_raw_common.sh"

HARD=0
if [ "${1:-}" = "--hard" ]; then HARD=1; shift; fi
if [ "$HARD" -eq 0 ] && is_hard_sealed; then
  die "$RAW_DIR is root-owned (sealed --hard). Re-run as: scripts/intake-raw.sh --hard $*"
fi

[ "$#" -gt 0 ] || die "nothing to add. Usage: scripts/intake-raw.sh <file> [...]"

mkdir -p "$RAW_DIR"

# Refuse before touching anything, so a bad argument does not leave the seal
# half-lifted with some files copied and others not.
for src in "$@"; do
  [ -f "$src" ] || die "not a file: $src"
  [ -e "$RAW_DIR/$(basename "$src")" ] && die "already in $RAW_DIR: $(basename "$src") — raw data is write-once. Give the new version a different name."
done

say "Lifting the seal on $RAW_DIR …"
if [ "$HARD" -eq 1 ]; then
  sudo chown -R "$(id -un)" "$RAW_DIR"
fi
lift_seal

for src in "$@"; do
  cp "$src" "$RAW_DIR/"
  say "  added  $(basename "$src")"
done

say "Re-sealing and refreshing the manifest …"
write_manifest
if [ "$HARD" -eq 1 ]; then
  sudo chown -R root "$RAW_DIR"
  sudo find "$RAW_DIR" -type f -exec chmod 444 {} +
  sudo find "$RAW_DIR" -type d -exec chmod 555 {} +
else
  apply_seal
fi

say ""
say "Done. $RAW_DIR sealed again, $(raw_files | grep -c . || true) file(s) fingerprinted."
