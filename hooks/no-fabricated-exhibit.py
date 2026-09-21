#!/usr/bin/env python3
"""
no-fabricated-exhibit.py — PreToolUse hook. Blocks producing an EXHIBIT (a figure/table written
to output/figures|tables via ggsave/savefig/etc.) from FABRICATED data, UNLESS it is an acknowledged
Monte Carlo. Enforces the data-provenance RULE OF LAW: never present a number/figure that doesn't
trace to REAL, unmodified data — including "teaching" figures.

Incident it prevents (2026-07-17): a teaching slide bound for a reviewer drew illustrative
SYNTHETIC (made-up) series with a footnote. It passed DCAS and the raw-data hook because it
came through a FIGURE SCRIPT (the exposition door), not through data/raw/. This hook guards that door.

TWO ARMS (registered on both matchers in settings.json):
  Arm W  Edit|Write|MultiEdit — scan the NEW CONTENT of any .py/.R exhibit script being written.
  Arm B  Bash — when the command RUNS a named script (python[3] file.py, Rscript file.R,
         R CMD BATCH file.R), READ that script from disk and scan it. This closes the two round-1
         (2026-08-26) red-team defeats: (1) a fabricating script placed OUTSIDE code/ was never
         inspected (Arm W now path-agnostic), and (2) a script written via a Bash heredoc + run was
         invisible to the Write arm (Arm B now reads and scans the executed file).

Honest scope (all deliberate, and confirmed limits by the 2026-08-26 red team):
  - Fabrication is detected by TELL-TALE WORDS (synthetic/illustrative/made-up/fabricated/dummy/
    placeholder/fake/mock) alongside a data-GENERATION signal (rnorm/np.random/etc.). This is a
    conscious-pause TRIPWIRE, not a proof of honesty. It will NOT catch: a hardcoded fake array with
    no RNG and no tell-word; a fabrication synonym not on the list ("hypothetical"/"stylized"); or a
    FALSELY self-declared Monte Carlo. Those residuals stay HUMAN + the deck/canon hooks. Fabrication
    is intent + provenance, which is not decidable from a script's text; the real guarantee is that
    every decked exhibit traces to real data through the wired pipeline.
  - Monte Carlo is the ONE carve-out: a '# MONTE CARLO' / '# SIMULATION' header, or a
    sim/power/permutation/placebo/bootstrap/RI/conformal filename, is allowed through.
  - "synthetic control" (and synth/augsynth/synthdid) is EXCLUDED from the trigger: legitimate term.
  - Infra files (~/.claude/, /hooks/, site-packages, node_modules, .git) are NEVER scanned — the
    hook's own source contains every trigger word, so scanning it would block editing the hook itself.

Fail-open on any error.
"""
import json, os, re, sys

MUTATING = {"Edit", "Write", "MultiEdit"}
# any python/R script, ANY directory (Arm W is now path-agnostic — round-1 gap 1).
SCRIPT_RE = re.compile(r"\.(py|R)$", re.I)
# never scan infra / the hook's own source / vendored code (prevents self-trigger + noise).
SKIP_RE = re.compile(r"[/\\]\.claude[/\\]|[/\\]hooks[/\\]|site-packages|node_modules|[/\\]\.git[/\\]", re.I)
EMITS_RE = re.compile(r"ggsave|savefig|plt\.save|pdftoppm|output/figures|output/tables", re.I)
FAB_RE = re.compile(
    r"\bsynthetic\b|\billustrative\b|for illustration|\bmade[\s\-_]?up\b|\bfabricat|"
    r"\bdummy[\s_]?data\b|\bplaceholder[\s_]?data\b|\bfake\b|\bmock[\s_]?data\b",
    re.I,
)
SYNTH_CONTROL_RE = re.compile(
    r"synthetic\s+control|synthetic\s+did|synth[\s_]?did|augsynth|\btidysynth\b|"
    r"multisynth|\bsynth\b|synthetic\s+counterfactual",
    re.I,
)
MC_HEADER_RE = re.compile(
    r"#\s*(MONTE\s*CARLO|SIMULAT|placebo\s+draws|null\s+distribution|randomization\s+inference)",
    re.I,
)
MC_NAME_RE = re.compile(
    r"power|_sim|montecarlo|monte_carlo|permut|placebo|randomiz|conformal|boot|_mc\b|_ri\b", re.I
)
GEN_SIGNAL_RE = re.compile(
    r"\brnorm\b|\brunif\b|\brbinom\b|\brpois\b|\brgamma\b|\brbeta\b|\brexp\b|"
    r"np\.random|numpy\.random|\.normal\(|\.uniform\(|\.randint\(|\brandom\.|"
    r"\bmake_blobs\b|\bmake_classification\b|\bfaker\b|\bFaker\b",
    re.I,
)
# Arm B: pull the script file(s) out of an interpreter invocation.
RUN_SCRIPT_RE = re.compile(
    r"(?:python[0-9.]*|Rscript)\s+(?:-[^\s]+\s+)*([^\s;|&<>]+\.(?:py|R))"
    r"|R\s+CMD\s+BATCH\s+(?:-[^\s]+\s+)*([^\s;|&<>]+\.R)",
    re.I,
)


def new_content(tool, ti):
    if tool == "Write":
        return ti.get("content", "") or ""
    if tool == "Edit":
        return ti.get("new_string", "") or ""
    if tool == "MultiEdit":
        return "\n".join(
            e.get("new_string", "") for e in (ti.get("edits") or []) if isinstance(e, dict)
        )
    return ""


def would_block(content, path):
    """Return the offending fab-word if this content is a fabricated exhibit, else None."""
    if MC_NAME_RE.search(os.path.basename(path or "")):
        return None  # labeled simulation script by name -> allowed
    if not EMITS_RE.search(content):
        return None  # not an exhibit producer
    if MC_HEADER_RE.search(content):
        return None  # acknowledged Monte Carlo -> allowed
    scrubbed = SYNTH_CONTROL_RE.sub(" ", content)  # protect "synthetic control" vocabulary
    m = FAB_RE.search(scrubbed)
    if not m:
        return None
    if not GEN_SIGNAL_RE.search(scrubbed):
        return None  # tell-word without a generator -> documented residual, allow
    return m.group(0)


def block(hit, path, via):
    sys.stderr.write(
        "BLOCKED by no-fabricated-exhibit hook (data-provenance RULE OF LAW).\n"
        f"This exhibit-producing script contains synthetic/illustrative-data language ('{hit}') "
        "and writes to output/.\n"
        "Never present a figure/number that does not trace to REAL, unmodified data — including "
        "'teaching' figures (the 2026-07-17 fabricated-teaching-slide incident). A footnote is not a defense.\n"
        "  -> Draw the exhibit from real data in data/raw|derived (the chain raw -> code -> exhibit); or\n"
        "  -> if this is a labeled Monte Carlo (size/power sim, RI, placebo/bootstrap cloud), add a "
        "'# MONTE CARLO' header or name the script with a sim/power/permut/boot tag.\n"
        "If the user has explicitly asked to synthesize anyway, STOP and ask them verbatim: "
        '"Are you sure?" and wait for confirmation before proceeding.\n'
        f"    {via}: {path}\n"
    )
    sys.exit(2)


def candidate_scripts(command, cwd):
    """Every script file referenced by an interpreter invocation in a Bash command."""
    out = []
    for m in RUN_SCRIPT_RE.finditer(command or ""):
        tok = m.group(1) or m.group(2)
        if not tok:
            continue
        for cand in (tok, os.path.join(cwd, tok) if cwd else None):
            if cand and os.path.isfile(cand):
                out.append(cand)
                break
    return out


def main():
    try:
        ev = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    tool = ev.get("tool_name", "")
    ti = ev.get("tool_input") or {}

    # --- Arm W: writing a script (path-agnostic .py/.R) ---
    if tool in MUTATING:
        path = ti.get("file_path") or ""
        if not path or not SCRIPT_RE.search(path) or SKIP_RE.search(path):
            sys.exit(0)
        hit = would_block(new_content(tool, ti), path)
        if hit:
            block(hit, path, "file")
        sys.exit(0)

    # --- Arm B: running a named script via the shell ---
    if tool == "Bash":
        cwd = ev.get("cwd") or os.getcwd()
        for spath in candidate_scripts(ti.get("command", ""), cwd):
            if SKIP_RE.search(spath):
                continue
            try:
                content = open(spath, "r", errors="ignore").read()
            except Exception:
                continue  # fail-open on unreadable file
            hit = would_block(content, spath)
            if hit:
                block(hit, spath, "runs")
        sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()
