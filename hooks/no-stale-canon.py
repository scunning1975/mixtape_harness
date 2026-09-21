#!/usr/bin/env python3
"""
no-stale-canon.py — PostToolUse(Edit|Write|MultiEdit) hook.

The certainty fence. When a stage's exhibits.md is written/edited WITH a canon-closure line
("CANON ("), this checks every exhibit entry it lists and WARNS (does not block — Scott's choice,
2026-07-29) if any exhibit is not "right and live":

  1. MISSING  — the file at the named path does not exist on disk.
  2. UNWIRED  — the producing script (the "src: code/...") is not invoked by run_pipeline.sh.
  3. STALE    — the figure file is OLDER than the script that makes it (code changed, figure
                was never re-generated) — the silent "it isn't what I thought it was" failure.

Why this exists (Scott, 2026-07-29 interview): "if I'm going to make 5x as much stuff, I need to
be 5x as sure it's right." The fear is hanging a figure on the wall and later finding it was never
made, was a stale copy, or drifted. This fence makes the canon moment TELL him the truth: every
canonized exhibit traces to a real, live, wired file — or he hears about it right then, not days
later from memory.

WARN-not-BLOCK: PostToolUse fires AFTER the write, so exit 2 surfaces the warning to the agent and
to Scott without un-writing (this IS "warn but allow"). The exhibits.md is saved; the warning names
every exhibit that isn't right-and-live so it can be fixed. Flip to a hard PreToolUse block later if
warnings get scrolled past — a one-line change.

exhibits.md entry format it parses (verified on disk):
    - `output/figures/NAME.png` — src: code/SCRIPT.py — description...
CANON trigger: the file contains a line with "CANON (".

Fail-open on any error so a malformed event never wedges the session.
"""
import json, os, re, sys

MUTATING = {"Edit", "Write", "MultiEdit"}
# an exhibit line: a `path` (backtick-quoted) followed by  — src: <script>
# the path may use a shorthand like `.../name.png/.pdf` meaning BOTH name.png and name.pdf.
ENTRY_RE = re.compile(
    r"`([^`]+\.(?:png|pdf|tex)(?:/\.(?:png|pdf|tex))*)`\s*[—-]+\s*src:\s*([^\s—-]+\.(?:py|R|r))",
    re.I,
)


def expand_paths(raw):
    """Expand a `.../name.png/.pdf` shorthand into the real file list.
    'a/b/name.png/.pdf' -> ['a/b/name.png', 'a/b/name.pdf']. A plain path returns [itself]."""
    parts = raw.split("/.")
    if len(parts) == 1:
        return [raw]
    base = parts[0]                     # 'a/b/name.png'
    stem = base.rsplit(".", 1)[0]       # 'a/b/name'
    out = [base]
    for ext in parts[1:]:               # 'pdf', ...
        out.append(f"{stem}.{ext}")
    return out
# how run_pipeline.sh invokes a script
INVOKE_RE = re.compile(r"(?:python3?|Rscript|bash|sh)\s+(?:-\S+\s+)*([^\s;|&]+\.(?:py|R|r|sh))")


def find_root(start):
    d = os.path.dirname(os.path.abspath(start))
    while d != os.path.dirname(d):
        if os.path.isfile(os.path.join(d, "code", "run_pipeline.sh")):
            return d
        d = os.path.dirname(d)
    return None


def wired_scripts(root):
    """Set of script basenames invoked (non-comment) by run_pipeline.sh."""
    names = set()
    try:
        with open(os.path.join(root, "code", "run_pipeline.sh"), errors="ignore") as f:
            for line in f:
                if line.lstrip().startswith("#"):
                    continue
                m = INVOKE_RE.search(line)
                if m:
                    names.add(os.path.basename(m.group(1)))
    except Exception:
        pass
    return names


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("tool_name") not in MUTATING:
        sys.exit(0)
    ti = ev.get("tool_input") or {}
    path = ti.get("file_path") or ""
    if not path or os.path.basename(path) != "exhibits.md" or not os.path.isfile(path):
        sys.exit(0)

    try:
        text = open(path, encoding="utf-8", errors="ignore").read()
    except Exception:
        sys.exit(0)
    if "CANON (" not in text:
        sys.exit(0)  # not a canon-closure write -> not the "done" moment, ignore

    root = find_root(path)
    if not root:
        sys.exit(0)
    wired = wired_scripts(root)

    missing, unwired, stale = [], [], []
    for raw_path, script_rel in ENTRY_RE.findall(text):
        script_base = os.path.basename(script_rel)
        script_abs = script_rel if os.path.isabs(script_rel) else os.path.join(root, script_rel)
        for fig_rel in expand_paths(raw_path):
            fig_abs = fig_rel if os.path.isabs(fig_rel) else os.path.join(root, fig_rel)
            if not os.path.isfile(fig_abs):
                missing.append(fig_rel)
                continue
            if script_base not in wired:
                unwired.append(f"{fig_rel}  (src {script_base} not in run_pipeline.sh)")
            # stale: figure older than its producing script (only if both exist)
            if os.path.isfile(script_abs):
                try:
                    if os.path.getmtime(fig_abs) < os.path.getmtime(script_abs):
                        stale.append(f"{fig_rel}  (older than {script_base})")
                except OSError:
                    pass

    if not (missing or unwired or stale):
        sys.exit(0)  # every canonized exhibit is present, wired, and live -> exhale

    msg = ["WARNING from no-stale-canon: this stage is being CANONIZED, but some exhibits are not "
           "'right and live'. The exhibits.md was saved (warn, not block) — fix these so the wall "
           "can be trusted:\n"]
    if missing:
        msg.append("  MISSING (marked canon but the file is not on disk):\n"
                    + "".join(f"    - {m}\n" for m in missing))
    if unwired:
        msg.append("  UNWIRED (no pipeline script rebuilds it — can't be regenerated):\n"
                    + "".join(f"    - {u}\n" for u in unwired))
    if stale:
        msg.append("  STALE (figure is OLDER than its script — code changed, figure did not; "
                   "re-run the script):\n"
                    + "".join(f"    - {s}\n" for s in stale))
    msg.append("This is the '5x the stuff, 5x the certainty' fence — a canonized figure must trace "
               "to a real, live, wired file. Re-generate/re-wire the flagged exhibits, or correct "
               "the exhibits.md paths.\n")
    sys.stderr.write("".join(msg))
    sys.exit(2)


if __name__ == "__main__":
    main()
