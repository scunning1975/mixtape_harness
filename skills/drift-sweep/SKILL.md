---
name: drift-sweep
description: Session-opening report with two parts. (1) Where were we — a brief continuity snapshot for picking up after a terminal close. (2) Drift — a discrepancy report flagging claims unsupported by current pipeline output, orphaned figures, stale memories, contradictions between CLAUDE.md / narrative.md / cards / scratch, and references to files no longer present. Replaces "read all markdowns" with both continuity and verification in one gesture.
allowed-tools: Read, Bash(ls*), Bash(stat*), Bash(find*), Bash(wc*), Bash(grep*), Bash(rg*), Bash(git*), Glob, Grep
argument-hint: '[optional: specific scope, e.g. "cards only" or "since last week"]'
---

# Drift-Sweep: Continuity + Discrepancy Report

You are the **Drift-Sweep**. Your job is what "read all markdowns" pretends to be — but isn't.

When Scott opens a session and asks Claude to read the markdowns, he is doing two things at once: **catching up** (where was I, what was in flight when the terminal closed) and **verifying** (do the documents still match the pipeline). The first is necessary; without it he can't act. The second is what comprehension-by-reading misses entirely. Documents rot. Cards/INDEX.md keeps a claim that the pipeline no longer supports. Memory references a file that was deleted. CLAUDE.md says X; narrative.md says Y. Scratch ideas point at suggested tasks that were completed but never crossed off. Figures sit in `output/figures/` that no card or narrative cites.

This skill produces both — a brief **Where were we** snapshot first, then the **Drift** mismatch list. Same gesture Scott already makes at session start; richer output.

---

## When to Invoke

- At the start of any session that would otherwise begin "please read all markdowns and get caught up."
- After a long break (≥1 week) where filesystem state may have drifted from documented claims.
- Before a major writeup pass — you want to know what the documents claim that the pipeline no longer earns.
- Before a meeting or audit where someone external will read the artifacts.

If the project is fresh (≤3 days old) or the documents are still being authored, this is overkill — just read.

---

## What "Drift" Means Here

Five categories of rot, ranked by danger:

1. **Unearned claims.** A document asserts a fact that the current pipeline output does not establish. Example: `cards/INDEX.md` says "donut falsification kills the spike," but no figure in `output/figures/` was generated after the donut script's last edit.

2. **Contradictions across documents.** CLAUDE.md, narrative.md, cards, and scratch say different things about the same fact. Example: CLAUDE.md says treatment is Feb 13; narrative.md says Feb 8.

3. **Orphaned artifacts.** A figure or table exists in `output/` but is not referenced by any card, narrative, or deck. Either it should be cited or it should be retired.

4. **Dangling references.** A document or memory mentions a file path, function, or memory entry that does not exist. The world has moved; the reference has not.

5. **Stale outputs.** A figure or table predates its source script's last edit. The artifact is older than the code that produces it — almost always means it should be re-run.

---

## The Protocol

### Step 0: Where were we (continuity snapshot)

This step exists because Scott's terminal closes and he needs to pick up. Keep it brief — three to six bullets, no prose. Goal: orient him in 10 seconds, not summarize the project.

Build the snapshot from filesystem signals, not document contents:

1. **Most recently touched files** (last ~24–72h). Run `find . -type f -newer <ref> -not -path './.git/*' -not -path './data/raw/*'` or `ls -lt` on the live directories (`scripts/`, `cards/`, `scratch/`, `narrative.md`, `output/`, `decks/`). The 5–10 newest files name the live front.
2. **Open scratch ideas.** Read the top of `scratch/` (newest entries — reverse-chronological). Anything marked "in progress," "next," "TODO," or with a recent suggested-task that isn't crossed off goes here.
3. **In-flight cards.** Anything in `cards/` whose front says "draft," "WIP," or whose back has unfilled bullets / `??` placeholders.
4. **Uncommitted changes** (if a git repo). `git status -s` and `git diff --stat HEAD` — the changes show what was in flight when the terminal closed. Note any large unstaged hunks; those are the work that wasn't saved to a checkpoint.
5. **Last courtroom / referee2 / blindspot output.** Newest file in `correspondence/` if present. The last audit's verdict often names the next move.
6. **Backstop: the last few entries from this session's transcript.** If `~/.claude/projects/<project-slug>/` has recent .jsonl files, look at the tail of the most recent one to pick up the very last thread (what was Claude in the middle of when the terminal closed).

Output as the **Where were we** block — see report template below. Do this *before* the drift checks; the snapshot is what Scott reads first to decide whether to even run the rest.

### Step 1: Map the scaffolding

Identify the project's "documented claims" surface. Default targets, in order:
- `CLAUDE.md` (project root)
- `narrative.md` if present
- `cards/INDEX.md` and individual files in `cards/`
- `scratch/` (recent ideas, especially with "suggested task" markers)
- `checklists/` (especially `did_checklist.md`)
- `correspondence/referee2/` (recent audit reports)
- Memory: `~/.claude/projects/<project-slug>/memory/MEMORY.md` and the files it points to

Identify the "produced artifacts" surface:
- `output/figures/`
- `output/tables/`
- `data/clean/`, `data/derived/`
- `decks/` (built PDFs)

Identify the "machinery" surface:
- `scripts/python/`, `scripts/r/`, `scripts/stata/`

If the user passed a scope argument, narrow to it. Otherwise: full sweep.

### Step 2: Build a fact ledger from the documents

Read the scaffolding documents. Extract every concrete claim that could be checked against the filesystem:
- "Figure X shows Y" → does `output/figures/X.{pdf,png}` exist?
- "Script Z produces output W" → does Z exist; does W exist; is W newer than Z's last edit?
- "Memory says file F at path P" → does P exist?
- "Card C cites figure G" → does G exist; is G referenced anywhere else?
- "Narrative claims result R" → can you find a card backing R; can you find an output backing the card?

Do not interpret yet. Just collect.

### Step 3: Run the five drift checks

**Unearned claims.** For each empirical claim in cards/narrative, find the figure or table that backs it. If none exists, flag. If one exists but is older than the script that should have produced it (`stat`), flag as stale.

**Contradictions.** Cross-read CLAUDE.md, narrative.md, cards/, and scratch/ for the same fact. Treatment date, sample size, geographic level, sentiment definition, primary outcome — these are recurring contradiction targets in this project. Quote both sides verbatim.

**Orphans.** List every figure and table in `output/`. For each, search the documents (cards, narrative, decks, scratch) for a reference. Anything cited zero times is an orphan. Report the file's mtime so Scott can decide if it's recently produced (decide what to do with it) or old (probably retire).

**Dangling references.** For every file path or function name mentioned in the documents and memory, verify it exists. Report each that does not.

**Stale outputs.** For each `output/figures/*.{pdf,png}` and `output/tables/*.{tex,csv}`, identify its likely producing script (common conventions: filename match, mention in docstring, declared inputs/outputs at top of script). Compare mtimes. Flag any output older than its producer.

### Step 4: Memory check

Read `~/.claude/projects/<this-project>/memory/MEMORY.md` and each linked file. For each memory:
- Does any file path it names still exist?
- Does any deadline it cites still lie in the future relative to today?
- Does any "Why" or "How to apply" still reference a still-existing constraint?

Flag memories that have rotted. Suggest update or removal. Do not edit memory yourself unless Scott asks.

### Step 5: Git sanity (if in a git repo)

If `git status` is available:
- Uncommitted changes that touch documents claim-bearing files (CLAUDE.md, narrative.md, cards/) — note them; the documented state may not match what's on disk.
- Files newer than the latest commit but referenced as "shipped" or "approved" — flag.

---

## The Report

Two parts. **Where were we** comes first — short, factual, oriented at picking up. **Drift** comes second — the mismatches Scott is here to react to. Lead with continuity so he can act even if drift is empty; lead with drift inside the second half so the gaps don't get buried.

```
## Drift Report
**Project:** [path]
**Date:** YYYY-MM-DD
**Scope:** [full sweep | narrowed: ...]

---

### Where were we (continuity)
- **Last touched** (most recent first): `path/a` (mtime), `path/b` (mtime), ... [5–10 files]
- **In-flight scratch:** "[top 1–3 unresolved scratch entries — verbatim or near-verbatim, with file:line]"
- **In-flight cards:** [card titles flagged WIP/draft, or "(none)"]
- **Uncommitted changes:** [file count + one-line summary, or "(clean)" / "(not a git repo)"]
- **Last audit:** [path to most recent referee2/blindspot/courtroom output, with its verdict] or "(none recent)"
- **Best guess at the live thread:** one sentence — what Scott was probably doing when the terminal closed. This is a guess; mark it as such.

---

### 🔴 Unearned claims (document asserts X; pipeline does not establish X)
1. [doc:line] claims "..." — no backing figure/table found, OR backing artifact `path` is older than its producer `script`. Re-run or downgrade the claim.
2. ...

### 🔴 Contradictions (documents disagree on the same fact)
1. CLAUDE.md says: "..." (line N). narrative.md says: "..." (line M). Reconcile.
2. ...

### 🟡 Stale outputs (artifact older than its producer)
1. `output/figures/foo.png` (mtime: ...) older than `scripts/python/03_descriptive.py` (mtime: ...). Re-run.
2. ...

### 🟡 Orphans (in output/, cited nowhere)
1. `output/figures/bar.pdf` (mtime: ...) — not in cards, narrative, scratch, or decks. Cite or retire.
2. ...

### 🟡 Dangling references (document mentions file/path that does not exist)
1. [doc:line] references `path/that/is/gone.csv` — file not present. Update or remove the reference.
2. ...

### 🟢 Stale memories (memory entry references vanished file or expired deadline)
1. `memory/foo.md` references `path/no/longer/here`. Update or remove.
2. ...

### Suggested first action
The single highest-leverage fix to start with. Usually a contradiction or an unearned claim — these damage the narrative most directly.
```

Use 🔴 for things that would make a reader think the project says something it doesn't actually establish. Use 🟡 for hygiene that doesn't yet damage claims. Use 🟢 for housekeeping.

If a category is empty, write "(none)". Do not pad.

---

## What Drift-Sweep Is Not

- Not "read all the markdowns and tell me where we are." That's a status summary; this is a discrepancy report.
- Not `/referee2` — Referee 2 audits the methodology and the code. Drift-Sweep audits whether the documents and outputs still agree with each other.
- Not `/blindspot` — Blindspot audits Scott's perception of a single output. Drift-Sweep audits the consistency of the project's documented state across many outputs.
- Not a verification of correctness — a figure that exists and is up-to-date passes Drift-Sweep even if the regression behind it is wrong. Correctness is `/referee2`'s job.

---

## Origin

Built June 7, 2026, alongside `/refuter`, after a usage analysis revealed that Scott's session-opening "read all markdowns" pays a re-grounding tax that produces comprehension but not verification. Same gesture, different output: instead of absorbing what the documents say, Scott opens by reacting to what doesn't match. The skill exists because reacting-to-drafts is how Scott thinks — so the right session-opener is one that hands him a list of things to react to, not a summary to absorb.
