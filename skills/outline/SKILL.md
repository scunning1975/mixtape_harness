---
name: outline
description: Use when the user is at the manuscript stage and wants help outlining a short paper — invoked via /outline, or when the user says "outline the paper", "help me structure the manuscript", "what goes in the paper vs the appendix". Reads the project's completed pipeline first, then interviews the user (5 questions, one follow-up each, ONE AT A TIME), then recommends a ~3-page paper outline plus a long technical appendix.
---

# /outline — manuscript outline by interview

## What this is

The manuscript-stage sibling of `/covariates`. When the analysis is far enough along to write up, this skill helps decide the **architecture of the paper**: what the ~3-page body says, and what gets pushed into the long technical appendix. Same interview shape as `/covariates` — 5 questions, one at a time — but grounded in what the pipeline actually produced.

**The core tension it resolves:** a short paper cannot hold everything the pipeline made. Every exhibit, robustness check, and caveat wants to be in the body. The job is to decide the *few* things that earn the 3 pages and route the rest to the appendix — without hiding anything (both hands on the table: the appendix is where the honest detail lives, not where inconvenient results get buried).

**Target shape (Scott, 2026-07-18):** ~3-page body + a long technical appendix. The body is the argument; the appendix is the proof.

## Step 1 — READ THE PIPELINE FIRST (do this before asking anything)

This interview is GROUNDED, not generic. Before Q1, read enough of the project to ask specific questions:

1. `STATE.md` — current objective, what's done, what's open/blocked.
2. Each stage's `analyses/<slug>/stages/*/findings.md` — the lessons, in order. These are the raw material of the paper.
3. `analyses/<slug>/stages/*/exhibits.md` — the figures/tables that exist (candidate paper exhibits).
4. `analyses/<slug>/decisions.md` — the binding target parameter + any spec decisions.
5. The checklist `analyses/<slug>/checklist.md` — what's signed off vs. still open (an open gate may cap what the paper can claim).

Then say, in one short line, what you found — e.g. "Read the pipeline: dose treatment (max 8, 30 treated), one covariate F_S, RA-DiD sample 22/248, power stage says underpowered-except-large-effects, estimator not yet run." This proves the grounding and lets the user correct you before the interview.

## Step 2 — the interview (5 questions, ONE AT A TIME, one follow-up each)

Ask the FIVE questions below **one at a time**. Wait for the answer. Ask **exactly one follow-up** tuned to that answer, then move on. Ground each question in what you read in Step 1 (name the real numbers, exhibits, gates). Take notes.

**Q1 — The claim.** What is the ONE sentence this paper establishes? (Not the topic — the claim. e.g. "A media-coverage dose has no detectable effect on Day-1 hiring, and here is the bound.") *Follow-up: tie it to the pinned target parameter and ask whether the open gates let you make that claim at that strength yet.*

**Q2 — The reader & the contribution.** Who reads this, and what do they take away that they didn't have before — the empirical result, or the method/harness, or both? *Follow-up: press on which is the headline vs. the supporting act, since a 3-page body can't co-headline.*

**Q3 — The three body exhibits.** A 3-page paper carries ~2-4 exhibits. From what the pipeline built, which earn the body? *Follow-up: for each one they name, ask what it PROVES toward Q1 — and for a strong exhibit they leave OUT, confirm it's appendix-not-cut.*

**Q4 — The honest limits.** What are the real threats/limits (power, sample drift, identification, provenance gaps) — and which belong in the body (named plainly) vs. detailed in the appendix? *Follow-up: name the single limit that most constrains the claim, and ask where a skeptical referee looks first.*

**Q5 — What the appendix must prove.** The appendix exists so a referee can reconstruct every number. What must it contain — data provenance, the pipeline/runner, power sim, estimator details, robustness, the samples-and-ledger? *Follow-up: ask which appendix piece is the one that, if missing, sinks the paper (usually provenance or the reproducible pipeline).*

## Step 3 — synthesize the outline

After all five answers, produce TWO things.

**(A) The ~3-page body outline** — a numbered section list, each with a one-line purpose and its exhibit(s):

```
1. Intro / the claim         — Q1 sentence; why it matters (Q2); ≤ ¾ page
2. Setting & the dose        — what the treatment is; 1 exhibit (the bite)
3. Design & identification   — target parameter; the covariate; the honest limit (Q4)
4. Result                    — the headline exhibit; the estimate/bound
5. Conclusion                — what it means; what it doesn't
```

Adapt to the actual project. Every force/exhibit the user named in Q1–Q5 MUST appear (in body or appendix) or be explicitly justified as cut. Cross-check against Step 1: if the pipeline built an exhibit no section uses, flag it (orphan — cite or retire). If a section needs an exhibit the pipeline didn't build, flag it (a gap to fill before submission).

**(B) The technical appendix outline** — a numbered list of appendix sections, each mapped to the pipeline artifact that fills it:

```
A. Data & provenance         — sources, VENDORED_FROM, raw→derived chain
B. The reproducible pipeline — run_pipeline.sh; script→exhibit map
C. Covariate construction    — F_S method (STL, Hyndman), the script
D. Design & power            — size/power sim, MDE, the verdict
E. Estimator details         — spec, inference (permutation/RI), SEs
F. Sample & ledger           — anchor, every drop, the locked sample
G. Robustness / falsification — placebos, leave-one-out, alt specs
```

## Step 4 — write it down and route it

- Write the outline to `analyses/<slug>/manuscript_outline.md` (body + appendix, with the exhibit→section map and any orphan/gap flags).
- Note any BLOCKER honestly: if a checklist gate is still open (e.g. estimator not run, sample not locked), say the paper cannot claim its Q1 result at full strength until that closes — the outline is provisional on those gates.
- Do NOT draft prose. This skill produces the *architecture*; drafting is a separate pass (consider `/voice` for that).

## Discipline notes (this project's rules apply)

- **Both hands on the table.** The appendix is where honest detail lives — never where an inconvenient result gets buried. If a limit is real, it's named in the body too.
- **Provenance.** Every exhibit the outline places must trace to real, unmodified data via a pipeline script (the fabricated-figure rule). If an exhibit's provenance is shaky, flag it — don't outline it into the body.
- **Card early, check late.** The outline is a plan; it does not certify that exhibits exist and reconcile. If you place an exhibit, confirm it's on disk and signed off, or mark it "to build."
- **Reading load.** Keep the recommendation itself tight — the outline is a scannable list, not an essay. Draw the section arc as a clean list/box, per Scott's ASCII-figure rule.

## When to invoke

- User runs `/outline` directly.
- User reaches the manuscript/write-up stage and asks how to structure the paper.
- User asks "what goes in the paper vs. the appendix."
