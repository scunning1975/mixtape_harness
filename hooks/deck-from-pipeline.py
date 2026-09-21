#!/usr/bin/env python3
"""
deck-from-pipeline.py — PostToolUse(Edit|Write) hook.

Enforces the deck-from-pipeline RULE OF LAW mechanically: every analysis EXHIBIT referenced by a
deck (or manuscript) must be produced by a script that is WIRED INTO code/run_pipeline.sh.
"Exists on disk" / "ran once in chat" is NOT enough — if the runner can't rebuild it, it can't be
shown.

Incident it prevents: an entire outcome was once built ad-hoc in chat — many scripts, real
figures, stages LOCKED — with NOT ONE script wired into run_pipeline.sh, and it got decked
anyway. Caught only by human memory, not the machine. This turns that prose rule into a fence.

Why PostToolUse (not Pre): a figure reference may be ADDED by the very edit we are checking, so we
need the merged, on-disk file to see all references. The tool has already run; exit 2 surfaces the
violation to the SAME session immediately (vs. Scott's memory catching it days later).

Scope discipline (keeps false positives near zero):
  - only fires on deck files:      decks/**/*.html  or  any *.tex
  - only enforces on EXHIBIT refs: a figure path that lives in an exhibit dir
    (img/, tbl/, output/figures, output/tables, /figures/, /tables/).
    Screenshots/logos/chrome (assets/, logo*, icon*) are SKIPPED — so a conceptual
    deck referencing assets/dash_home.png never trips.
  - dynamic sprintf/f-string names (…_%s.png) handled by progressive stem matching.

Fail-open on any error so a malformed event never wedges the session.
"""
import json, os, re, sys, glob

MUTATING = {"Edit", "Write", "MultiEdit"}
DECK_RE = re.compile(r"(decks[/\\].*\.html$)|(\.tex$)", re.I)
# any figure path in the deck body
FIG_RE = re.compile(r"([A-Za-z0-9_./\-]+\.(?:png|pdf))")
# a reference counts as an EXHIBIT (enforce) only if its path hits one of these
EXHIBIT_DIR_HINTS = ("img/", "tbl/", "output/figures", "output/tables", "/figures/", "/tables/")
# never enforce on these (screenshots, chrome, template assets)
SKIP_HINTS = ("assets/", "logo", "icon", "_template", "screenshot", "dash_")
# how run_pipeline.sh invokes a script
INVOKE_RE = re.compile(r"(?:python3?|Rscript|bash|sh)\s+(?:-\S+\s+)*([^\s;|&]+\.(?:py|R|r|sh))")


def find_root(start):
    d = os.path.dirname(os.path.abspath(start))
    while d != os.path.dirname(d):
        if os.path.isfile(os.path.join(d, "code", "run_pipeline.sh")):
            return d
        d = os.path.dirname(d)
    return None


def wired_source_blob(root):
    """Concatenated source of every script INVOKED (on a non-comment line) by run_pipeline.sh."""
    runner = os.path.join(root, "code", "run_pipeline.sh")
    texts = []
    try:
        with open(runner, encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.lstrip().startswith("#"):
                    continue
                m = INVOKE_RE.search(line)
                if not m:
                    continue
                sp = m.group(1)
                cand = sp if os.path.isabs(sp) else os.path.join(root, sp)
                if os.path.isfile(cand):
                    try:
                        texts.append(open(cand, encoding="utf-8", errors="ignore").read())
                    except Exception:
                        pass
        # also count the runner's own inline commands (e.g. python3 -c "...") as "wired"
        texts.append(open(runner, encoding="utf-8", errors="ignore").read())
    except Exception:
        return None
    return "\n".join(texts)


def stems(basename):
    """Full stem, then progressively shorter prefixes (>=4 tokens), so a sprintf-built name like
    proj_outcome_permonth_fullpool_53053.png still matches its producer's format-string prefix."""
    stem = re.sub(r"\.(png|pdf)$", "", basename, flags=re.I)
    parts = stem.split("_")
    # floor at 3 tokens: a 2-token project prefix (e.g. "proj_x_") is too generic,
    # so the first distinguishing token is #3. This lets a dynamic name like
    # proj_series_february.png match its producer's f-string prefix "proj_series_".
    for k in range(len(parts), 2, -1):
        yield "_".join(parts[:k])
    yield stem  # always include the whole thing


def is_exhibit_ref(ref):
    low = ref.lower()
    if any(s in low for s in SKIP_HINTS):
        return False
    return any(h in low for h in EXHIBIT_DIR_HINTS)


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("tool_name") not in MUTATING:
        sys.exit(0)
    ti = ev.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if not path or not DECK_RE.search(path) or not os.path.isfile(path):
        sys.exit(0)

    root = find_root(path)
    if not root:
        sys.exit(0)  # no runner in this project -> not our concern, allow

    blob = wired_source_blob(root)
    if blob is None:
        sys.exit(0)  # couldn't read runner -> fail open

    try:
        deck = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        sys.exit(0)

    refs = sorted({r for r in FIG_RE.findall(deck) if is_exhibit_ref(r)})
    violations = []
    for ref in refs:
        base = os.path.basename(ref)
        if not any(s in blob for s in stems(base)):
            violations.append(base)

    if violations:
        sys.stderr.write(
            "BLOCKED by deck-from-pipeline hook (deck-from-pipeline RULE OF LAW).\n"
            "This deck/manuscript references EXHIBIT(S) that NO script wired into "
            "code/run_pipeline.sh produces, so the pipeline cannot rebuild them:\n"
            + "".join(f"    - {v}\n" for v in violations)
            + "This is the 'vibed exhibit' failure mode. Either wire the producing "
            "script into run_pipeline.sh and re-run it clean, or remove the reference. "
            "'Exists on disk' / 'ran once in chat' is not enough.\n"
            "If this is a false positive (e.g. a dynamically-named figure whose producer isn't "
            "matched), confirm with Scott and adjust the hook's scope.\n"
        )
        sys.exit(2)
    sys.exit(0)


if __name__ == "__main__":
    main()
