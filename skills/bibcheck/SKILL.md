---
name: bibcheck
description: Many-agent bibliography audit. Verify each citation in a .bib file by spawning narrow-focus agents that confirm DOI/URL and cross-check that all fields belong to the same paper. Catches mixed-up entries (one paper's title with another's authors), wrong years, journal misattributions, and unverifiable references. Use when reviewing a manuscript's bibliography for accuracy before submission, after literature review, or when inheriting a .bib from a coauthor.
allowed-tools: Bash(claude*), Bash(ls*), Bash(cat*), Bash(wc*), Bash(grep*), Bash(mkdir*), Bash(cp*), Read, Write, Edit, WebSearch, WebFetch, Agent
argument-hint: '[--by-citation|--by-field] <path-to-bib-or-tex> [--max-parallel N]'
---

# Bibcheck: Many-Agent Bibliography Audit

You are running `/bibcheck` — a verification routine that audits a bibliography by spawning many narrow-focus agents, one per citation (or one per field), so each agent operates on a small task with low risk of attention decay over a long context.

## Why narrow agents

A single agent asked to audit 80 citations in one pass tends to drift: early entries get careful treatment; later entries get pattern-matched. Splitting the work — one agent per entry, or one specialist per field across all entries — keeps each agent focused on something small and verifiable. The bottleneck shifts from agent attention to orchestration, which is what cheap parallel agents are for.

See `methodology.md` for the full rationale.

## Step 0: Read your full methodology

1. Read `methodology.md` in this skill directory — it explains the gradient-decay rationale and the audit standard for both modes.
2. Confirm you understand which mode the user invoked.

## Step 1: Parse arguments

Modes:

| Argument | Mode | What it does |
|----------|------|--------------|
| `--by-citation <file>` (default if omitted) | **Per-citation** | One Agent subagent per bib entry. Each fully audits its one entry. |
| `--by-field <file>` | **Per-field** | One CLI subprocess per field (title, year, journal, authors, volume/issue, pages, DOI). Each specialist reads the whole bibliography but checks only its field. |
| `--max-parallel N` | Optional | Cap concurrent subagents/subprocesses. Default 8. |

Input file:
- `.bib` — use directly
- `.tex` — extract `\bibitem{}` blocks or read the linked `.bib` from `\bibliography{}`. If both a `.tex` and a `.bib` are in the same folder, prefer the `.bib`.

If the user invoked `/bibcheck` with no arguments, ask:
- Which mode? (per-citation is the default; per-field is for adversarial cross-checks)
- Path to the .bib or .tex?

Do not guess.

## Step 2: Set up the run directory

Create a working folder next to the input file:

```
<bib_dir>/bibcheck_<timestamp>/
  ├── input.bib              # copy of source
  ├── entries/               # split entries (one .bib per entry)
  ├── reports/               # per-agent JSON/markdown outputs
  ├── bibcheck_report.md     # final consolidated report
  └── corrected.bib          # drop-in replacement
```

The timestamped folder means re-runs do not clobber prior audits.

## Step 3a: Per-citation mode

1. **Split the .bib into per-entry files.** A robust splitter: read the .bib, walk for `@type{key,` openers, balance braces to find each entry's close, write to `entries/<key>.bib`.

2. **Launch agents in waves of `--max-parallel`.** For each entry, dispatch one Agent subagent (subagent_type: general-purpose) with the brief below.

   **CRITICAL — how to actually run them in parallel.** The Agent tool blocks until that one agent completes. The only mechanism that produces concurrent agent execution in Claude Code is emitting **multiple Agent tool calls inside a single assistant message**. To run a wave of K agents truly in parallel, the orchestrator emits K Agent tool calls in one message, waits for all K to return, then emits the next wave. A naive read of "for each entry, dispatch one" as a per-entry loop collapses to N sequential Agent calls — each blocking — and on a 19-entry bib that is ~20 minutes wall time, which is the symptom users see as "hung." Do not dispatch-then-await-then-dispatch. Batch the wave explicitly.

   Concretely: with `--max-parallel 8` on a 19-entry bib, emit 8 Agent calls in message 1, wait for all 8 to return, emit 8 more in message 2, wait, then 3 more in message 3. Three waves total, ~3–5 minutes wall time on typical web access.

   **Per-agent timeout.** Add to the brief: "If you cannot find the paper within 90 seconds of WebSearch + WebFetch effort, return status=unverifiable rather than continuing to search. A slow publisher redirect should not stall the wave." Without this, one slow DOI redirect can stall an entire wave behind its slowest member.

   The brief:

   ```
   You are auditing one bibliography entry. The entry is:

   <paste the .bib block>

   Time budget: 90 seconds for web work. If you cannot identify the paper or
   confirm its canonical fields in that window, return status=unverifiable.

   Your job:
   1. Identify the cited paper. Use WebSearch (and WebFetch if needed) to find it.
   2. Locate a canonical anchor: DOI, journal landing page URL, or author working-paper URL.
   3. Cross-check every field in the .bib block against the canonical source:
      - title, authors, year, journal/booktitle, volume, number, pages, publisher, DOI
   4. Specifically test for "field mixing" — e.g., the title belongs to one paper but the authors or year belong to another. This is the most common silent error in inherited .bib files.
   5. Output JSON to <reports/<key>.json> with:
      - status: "clean" | "corrected" | "unverifiable"
      - one_sentence: plain-language description of the paper (one sentence)
      - canonical_url: DOI or URL
      - issues: list of {field, original, corrected, reason}
      - corrected_bib: the corrected entry (or the original if status=clean)

   You do NOT modify the input file. You only write the report and the corrected entry.
   ```

3. **Final reviewer pass.** Only after all per-entry agents in all waves have returned, dispatch a single reviewer agent that:
   - Reads every `reports/*.json`.
   - Spot-checks any entry marked "unverifiable" (does a quick second WebSearch).
   - Adjudicates conflicts where a corrected field looks suspicious.
   - Writes `bibcheck_report.md` with a summary table (Clean / Corrected / Unverifiable counts) and per-entry detail.
   - Concatenates the corrected_bib fields into `corrected.bib`.

## Step 3b: Per-field mode

The point of this mode is **isolation**: each specialist agent should not see what the others are concluding. We achieve that by launching each specialist as a separate `claude -p` subprocess. Each subprocess is a fresh CLI session.

For each field in the list `[title, year, journal, authors, volume_issue, pages, doi]`:

1. Build a prompt for the specialist that contains:
   - The full input.bib content
   - The field name
   - Instructions: "For each entry in this .bib, check ONLY the {field}. Compare against the canonical paper found via WebSearch. Output JSON to stdout: a list of {key, status, original, corrected, reason}."

2. Launch the specialist via Bash:
   ```bash
   claude --dangerously-skip-permissions -p "<the specialist prompt>" > reports/field_<field>.json 2>reports/field_<field>.log
   ```

3. Run subprocesses in parallel up to `--max-parallel`. Wait for all to complete.

4. **Final reviewer pass.** A consolidator agent reads all `field_*.json`, joins by entry key, and produces:
   - `bibcheck_report.md` — disagreements across specialists are flagged (e.g., title-specialist says X, year-specialist disagrees about which paper is being cited)
   - `corrected.bib` — applies a field-level fix only if the relevant specialist flagged it AND the cross-field consensus supports the fix

## Step 4: Reconciliation Double-Check (MANDATORY)

Bibcheck's own verification is itself fallible — agents die mid-wave, splitter regexes skip unusual entry types, an agent goes off-task and audits a paper that does not match its assigned bibkey. The reconciliation step is bibcheck's built-in double-check: it proves the audit did what the audit claims to have done.

**This step runs every time, before showing the user the summary in Step 5. If reconciliation fails, the user sees the failure first — not the summary.**

### What to reconcile

For each of the five drift modes below, perform the check and record the result. Any failure becomes a Major Concern in the consolidated report and blocks the success summary.

**4a. Entry-count conservation.**

```
input_count    = number of @-entries in input.bib (count via brace-balanced scan, not just lines starting with @)
reports_count  = number of reports/*.json files
corrected_count = number of @-entries in corrected.bib
```

Required: `input_count == reports_count`. If `reports_count < input_count`, list the missing bibkeys (entries in input.bib with no corresponding `reports/<key>.json`). Each missing report is one drift event.

`corrected_count` may differ from `input_count` only if entries were explicitly marked `status: removed` with a documented reason. Otherwise `input_count == corrected_count`.

**4b. Bibkey integrity.**

For every input bibkey, verify a `reports/<bibkey>.json` exists. For every report, verify its filename matches a bibkey in input.bib. Orphan reports (file exists but no matching input bibkey) are also drift events — they suggest the splitter renamed an entry or an agent invented a key.

**4c. Bibkey-paper consistency (the off-task check).**

For each `reports/<bibkey>.json`, read the `one_sentence` field and the input.bib entry's `title` and `author` fields. Verify the one-sentence description is plausibly about the same paper the input entry claims to cite. The check is intentionally loose — a fuzzy title-match on 4+ content words plus an author-surname overlap is sufficient. The goal is to catch agents that drifted off-task and audited a different paper entirely (which happens when an agent's WebSearch returns the wrong top result and the agent does not realize the .bib entry was about something else).

If the one-sentence description shares zero content words with the input title AND no author surnames overlap, flag as `bibkey_paper_mismatch`. This is a serious drift event — the agent's correction is suspect because the agent was looking at the wrong paper.

**4d. Status accounting.**

Required: `count(status="clean") + count(status="corrected") + count(status="unverifiable") + count(status="removed") == reports_count`. Any report with a missing or unrecognized status is a drift event.

**4e. Wave completeness.**

If the run logged wave dispatch counts (e.g., wave 1: 8 entries assigned, wave 2: 8, wave 3: 3), verify each wave returned the expected number of reports. A wave that dispatched 8 agents but only produced 7 reports indicates a silent agent death. Check the per-agent log files in `reports/` for any zero-byte or partial outputs that would point to the failed agent.

### Where to record the reconciliation

Write `reports/reconciliation.md` with the five checks, their pass/fail verdicts, and the list of any drift events. The consolidated `bibcheck_report.md` (produced by the final reviewer in Step 3a/3b) **must include the reconciliation results in its summary header.**

If any of 4a–4e fails, the consolidator marks the audit `RECONCILIATION FAILED` and the final summary in Step 5 leads with that — not with the clean/corrected/unverifiable counts.

### Why this is mandatory, not optional

The whole point of bibcheck is that the user trusts a single "Clean: N" number to be true. If 80 went in and 78 got audited, the user has no way to know which 2 were never checked — and the corrected.bib will look complete because the missing entries pass through unmodified. That is the same shape as sample drift in `/referee2 drift`: a silent failure that looks like success. Reconciliation is the structural defense.

## Step 5: Present the result to the user

If reconciliation passed, show the user:

```
bibcheck complete.

  Clean:        N entries
  Corrected:    M entries (see bibcheck_report.md)
  Unverifiable: K entries (need human eyes)

  Reconciliation: PASSED  (see reports/reconciliation.md)

Drop-in replacement: corrected.bib
Full audit:          bibcheck_report.md
```

If reconciliation failed, lead with the failure — do not show the clean/corrected/unverifiable counts as if the audit were successful:

```
bibcheck RECONCILIATION FAILED.

  Drift events: D  (see reports/reconciliation.md)

  - 4a entry-count: input=80, reports=78, corrected=80
    missing bibkeys: smith2019, jones2021
  - 4c bibkey-paper mismatch: 1 entry (lee2020)

The audit is incomplete. Re-run bibcheck on the missing bibkeys, or re-dispatch
the lee2020 agent before relying on the corrected.bib output.
```

Do not auto-overwrite the user's source `.bib`. They review, then move `corrected.bib` into place themselves.

## Defaults and tone

- Default mode is **per-citation** unless the user asks for `--by-field`.
- Default `--max-parallel` is **8**. Bump on request.
- This is a verification skill — never *write* citations from scratch. Only audit and correct.
- If a citation is genuinely unverifiable (paywalled, dead URL, ambiguous match), say so. Do not invent a DOI.

## When to suggest the other mode

After per-citation completes, if 3+ entries came back as unverifiable, suggest the user re-run with `--by-field` for those specific entries — a field-specialist sometimes catches what a citation-generalist missed (e.g., a wrong year hiding behind a correct title).
