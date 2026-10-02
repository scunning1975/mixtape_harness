---
name: amnesia
description: |
  Get-me-up-to-speed mode. RECONCILES STATE.md against ground truth (git log +
  disk + checklist boxes) first — auto-fixing any factual claim that drifted —
  then produces (1) a chat summary of where the project stands and (2) a
  two-line TODAY.md (which stage + what's left today) that the dashboard's
  Home tab renders as a "Today" card. Use when the user says "amnesia", "get
  me up to speed", "where were we", "reorient me", or invokes /amnesia.
  Disposable; regenerate every invocation. ALSO supports STAGE MODE: "amnesia
  stage 2", "amnesia bite", "amnesia target" reorient on ONE checklist-stage
  canister and focus all subsequent work there.
---

# /amnesia — Reorientation

Session amnesia is the recurring failure mode of the researcher's workflow. He works conversationally and does not pre-plan in detail. Across sessions and within long sessions interrupted by tangents or breaks, he loses position in the work and reconstructs it unreliably from memory.

This skill is the orientation tool. It produces two things from current sources:

1. **A chat summary** — a 4–8 sentence in-conversation reload of where things stand. Read first; it's the primary output.
2. **A `TODAY.md` to-do** at the project root — a two-line "today" note (which stage we're in + what's left to do today). ALWAYS written on every invocation. The dashboard's Home tab renders it as a "Today" card, and the two lines also go into the chat summary. See "Step 0 — the TODAY.md to-do" below.

Always reads from current sources; never gets stale. Disposable; each invocation overwrites.

> **STATE.md is the ONE thing that can lie.** Git, disk, and the checklist boxes cannot lie about what happened — a commit exists or it doesn't, a file is built or it isn't, a box is `[x]` or `[ ]`. STATE.md is the only orientation source written by a fallible hand, so it is the only one that drifts. It drifts most dangerously when a session keeps working *past* the last time STATE.md was touched (this bit us 2026-07-10: STATE.md's header still read "dose NOT built, blocked on a live fork" while four later commits that same day had resolved the fork, built the dose panel, and made a 14-slide deck — `/amnesia` then faithfully replayed a world that no longer existed). **The fix is Step -1 below: amnesia now RECONCILES STATE.md against ground truth and auto-fixes drifted facts BEFORE it trusts or reports anything.** Amnesia is no longer "trust the note"; it is "trust the note, verify it against git+disk, fix it, then report."

> **Retired 2026-07-09:** the old HTML reorient deck (`reorient/index.html`, served at `/reorient`) was dropped. `/amnesia` no longer generates it, and the dashboard no longer serves it. The visual reload now lives on the dashboard's **Home** tab (the "Today" card from `TODAY.md` above the verification scale). Chat summary + `TODAY.md` are the whole output.

## When to invoke

- User says "amnesia", "get me up to speed", "where were we", "reorient me", "what's going on now", or invokes `/amnesia` directly.
- Optionally, on session start when STATE.md is large enough that a chat summary alone won't reload context.

## Step -1 — RECONCILE STATE.md against ground truth (do this FIRST, every full-mode invocation)

Before reading STATE.md *as truth*, verify its factual claims against the things that cannot lie. This runs on every full-mode invocation and is cheap. (Stage mode reconciles more narrowly — see the stage-mode note below.)

**The tripwire (always run it first — it catches most drift in one line):**

```bash
# Newest commit time vs STATE.md's own "Last updated" stamp.
git -C <project> log -1 --format="%ci %h %s"        # newest commit
grep -m1 "Last updated" STATE.md                     # what STATE thinks "now" is
```

**If any commit is newer than STATE.md's `Last updated:` stamp, STATE.md is behind by definition** — the session kept working past the last STATE.md edit. Do NOT trust STATE.md's factual claims until reconciled. (If STATE.md is *at or ahead of* the newest commit, drift is unlikely; a light check is still worth one pass.)

**Then verify the specific claims STATE.md makes.** Read STATE.md, and for every *factual* claim it makes about the state of the work, check it against ground truth:

| STATE.md claim of the form… | Verify against… |
|---|---|
| "X is NOT built / not yet done" | does the file exist on disk? (`ls`, `find`) — a "not built" that IS on disk is drift |
| "blocked on decision D / live fork" | `git log --oneline` since the stamp — a commit message resolving D means it's decided |
| "Step N open / boxes unticked" | the `[x]`/`[ ]`/`[~]` states in `analyses/<slug>/checklist.md` |
| "ACTIVE_STAGE = …" / "in stage N" | the actual `analyses/<slug>/ACTIVE_STAGE` file |
| "no exhibits / no figures yet" | `ls output/figures/ output/tables/` |
| "uncommitted / N commits behind" | `git status --short` and `git log` |

Keep it to a handful of targeted checks driven by what STATE.md actually asserts — do NOT scan the whole project. The point is to catch the specific lies STATE.md is telling, not to re-audit everything.

**The reconcile rule — facts vs. judgment ("auto-fix facts, flag them"):**

```
Facts    (built? committed? box ticked? which stage? fork resolved per a commit?)
   → git + disk WIN. Auto-correct STATE.md to match, and say out loud in chat
     exactly what you changed and why (cite the commit hash / the file on disk).

Judgment (WHY we're blocked, what worries us, an unresolved caveat, a fit we don't
          trust, a decision the researcher owes that no commit has settled)
   → STATE.md / the researcher WIN. PRESERVE this verbatim. Never overwrite a human
     judgment from a commit message — a commit says what was done, not whether
     the researcher is satisfied it's right.
```

**When you auto-fix STATE.md:** rewrite only the drifted *factual* claims (update the `Last updated:` stamp, correct "not built"→"built at <path>", move a resolved fork out of the "LIVE DECISION" block into "Just completed" with the commit hash, re-point ACTIVE_STAGE/step language to reality). Leave the narrative, the reasoning, the caveats, and any genuinely-open human judgment untouched. Then the chat summary and TODAY.md are built from the **corrected** STATE.md — so they never replay a dead world. **Always report the corrections in chat** (a short "Reconciled — STATE.md said X, git/disk show Y, fixed" block) so the researcher sees what moved.

If STATE.md turns out to be accurate (no drift), say so in one line ("STATE.md reconciles clean against git+disk") and proceed — the check is not noise, a clean pass is a real result.

## What to read

After Step -1, the reading order (STATE.md is now the *reconciled* version):

1. **`STATE.md` at the project root.** Required. If it does not exist, halt and tell the user to create it first (per the CLAUDE.md STATE.md rule). (Already read during Step -1; use the corrected version.)
2. **The most recent file in `audits/`.** The newest file by mtime that matches `audits/YYYY-MM-DD_*.md`. Use it to populate the "how we got here" slide.
3. **Optionally, `correspondence/referee2/`** if the most recent file there is newer than the most recent audits/ file. Audits and referee2 reports are both legitimate "history" sources.

Do NOT scan the whole project. The point is fast orientation. STATE.md (reconciled) should already be the curated current state; the audit log adds one slide of recent context.

## STAGE MODE (amnesia a single checklist stage / canister)

When the user names a **checklist stage** — by number ("amnesia stage 2"), by nickname ("amnesia bite", "amnesia target", "amnesia covariates"), or any phrasing that points at one stage ("get me up to speed on the bite") — DO NOT reorient the whole project. Reorient on that **one stage canister** and then **focus all subsequent work there.** This is the read-half of the "lock the door, be in the room" rule from CLAUDE.md ("Checklist Stages Are Canisters").

### Resolve the stage (whatever the user says → one room)

Stages live at `analyses/<slug>/stages/<NN_name>/`. Map the user's words to a folder, generously:
- a number → the `NN_` prefix (2 → `02_bite`).
- a nickname → the stage's known alias. The canonical map: 0 packages · 1 target · **2 bite / assignment / treatment / selection / rollout** · 3 covariates / balance · 4 sample shares / N · 5 outcome trends · 6 power / MDE · 7 estimator / event study · 8 falsification / sensitivity · 9 rerun / debug.
- "bite", "assignment mechanism", "treatment", "selection" ALL resolve to stage 2. Be liberal: the user's intent is a room, not a string match.
- If more than one analysis has that stage, use the one whose `analyses/<slug>/ACTIVE_STAGE` matches, else ask which slug (only if genuinely ambiguous).

### Reconcile (stage mode)

Run a narrower version of Step -1 scoped to the stage: `git log --oneline` since the stage's findings/checklist were last touched, and check the stage's `checklist.md` box states and any files its `todo.md`/`findings.md` claim exist-or-not. Same rule — facts (built/committed/ticked) auto-fix in the stage files; human judgment is preserved. Flag what you changed in chat.

### What to read (stage mode)

Only the canister's four files, in this order:
1. `findings.md` — what we learned here (the most important; lead with it).
2. `todo.md` — open actions in this room.
3. `ideas.md` — live ideas native to this room.
4. `exhibits.md` — the figures/tables this stage produced (keep/update/discard state).
Plus the stage's section in `analyses/<slug>/checklist.md` for the gate state, and `decisions.md` if the stage references it. Do NOT read the whole project.

### What to produce (stage mode)

1. **Set focus.** Write the stage to `analyses/<slug>/ACTIVE_STAGE` (so the dashboard's Stages hallway glows the right room and you are now "in" it). State plainly in chat: "Now in the <slug> · <stage> room — I'll keep work scoped here."
1b. **Write `TODAY.md`** (as in Step 0 of full mode), but scoped to this stage: `Stage:` names this room; `Left:` comes from this stage's `todo.md`. Always do this in stage mode too.
2. **Chat summary**, stage-scoped:
   ```
   In the <slug> · <NN_name> room (stage <n> — <title>):

     Findings so far: <2-3 lines from findings.md>
     Open to-do:      <the open boxes from todo.md, terse>
     Live ideas:      <ideas.md, 1-2 lines>
     Exhibits:        <count + any flagged update/discard>
     Gate state:      <this step's grade from the checklist: done/partial>
   ```
3. **Chat summary + TODAY.md are the reload** in stage mode — no other artifact.
4. **Then stay in the room.** For the rest of the conversation, scope ideas/edits/exhibits to this stage; new ideas go in this room's `ideas.md`, new actions in its `todo.md`. If the user pivots to another stage, switch ACTIVE_STAGE and say so.

## What to produce

### Step 0 — write `TODAY.md` (always, before the chat summary)

On EVERY invocation (full mode and stage mode), write/overwrite `TODAY.md` at the project root. It is deliberately tiny — two things only: **which stage we're in**, and **what's left to do today**. Derive both from STATE.md (§4 In progress → the stage; §5 Next → what's left) and, in stage mode, from the active stage's `todo.md`. Exact format the dashboard's Home card parses:

```markdown
# Today · YYYY-MM-DD

Stage: <NN · nickname — one clause of context, e.g. "02 · bite (treatment construction) — dose NOT built yet">

Left:
- <first thing left to do today>
- <second>
- <third — keep it to the handful that actually matters today>
```

Rules:
- The `# Today · <date>` line carries today's date (the dashboard uses it to flag a stale card).
- `Stage:` is ONE line. `Left:` is a short bullet list — the day's real remaining work, not the whole backlog.
- **PLAIN LANGUAGE FIRST (the researcher needs a little more help than the terse jargon gives him).** Each `Left:` item must OPEN with one plain-English sentence a tired the researcher re-reading cold will instantly understand — what we're actually doing and why, no jargon, no file names, no acronyms. THEN, in parentheses, the precise jargony version (file names, column names, method terms) is welcome and encouraged for when he's back in the work. Pattern: `- <plain sentence>. (<precise jargon detail>)`. A bare jargon item like "Verify the data WIRING (ring_classified.csv vs ring_articles_to_fips.csv), do they join?" FAILED him once — lead with "Look at the two raw files with our own eyes and see if they fit together" and put the file names in the parenthetical. This applies to the chat summary's "Left:" lines too.
- The Home card renders each `Left:` bullet as a click-to-cross-off checkbox; keep each item to ONE bullet (the plain sentence + its parenthetical) so a check crosses off a whole coherent task.
- If the project isn't a DiD/stage project (no stages), `Stage:` may name the current phase instead (e.g. "drafting §3").
- `TODAY.md` is disposable, regenerated each run; projects should gitignore it (like the diff review ledger). It is NOT a substitute for STATE.md — STATE.md is the durable state; TODAY.md is just today's focus. The dashboard's Home "Today" card persists per-item checkmarks within the day (localStorage); a new date clears them — which is exactly why /sleep writes tomorrow's TODAY.md fresh.

### Step 1 — chat summary (right after TODAY.md)

In the chat, write:

```
Where we stand (from STATE.md, last updated <timestamp>):

  Current objective: <one sentence from STATE.md §2>
  Just completed:    <2-3 lines from STATE.md §3, most recent first>
  In progress:       <STATE.md §4, terse>
  Next:              <STATE.md §5, terse, top 1-2 items>

Today's to-do (also written to TODAY.md):
  Stage: <which stage we're in>
  Left:  <what's left to do today, terse>

Most recent dated activity (<filename>): <one-sentence headline from frontmatter or first H1>

Open: <STATE.md §7 if non-trivial>
```

Keep it tight. This is the primary output.

### Step 2 — the CLOSE-OUT TO-DO SWEEP (do this at the END of every interview — RULE OF LAW)

**The reason amnesia exists is that BOTH parties drift — the researcher AND Claude.** The
interview itself is a drift trap: as the researcher is coaxed back into the project, he *raises new things* — "append
those two slides to the deck," "redo the dose-1 Monte Carlo with wild cluster bootstrap," "revisit the bite
analysis." If those are merely mentioned and the conversation flows on, they evaporate — because Claude's
context rolls over and the researcher forgets he ever said them. **The interview must not end by summarizing; it must
end by ACTING.**

So at the close of the interview (or the chat summary in non-interview mode), Claude MUST:

1. **Sweep the whole session-so-far for every to-do the researcher raised** — every "we should…", "let's also…",
   "remind me to…", "we'll need to…", every fix/build/check named in the conversation. Not just the
   headline next-action — ALL of them.
2. **Consolidate them into one explicit to-do list, shown to the researcher**, each item written plain-language-first
   (the same rule as TODAY.md's `Left:` bullets: one plain sentence, then the jargon in parens).
3. **Then actually DO them** — or, for anything genuinely deferred, WRITE it into the durable canister
   (the stage `todo.md`, the checklist, TODAY.md) the same turn, per the CLAUDE.md "fix-on-learn or write it
   down the same turn" rule. A thing that was only *said* in the interview and neither done nor written to
   disk is a guaranteed drift. "I'll remember" is never acceptable — from either party.
4. **Confirm the sweep out loud**: "Here is everything you raised this session — [list] — here's what I did
   and what I filed." So the researcher sees nothing was dropped.

**The close sequence (after Q5, in order):**
1. Fold anything Q5 itself raised into the to-do list.
2. Present the consolidated to-do and say plainly: **"Okay, we're done reloading. Here's what I'm about to
   do — [the list]. Are you cool with it?"** — get his go before executing outward-facing work.
3. Give an honest **interview grade** — how loaded-in he got: e.g. "you came in well-informed — you nailed
   the design and the dose, only drifted on the outcome lock," or "you were pretty foggy on X, so lean on
   the notes today." This is feedback, not flattery; it tells him how much to trust his own recall this session.
4. On his go-ahead, **the consolidated to-do list BECOMES the session's working agenda.** Amnesia exits by
   handing the researcher that ordered list, and then we **walk it one item at a time** for the rest of the session.
   The list is the bridge from "reloaded" to "working" — it's the immediate next thing, not a someday-pile.
   Executing it, item by item, IS how the ritual closes — not the summary, not the file-writes, the doing.

This is the teeth of the ritual — and it closes the full loop: `/sleep` writes the handoff → `/amnesia`
reloads it AND hands back the ordered to-do → we execute that to-do item by item. The to-do is the output. `/sleep` writes the handoff; `/amnesia` reloads it AND closes the loop on
everything the reload surfaced. The interview coaxes the state back through the researcher; the sweep guarantees the
things he produces while being coaxed are executed, not lost.

## Edge cases

- **STATE.md missing:** halt the skill. Tell the user STATE.md does not exist and offer to create it from current session context. The chat summary cannot run without it.
- **STATE.md trivially short or stale:** Step -1 should catch staleness via the git-timestamp tripwire and auto-fix the drifted facts. If STATE.md is *so* thin that reconciliation can't reconstruct the state (e.g. it names no files, no stage), still write TODAY.md and the chat summary, but flag that STATE.md is too sparse to reconcile fully and recommend a `/sleep` to rebuild it.
- **No audits/ folder:** skip the "most recent dated activity" line; use the newest file in `progress_logs/` instead if present.

## Style discipline

- **Reconcile (Step -1) comes before everything.** Do not write TODAY.md or the chat summary from an unreconciled STATE.md — that is exactly the failure this skill now exists to prevent.
- The chat summary is the primary output. After reconciling, write TODAY.md first (it's cheap and always wanted), then the summary — both built from the *corrected* STATE.md.
- Do not editorialize or interpret the *narrative*. Render what the reconciled STATE.md says. But the fact-vs-judgment rule from Step -1 governs conflicts: on **facts**, git+disk win over STATE.md and you auto-fix (this reverses the old "STATE.md always wins" — a factual claim STATE.md makes that disk contradicts is drift, not truth); on **human judgment**, STATE.md/the researcher win and you preserve. Either way, flag the disagreement in chat.
- Do not propose actions in TODAY.md beyond what the reconciled STATE.md's Next section supports. TODAY.md reports the day's focus; the chat summary is where the conversation pivots to next moves.

## Origin

Created June 9, 2026, after the researcher articulated session amnesia as the recurring failure mode and proposed STATE.md as the fix. Originally paired with an HTML "reorient deck" for visual reload; that deck was retired 2026-07-09 once `/amnesia` began writing `TODAY.md` and the dashboard grew a Home tab — the Home "Today" card is now the visual reload, and STATE.md remains what the AI reads on entry. Same philosophy: orientation, not documentation; always reads from current sources.

**Step -1 (reconcile) added 2026-07-11**, after STATE.md's header drifted a full day behind git+disk (it read "dose NOT built, blocked on a live fork" while four later commits that same day had resolved the fork, built the dose panel, and shipped a 14-slide deck) — and `/amnesia` faithfully replayed the dead state. The lesson: STATE.md is hand-written and therefore the only orientation source that can lie, while git/disk/checklist boxes cannot. So amnesia now verifies STATE.md against ground truth and auto-fixes drifted facts (preserving human judgment) before trusting it. This is the harness's own "verification is continuous, the producer cannot grade its own exam" discipline applied to the orientation file itself.
