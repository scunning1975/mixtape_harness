#!/usr/bin/env bash
# verify-raw.sh — prove the sealed raw data is byte-for-byte what it was when sealed.
#
# WHY: permissions stop the modal write, but a determined process running as you can
# still un-seal. The manifest is the after-the-fact truth: run this any time (and
# every pipeline run) to confirm no raw file changed, none went missing, none appeared.
# Reading is always allowed, so this works whether the seal is owner-level or root-owned.
#
# USAGE:
#   scripts/verify-raw.sh                # verify ./data/raw against ./data/raw.manifest.sha256
#   RAW_DIR=data/raw scripts/verify-raw.sh
#
# Exit 0 = clean. Exit 1 = drift (prints what changed). Wire into run_pipeline.sh.
set -euo pipefail

RAW_DIR="${1:-${RAW_DIR:-data/raw}}"
MANIFEST="$(dirname "$RAW_DIR")/raw.manifest.sha256"

if [[ ! -f "$MANIFEST" ]]; then
  echo "verify-raw: no manifest at $MANIFEST — run scripts/seal-raw.sh first." >&2
  exit 1
fi
if command -v shasum >/dev/null 2>&1; then SHA="shasum -a 256";
elif command -v sha256sum >/dev/null 2>&1; then SHA="sha256sum";
else echo "verify-raw: need shasum or sha256sum" >&2; exit 1; fi

# recompute current fingerprints, compare to the manifest
CUR="$(mktemp)"
( cd "$RAW_DIR" && find . -type f ! -name '.DS_Store' -print0 \
    | sort -z | xargs -0 $SHA ) > "$CUR"

if diff -q "$MANIFEST" "$CUR" >/dev/null; then
  N=$(wc -l < "$MANIFEST" | tr -d ' ')
  echo "verify-raw: ✓ clean — $N raw file(s) match the sealed manifest."
  rm -f "$CUR"; exit 0
fi

echo "verify-raw: ✗ DRIFT DETECTED in $RAW_DIR — raw data no longer matches the seal:" >&2
# show what differs (changed hash, missing, or new file)
diff <(awk '{print $2}' "$MANIFEST" | sort) <(awk '{print $2}' "$CUR" | sort) \
  | grep '^[<>]' | sed 's/^</  MISSING now: /; s/^>/  NEW  since seal: /' >&2 || true
comm -12 <(sort "$MANIFEST") <(sort "$CUR") >/dev/null 2>&1 || true
# files present in both but with a changed hash:
join -j 2 <(sort -k2 "$MANIFEST") <(sort -k2 "$CUR") 2>/dev/null \
  | awk '$2 != $3 {print "  CHANGED: "$1}' >&2 || true
rm -f "$CUR"
exit 1
