#!/usr/bin/env bash
# verify-raw.sh — prove the raw data is byte-for-byte what it was when sealed.
#
# WHY. Permissions stop the ordinary write; they do not stop a process running
# as you from lifting the seal first. This is the check that catches what the
# seal could not prevent. Run it at the top of every pipeline run, and any time
# you want to know the raw data has not moved under you.
#
# Reading is always allowed, so this works whether the seal is owner-level or
# root-owned.
#
# EXIT CODE
#   0  clean — every file matches the manifest, none missing, none added
#   1  drift — something changed, disappeared, or appeared. Details printed.
#
# USAGE
#   scripts/verify-raw.sh
#   RAW_DIR=path/to/raw scripts/verify-raw.sh

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/_raw_common.sh"

take_dir_arg "${1:-}"

[ -d "$RAW_DIR" ]   || die "no such directory: $RAW_DIR"
[ -f "$MANIFEST" ]  || die "no manifest at $MANIFEST — run scripts/seal-raw.sh first."

changed=0; missing=0; added=0

# Walk the manifest: does each recorded file still exist, with the same hash?
while read -r want path; do
  case "$want" in ''|\#*) continue ;; esac
  if [ ! -f "$RAW_DIR/$path" ]; then
    say "  MISSING  $path"; missing=$((missing + 1)); continue
  fi
  got="$(hash_of "$RAW_DIR/$path")"
  if [ "$got" != "$want" ]; then
    say "  CHANGED  $path"
    say "             sealed as $want"
    say "             now reads  $got"
    changed=$((changed + 1))
  fi
done < "$MANIFEST"

# And the other direction: anything on disk the manifest never recorded? Compared
# as two sorted lists rather than by grepping the filename as a pattern, so a dot
# or a bracket in a name cannot quietly match the wrong line.
while IFS= read -r f; do
  [ -n "$f" ] || continue
  say "  NEW      $f"; added=$((added + 1))
done < <(comm -13 <(manifest_paths) <(raw_files))

total=$((changed + missing + added))
say ""
if [ "$total" -eq 0 ]; then
  say "Raw data verified clean against $MANIFEST."
  exit 0
fi
say "RAW DATA DRIFT: $changed changed, $missing missing, $added new."
say ""
say "The seal did not hold, or someone lifted it. Before anything else, get the"
say "original bytes back — from your backup, or from your sync service's version"
say "history. Then re-seal with scripts/seal-raw.sh."
exit 1
