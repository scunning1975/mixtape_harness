---
name: sleep
description: |
  End-of-session handoff mode — the bookend to /amnesia. Writes (1) a dated
  progress log to progress_logs/ capturing what this session did, (2) an
  updated STATE.md, and (3) the next TODAY.md so tomorrow's /amnesia reads a
  clean handoff. Use when the user says "sleep", "wrap up", "end the session",
  "let's stop here", "hand off", or invokes /sleep. The point is a clean
  handoff to the next meeting: what happened, where we are, what's next.
---

# /sleep — Session-close handoff

`/amnesia` opens a session (reads state, reloads context). `/sleep` closes it (writes state, sets up the handoff). They are a matched pair: what `/sleep` writes tonight is exactly what `/amnesia` reads back tomorrow. The recurring failure mode is session amnesia — Scott loses position across sessions and reconstructs it unreliably. `/amnesia` fixes the *read*; `/sleep` fixes the *write*, so there is something faithful to read.

The goal in one line: **leave the project so the next session (Scott's, or a fresh Claude's) can pick up cold, with no memory of this conversation, and lose nothing.**

## When to invoke

- User says "sleep", "wrap up", "end the session", "let's stop here", "hand off for tomorrow", "close out", or invokes `/sleep`.
- Proactively suggest it when a working session is clearly ending (Scott says he's done for the day, or a stage/task just closed and he's stepping away).

## What it produces (three writes, in this order)

### Step 1 — the progress log (`progress_logs/YYYY-MM-DD_<slug>.md`)

The permanent dated record of THIS session. Match the house format of the most recent file already in `progress_logs/` (read it first for tone/structure). Write it from what actually happened in the conversation — not from STATE.md (that's downstream). Include:

- **A one-line status** at the top: what changed this session, and what did NOT (e.g. "analysis unchanged, infrastructure only").
- **The arc** — how the session went, the decisions made and why (the reasoning, not just the outcome — the "why" is what evaporates).
- **Files touched** — concrete paths, so the next session can find the work.
- **What's next** — the handoff, carried into STATE.md and TODAY.md below.

Naming: `YYYY-MM-DD_<short_slug>.md`. If a log for today already exists, append a session-N section or fold into it — do not overwrite the earlier session's record. Get today's date from the environment context (never guess); convert any relative dates ("yesterday") to absolute.

### Step 2 — update `STATE.md`

Bring the durable state file current per its required structure (last-updated timestamp, current objective, just-completed, in-progress, next, canonical files, open questions). STATE.md is orientation, not history — keep it under a minute to read; prune stale lines. The progress log holds the detail; STATE.md holds the position.

### Step 3 — write the next `TODAY.md` (the handoff to-do)

Write/overwrite `TODAY.md` at the project root — the SAME two-line format `/amnesia` uses and the dashboard Home card parses, but pointed at the NEXT meeting:

```markdown
# Today · YYYY-MM-DD

Stage: <which stage we'll be in next session>

Left:
- <the first thing to do next meeting>
- <second>
- <third>
```

Date it TODAY (the dashboard flags it stale once the day turns, which is the correct signal — it's last session's handoff). This is the single most important write for continuity: it's the first thing the next session sees on the Home tab and the thing `/amnesia` reads back. Make the first bullet the genuine next action, concrete enough to start on cold.

**PLAIN LANGUAGE FIRST (Scott needs a little more help than terse jargon gives him).** Each `Left:` bullet must OPEN with one plain-English sentence he'll understand cold — what we're doing and why, no jargon/filenames/acronyms — THEN the precise jargony detail in parentheses. Pattern: `- <plain sentence>. (<precise jargon>)`. A bare jargon item failed him once; lead human, follow precise. The Home card renders each bullet as a click-to-cross-off checkbox, so keep each item to ONE coherent bullet. (Same rule as `/amnesia` Step 0 — they write the same file.)

## Style discipline

- **Truth over tidiness.** Record what actually happened, including dead ends, unresolved decisions, and things left half-done. A progress log that only lists wins is a lie that costs the next session. If a gate is unmet or a diff is unreviewed, say so.
- **The "why" is the payload.** Outcomes are recoverable from the files; the reasoning behind a choice is not. Spend the words there.
- **Do not overstate completion.** "Built and verified" only if verified; "built, not yet tested" otherwise. This is the zero-error constraint applied to the handoff.
- **Gitignore note.** `TODAY.md` is disposable per-session state — projects should gitignore it (like the diff review ledger). The progress log and STATE.md ARE tracked work.

## Composition with the harness

- **/amnesia** reads STATE.md + latest progress log + TODAY.md → reloads context. **/sleep** writes all three → creates that context. Same sources, opposite direction.
- The git-diff gate (where installed): if a stage's work was committed this session but its diff not yet reviewed, `/sleep` should NOTE that in both the progress log and TODAY.md as carried-forward verification debt — it does not silently discharge it.
- `/sleep` replaces the manual "departure ritual" — writing the progress log by hand at day's end.

## Origin

Created 2026-07-09, when Scott observed that `/amnesia` always writes the day's to-do and reasoned that the natural complement is a session-close skill that writes the progress log AND the next-meeting handoff — so the open/close pair fully brackets a session. Same philosophy as amnesia: continuity, not ceremony; always writes from what actually happened.
