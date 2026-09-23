#!/usr/bin/env bash
# seal-raw.sh — make raw data read-only, and write down its fingerprints.
#
# WHY. Raw source data is write-once. Nothing in the pipeline, and no agent,
# should ever be able to modify it. The protect-raw-data hook is a doorbell:
# it catches the honest Edit/Write mistake and explains it. This script is the
# lock underneath — file permissions, enforced by the operating system, which
# an agent cannot talk its way past.
#
# HONEST LIMIT. The default seal is owner-level. It blocks every ordinary
# write (echo >, cp over, sed -i, dd, truncate, python open('w'), rm, mv), but
# a process running as YOU can chmod u+w first and then write. That one hole
# is why verify-raw.sh exists: it catches after the fact what permissions did
# not prevent. Use --hard to close the hole properly (see below).
#
# USAGE
#   scripts/seal-raw.sh              seal ./data/raw, owner-level
#   scripts/seal-raw.sh --hard       also hand the files to root, so changing
#                                    the permissions back needs your password
#   RAW_DIR=path/to/raw scripts/seal-raw.sh     seal somewhere else
#
# DO NOT use --hard inside Dropbox, iCloud, or any sync folder. The sync client
# runs as you and cannot read root-owned files; you get sync errors and
# conflicted copies. For synced projects: owner-level seal + verify-raw.sh, and
# let the sync service's version history be your restore.

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE/_raw_common.sh"

HARD=0
if [ "${1:-}" = "--hard" ]; then HARD=1; shift; fi
take_dir_arg "${1:-}"

[ -d "$RAW_DIR" ] || die "no such directory: $RAW_DIR (set RAW_DIR to point elsewhere)"

n="$(raw_files | grep -c . || true)"
[ "$n" -gt 0 ] || die "$RAW_DIR is empty — put the data in first, then seal."

# Fingerprint BEFORE sealing, while the files are still readable and writable.
say "Fingerprinting $n file(s) in $RAW_DIR …"
lift_seal
write_manifest

if [ "$HARD" -eq 1 ]; then
  say "Hard seal: handing $RAW_DIR to root (you will be asked for your password)."
  sudo chown -R root "$RAW_DIR"
  sudo find "$RAW_DIR" -type f -exec chmod 444 {} +
  sudo find "$RAW_DIR" -type d -exec chmod 555 {} +
else
  apply_seal
fi

say ""
say "Sealed.  $RAW_DIR is read-only$([ "$HARD" -eq 1 ] && echo " and root-owned")."
say "Manifest: $MANIFEST  ($n file(s))"
say ""
say "  add data ....... scripts/intake-raw.sh <file> [...]"
say "  check it held .. scripts/verify-raw.sh"
