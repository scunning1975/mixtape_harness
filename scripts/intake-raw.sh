#!/usr/bin/env bash
# intake-raw.sh — the ONE sanctioned door for getting data into a sealed data/raw/.
#
# WHY: once data/raw/ is sealed read-only, nothing can write to it — which is the
# point. But you still need a deliberate, rare, human way to add the next batch of
# raw files. This is that door: it un-seals, copies your files in, and re-seals in
# one motion, then refreshes the fingerprint manifest. The friction is the feature —
# adding raw data is a decision you make on purpose, not a keystroke an agent slips in.
#
# USAGE:
#   scripts/intake-raw.sh newfile.csv                 # add one file to ./data/raw
#   scripts/intake-raw.sh a.csv b.dta some_dir/       # add several (dirs copied recursively)
#   scripts/intake-raw.sh --hard newfile.csv          # for a root-owned (sudo) seal
#   RAW_DIR=data/raw scripts/intake-raw.sh f.csv       # different raw dir
#
# It refuses to silently overwrite an existing raw file (raw is write-once). Pass
# --replace to intentionally supersede one — a loud, deliberate act.
set -euo pipefail

HARD=0; REPLACE=0
SRCS=()
for a in "$@"; do
  case "$a" in
    --hard)    HARD=1 ;;
    --replace) REPLACE=1 ;;
    *)         SRCS+=("$a") ;;
  esac
done
RAW_DIR="${RAW_DIR:-data/raw}"

if [[ ${#SRCS[@]} -eq 0 ]]; then
  echo "intake-raw: nothing to add. usage: scripts/intake-raw.sh [--hard] [--replace] FILE..." >&2
  exit 1
fi
mkdir -p "$RAW_DIR"

SUDO=""; [[ $HARD -eq 1 ]] && SUDO="sudo"

echo "intake-raw: opening $RAW_DIR for intake …"
$SUDO chmod -R u+w "$RAW_DIR"

for src in "${SRCS[@]}"; do
  if [[ ! -e "$src" ]]; then echo "  ! skip (not found): $src" >&2; continue; fi
  base="$(basename "$src")"
  dest="$RAW_DIR/$base"
  if [[ -e "$dest" && $REPLACE -eq 0 ]]; then
    echo "  ! skip (already exists, raw is write-once): $base  — pass --replace to supersede" >&2
    continue
  fi
  $SUDO cp -R "$src" "$dest"
  echo "  + added: $base"
done

echo "intake-raw: re-sealing …"
# delegate the re-seal + manifest refresh to seal-raw.sh so there is ONE seal definition
HERE="$(cd "$(dirname "$0")" && pwd)"
if [[ $HARD -eq 1 ]]; then
  RAW_DIR="$RAW_DIR" "$HERE/seal-raw.sh" --hard "$RAW_DIR"
else
  RAW_DIR="$RAW_DIR" "$HERE/seal-raw.sh" "$RAW_DIR"
fi
echo "  ✓ intake complete — raw is sealed again."
