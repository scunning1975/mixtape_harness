#!/usr/bin/env python3
"""
no-offbook-exhibit.py — PreToolUse(Bash) hook.

Blocks drawing a FIGURE or TABLE in a shell instead of from a named script on disk. The crime:
inline code (`python -c "...savefig..."`, `Rscript -e "...ggsave..."`) or a python/R heredoc that
plots. A picture made this way has NO producer file — it can't be re-run, re-styled, audited, or
reconciled, so "you're done" cannot survive to the next session. This is the "figure made in some
shell other than a scripted file" failure Scott kept feeling as "losing the thread."

The rule, in one line: every exhibit must be born in a NAMED script in code/ (then wired into
run_pipeline.sh), never in an ad-hoc shell command.

WHAT PASSES (verified against the real run_pipeline.sh):
  - named scripts:            python3 code/x.py   |   Rscript code/y.R
  - table-card compilation:   pdflatex … t.tex    |   pdftoppm … card   (a SCRIPT already wrote
    the .tex; these just render it — not inline drawing code)
  - inline `python -c` with NO plotting call (e.g. the runner's /tmp FIPS-filter helper)
  - a genuine scratch/exploration run acknowledged with SCRATCH_RUN=1 prefixed

WHAT BLOCKS:
  - python/python3/ipython  -c "..."   whose code contains a plotting/exhibit-writing call
  - Rscript -e "..."  /  R -e "..."     whose code contains a plotting call
  - a python/R heredoc  (python <<EOF … EOF)  that contains a plotting call

Escape hatch: prefix the command with SCRATCH_RUN=1 to acknowledge a deliberate throwaway
exploration (converts a silent off-book draw into a logged, intentional one).

Fail-open on any error so a malformed event never wedges the session.
"""
import json, os, re, sys

# inline code execution flags: python -c "...", Rscript -e "...", R -e "..."
INLINE_CODE_RE = re.compile(
    r"\b(?:python3?|ipython|bpython)\s+(?:-\S+\s+)*-c\b|"
    r"\b(?:Rscript|R)\s+(?:-\S+\s+)*-e\b",
    re.I,
)
# a python/R heredoc: python <<EOF ... / Rscript <<'EOF' ...
HEREDOC_RE = re.compile(r"\b(?:python3?|Rscript|R)\b[^\n]*<<-?\s*['\"]?\w+", re.I)
# plotting / exhibit-writing calls — the signal that the inline code is DRAWING an exhibit
PLOT_RE = re.compile(
    r"savefig|ggsave|\bplt\.|pyplot|matplotlib|seaborn|\bsns\.|plotnine|"
    r"\bggplot\b|\bpdf\s*\(|\bpng\s*\(|\bjpeg\s*\(|\bsvg\s*\(|"
    r"output/figures|output/tables|\.savefig|fig\.save",
    re.I,
)


def main():
    # deliberate scratch run -> allow (logged intent, not a silent off-book draw)
    if os.environ.get("SCRATCH_RUN"):
        sys.exit(0)
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if ev.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = (ev.get("tool_input") or {}).get("command", "")
    if not isinstance(cmd, str) or not cmd.strip():
        sys.exit(0)

    is_inline = bool(INLINE_CODE_RE.search(cmd)) or bool(HEREDOC_RE.search(cmd))
    if not is_inline:
        sys.exit(0)  # a named script, pdflatex, pdftoppm, or any normal command -> allow
    if not PLOT_RE.search(cmd):
        sys.exit(0)  # inline code that does NOT plot (e.g. a csv filter helper) -> allow

    sys.stderr.write(
        "BLOCKED by no-offbook-exhibit hook: this shell command DRAWS A FIGURE/TABLE INLINE "
        "(python -c / Rscript -e / heredoc with a plotting call).\n"
        "An exhibit made in a shell has no producer file — it can't be re-run, re-styled, audited, "
        "or reconciled, so it can never be 'put to bed.' This is the 'figure made off-book, thread "
        "lost' failure.\n"
        "  -> Put the plot in a NAMED script: code/<slug>_<stage>_<purpose>.py (or .R), then run "
        "that script and wire it into code/run_pipeline.sh in dependency order.\n"
        "  -> If this is genuinely throwaway exploration (NOT an exhibit anyone will see), re-run "
        "with SCRATCH_RUN=1 prefixed to acknowledge it.\n"
    )
    sys.exit(2)


if __name__ == "__main__":
    main()
