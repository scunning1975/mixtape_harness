#!/usr/bin/env python3
"""
protect-raw-data.py — PreToolUse hook. Blocks Edit/Write/MultiEdit/NotebookEdit whose target
resolves into a data/raw/ directory. Raw source data is IMMUTABLE (provenance RULE OF LAW / DCAS #2).

Deliberately MINIMAL (2026-08-24, after a 3-agent red team broke the bigger version):
this is the FAST, EXPLANATORY top layer only. It catches the modal honest mistake — the agent
reaching for Edit/Write on a raw file — and hands back a sentence instead of a cryptic errno.
It is NOT the wall. The wall is the kernel seal (root:wheel, dir 555 / files 444) + a hash
manifest checked every pipeline run + an offline backup.

Two arms were TRIED AND REMOVED: a Bash "guard the guard" (chmod/mv/redirect matching) and a
content-scan of .do/.R/.py bodies. Both were textual, and a constructed path defeats any textual
matcher by construction — while the matching false-positived on Claude's own read-only commands
(a top friction source). Once the vault is root-owned, the KERNEL is the guard-the-guard, so those
arms bought illusory protection at real cost. Gone.

Structural, not textual: the target path is a named field. We resolve it with realpath (collapses
parent symlinks and ..) and match case-insensitively (macOS APFS is case-insensitive), so
data/RAW/ and a symlinked parent dir can't sneak past. Reading raw is always fine.
Fail-open on any parse error so a malformed event never wedges work.
"""
import json
import os
import re
import sys

MUTATING_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# A data/raw/ segment anywhere in the resolved path. IGNORECASE for case-insensitive filesystems.
RAW_RE = re.compile(r"[/\\]data[/\\]raw[/\\]", re.IGNORECASE)


def target_path(tool_input):
    if not isinstance(tool_input, dict):
        return None
    return tool_input.get("file_path") or tool_input.get("notebook_path")


def resolve(path):
    """Absolute, symlink- and ..-resolved, so a parent symlink or case variant can't hide raw/."""
    try:
        return os.path.realpath(str(path))
    except Exception:
        return str(path)


def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # fail-open: never wedge the session on a parse error

    if event.get("tool_name", "") not in MUTATING_TOOLS:
        sys.exit(0)

    path = target_path(event.get("tool_input", {}))
    if not path:
        sys.exit(0)

    if RAW_RE.search(resolve(path)):
        sys.stderr.write(
            "BLOCKED by protect-raw-data: this path resolves inside a data/raw/ directory, which is "
            "IMMUTABLE (provenance RULE OF LAW / DCAS #2 — raw source data is never modified). Read it, "
            "and WRITE transformed output to data/derived/ (or the project's derived dir) via a named "
            "script, so the chain real -> code -> exhibit stays traceable.\n"
            f"    attempted: {path}\n"
            "This hook is only the fast top layer; the kernel seal (root:wheel 555/444) is the wall. "
            "If a raw file genuinely must be replaced, that is a deliberate sudo intake step the maintainer runs."
        )
        sys.exit(2)  # exit 2 = block the tool call and return stderr to the agent

    sys.exit(0)


if __name__ == "__main__":
    main()
