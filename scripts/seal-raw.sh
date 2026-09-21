#!/usr/bin/env bash
# seal-raw.sh — make raw data immutable, and write a fingerprint manifest.
#
# WHY: raw source data is write-once. Agents (and honest mistakes) must never
# modify it. This is the OS-level "wall" the protect-raw-data hook only gestures
# at — the hook is a doorbell; permissions are the lock.
#
# WHAT IT DOES:
#   1. sets every file under the raw dir to read-only (444)
#   2. sets the raw dir (and subdirs) to read+execute only (555) — so files
#      cannot be added, deleted, or replaced, only read
#   3. writes a SHA-256 manifest next to the raw dir (raw.manifest.sha256) so a
#      later `verify-raw.sh` can prove nothing changed
#
# TWO STRENGTHS:
#   (default)  you still OWN the files → you can re-seal/unseal without a password.
#              Stops accidental + agent writes. A process running AS YOU could
#              chmod +w first, so this is a strong speed bump, not a vault.
#   --hard     chown to root:wheel → even you need sudo to change it. A real wall.
#              (Prompts for your password. Intake then also needs --hard.)
#
# USAGE:
#   scripts/seal-raw.sh                 # seal ./data/raw  (owner-level)
#   scripts/seal-raw.sh path/to/raw     # seal a different raw dir
#   scripts/seal-raw.sh --hard          # seal ./data/raw  root-owned (sudo)
#   RAW_DIR=data/raw scripts/seal-raw.sh
#
# Re-run any time — it is idempotent. Run after every intake.
set -euo pipefail

HARD=0
ARGS=()
for a in "$@"; do
  case "$a" in
    --hard) HARD=1 ;;
    *) ARGS+=("$a") ;;
  esac
done
RAW_DIR="${ARGS[0]:-${RAW_DIR:-data/raw}}"

if [[ ! -d "$RAW_DIR" ]]; then
  echo "seal-raw: no such directory: $RAW_DIR" >&2
  echo "  (create it and put your raw files in FIRST, then seal.)" >&2
  exit 1
fi

# pick a sha-256 tool (macOS: shasum -a 256 ; linux: sha256sum)
if command -v shasum >/dev/null 2>&1; then SHA="shasum -a 256";
elif command -v sha256sum >/dev/null 2>&1; then SHA="sha256sum";
else echo "seal-raw: need shasum or sha256sum on PATH" >&2; exit 1; fi

MANIFEST="$(dirname "$RAW_DIR")/raw.manifest.sha256"

echo "seal-raw: sealing $RAW_DIR ($([[ $HARD -eq 1 ]] && echo 'HARD / root-owned' || echo 'owner-level'))"

# 1. write the fingerprint manifest BEFORE sealing perms (needs to read the files;
#    reading is always allowed, but we write the manifest OUTSIDE the sealed dir).
#    Sorted, path-relative, so it is stable and diffable.
( cd "$RAW_DIR" && find . -type f ! -name '.DS_Store' -print0 \
    | sort -z | xargs -0 $SHA ) > "$MANIFEST"
COUNT=$(wc -l < "$MANIFEST" | tr -d ' ')
echo "  fingerprinted $COUNT file(s) -> $MANIFEST"

# 2. seal permissions: files 444, dirs 555.
chmod -R a-w "$RAW_DIR"
find "$RAW_DIR" -type d -exec chmod 555 {} +
find "$RAW_DIR" -type f -exec chmod 444 {} +

# 3. optional hard seal: hand ownership to root so even the owner needs sudo.
if [[ $HARD -eq 1 ]]; then
  echo "  chowning to root:wheel (sudo) …"
  sudo chown -R root:wheel "$RAW_DIR"
fi

echo "  ✓ sealed. Raw data is now read-only. To add more, use scripts/intake-raw.sh"
