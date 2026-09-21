# Difference-in-Differences Checklist

Run this checklist for every DiD analysis in this project. Each step has a deliverable — figure, table, or decision recorded. Don't skip steps; if a step is genuinely irrelevant, write "N/A — reason" in place of the deliverable.

**Zero error is a constraint, not a goal.** Goals are endogenous choice variables you trade off against speed, cost, and ambition. Constraints are not negotiated — every other choice bends to fit them. This checklist exists because zero-error-as-constraint *requires* an enumerated procedure with deliverables; an enumerated procedure is the only way to make verification visible and continuous rather than a discretionary stage at the end. If you find yourself asking "is this step worth it?" you have flipped the constraint into a goal. The answer is always yes — that is what *constraint* means.

## Where evidence is made, and the write-up gate between steps (RULE OF LAW)

Two rules govern how this checklist relates to the courtroom and the narrative:

1. **All evidence is PRODUCED inside the checklist.** Every figure, table, and number is *made* by a checklist step. The **courtroom does not make evidence** — it only *assembles* what the checklist produced, into the narrative argument. If you ever find yourself generating a new exhibit inside the courtroom, stop: it belongs to a checklist step. The courtroom is a display and verification surface, not a production one. (See CLAUDE.md, "Show the beat spine.")

2. **The write-up gate: before advancing to the next step, write up what this step taught you.** Each step ends with a short prose entry in `analyses/<slug>/findings.md` — what the deliverable showed, what you now believe, what it rules in or out. This is not the deliverable (the figure/table); it is the *interpretation* of the deliverable, written while it is fresh. You do not move to the next ring of the checklist until the current ring's lesson is written down. **Why:** the checklist produces artifacts; the write-up converts artifacts into understanding while the producer still remembers the choices. Skipping it means arriving at the courtroom with exhibits no one can narrate — the exact amnesia the harness exists to prevent. The findings.md entries are what later collapse into the narrative and the cards.

## What this checklist actually is: an ATT checklist for Y(0)-missing designs

This document is titled "DiD" because that is the most common method here, but the discipline it enforces is more general. **The target parameter is the average treatment effect on the treated (ATT), and the missing counterfactual is Y(0)** — the outcome the treated group would have realized had they not been treated. Every step is built around that.

Every falsification class targets Y(0):

- **9a (pre-period leads)** — were treated and control already on different Y(0) trajectories before treatment?
- **9b (placebo group)** — a population whose Y(0) under the same external shocks should look like the treated group's Y(0) under no treatment.
- **9c (placebo outcome)** — an outcome whose Y(0) is unaffected by the treatment's mechanism.
- **9d (Rambachan-Roth)** — bounds on post-period Y(0) drift.

The checklist transfers cleanly to: DiD (any flavor), synthetic DiD, synthetic control, matching for ATT, panel event-study designs with no-anticipation. It does **not** transfer cleanly to ATU designs (missing counterfactual is Y(1)) or ATE designs (both potential outcomes missing) — those need the falsification class flipped or doubled. RDD and IV identify off different logic and need their own checklist.

This is also why **Step 1.3 forces the user to classify their reviewer's most damaging objection as a Y(0) confounder vs a Y(1) treatment component**. A Y(1) worry (the treatment did something other than what you claim) is not falsifiable by placebo — it's an interpretation question. A Y(0) worry (treated and control would have diverged anyway) is what placebos are for.

## 0. Package preflight — the human looks

This is a Gawande-style pause. **The user verifies the package versions with their own eyes and types them into the checklist.** That act of typing is the verification. Nothing here is enforced by the agent — if it were, the human would never have to look, and the whole point of Step 0 is that they look.

The dashboard renders each declared package as a flippable card to make the looking easier (front: name, installed version, required version, source, install date; back: source URL, description, dependent scripts, known-bug notes). The cards are a reading aid, not a gate.

- [ ] **For every package this analysis depends on, the user has typed into the frontmatter `packages:` block:**
  - package name
  - **installed version** (read from `packageVersion("<pkg>")` — the actual version, not the wished-for version)
  - **install source** (CRAN, GitHub `user/repo`, local sandbox path, etc.)
  - **install date** (when this version was put on this machine)
  - source URL
  - one-line description of what the package does
  - one-line behavior note for *this version* — what's different from the prior version, or what known bug it fixes (this is the human capital; the URL is metadata)
- [ ] **The user has read each declaration aloud or written it on paper or otherwise externalized it.** Not "I trust the dashboard says it's green" — actually looked. The cost of a wrong version surviving into a published result is enormous; the cost of looking is thirty seconds.
- [ ] **Every estimation script in this analysis declares `# REQUIRES: <pkg> [op] <version>` at its top.** This is the artifact the user can grep for in six months when memory has decayed.
- [ ] **The user has confirmed for at least one package: "I know what changed in this version vs. the version I would have used a month ago."** If not, the analysis is using human capital they do not have — flag in `notes.md` and pause to consult upstream changelogs.

**Why no automation:** the failure mode is not "wrong version installed" (a machine catches that) but "user did not realize this version's behavior differs from the version they think they're using" (a machine cannot catch that). Step 0 forces the user to look. See Cunningham (2026) "Claude Code 53: Applied econometrics will require a detailed checklist" for the longer argument.

## 1. Target parameter and weighting

### 1.0 Routing — is this a continuous-treatment design?

**Stop here and read this paragraph before answering anything else.** If your treatment is a **continuous dose** $D_i \in [0, \bar d]$ (kilometers, dollars, percentage points, article counts, doses-per-1000 — anything not in $\{0, 1\}$ for the treated population), and your target parameter is a function of dose ($\text{ATT}(d \mid d)$, $\text{ACRT}(d)$, a dose-response curve), **switch to `checklists/continuous_did_checklist.md` immediately.** That checklist has its own Step 0b (TWFE decomposition pedagogy) and its own Step 1 interview that surfaces decisions specific to continuous treatment — static vs dynamic, level vs slope, single-cohort vs staggered. Do not try to express a continuous parameter inside this checklist.

If your treatment is binary (or staggered binary across cohorts), continue here.

### 1.1 Estimand

- [ ] Estimand: ATT? ATE? ATU? Group-time ATT? Write it in expectation form (e.g., $E[Y(1) - Y(0) \mid D=1]$ for ATT).
- [ ] Population weight? (Yes / No, and rationale.)
- [ ] Unit of observation (county, individual, firm)?
- [ ] Time unit (day, week, month)?

**Why this matters:** the target parameter determines which estimators are even appropriate, and weighting choices change the estimand from sample-ATT to population-ATT.

## 2. Understand the treatment and its assignment mechanism

**This is identification work, not narrative.** A conditional-PT DiD is only as good as your understanding of *who gets treated and why*. Make that understanding HERE, in the checklist — do not produce it inside the courtroom. The courtroom *displays* what this step *makes*. Three facets:

- [ ] **Document the treatment.** What is the treatment, when did it happen, where did it land? (For a media event: the article timeline, sentiment, geographic spread — the "bite.") Deliverable: the figures/tables that show the treatment actually occurred and where.
- [ ] **Is there a first-stage effect?** Did the treatment actually arrive — is there measurable variation in the thing that is supposed to cause the outcome? If the treatment didn't land, nothing downstream is interpretable. State it.
- [ ] **Understand the assignment / selection mechanism.** Who is assigned to treatment, and why? What predicts treatment? This is the selection story — model it if you can (e.g., predict treatment from covariates; cross-event prediction). This directly informs Step 3's covariate choice: the X that drive selection into treatment are candidates for the X that must satisfy conditional parallel trends.

**Why this matters:** understanding selection is what makes the later ATT *interpretable*. A null is "media arrives where customers aren't" only if you have characterized who receives the treatment. This step is where that characterization is built and signed off — so the covariates (Step 3) are chosen with the assignment mechanism in view, not guessed.

## 3. Covariates
Run the `/covariates` skill (see ~/.claude/skills/covariates/SKILL.md). Five-question interview, synthesize the 10-chapter book, source the data. Informed by Step 2's assignment mechanism.

- [ ] Output: `data/covariates_proposed.md`
- [ ] Theoretical justification: $E[Y(0) mid D=1, X=x] = E[Y(0) mid D=0, X=x]$
- [ ] Operational justification: Heckman-Ichimura-Todd (1997), find X that drives $Delta Y(0)$.

## 4. Balance and overlap
- [ ] Decide control group: never-treated / not-yet-treated / restricted subset (and which subset).
- [ ] **Figure:** Propensity score distribution for treated vs. control (overlapping density plot).
- [ ] **Table:** Normalized differences in means.
  - Formula: $rac{ar Y_T - ar Y_C}{sqrt{(hatsigma^2_T + hatsigma^2_C)/2}}$
  - Last column = absolute value
  - **Bold** rows where $|	ext{normalized diff}| > 0.25$
  - Footnote: "Imbens & Rubin (2015) identify $|	ext{normalized diff}| > 0.25$ as imbalanced."

## 5. Treatment visualization
- [ ] Staggered design: `panelview` plot (R) showing treatment timing per unit.
- [ ] Two-group design: geographic map (counties / states / cities). Treated colored, control gray, dropped units excluded entirely.

## 6. Outcome over time (aggregated)
- [ ] Plot mean Y over time for treated and control AT THE GROUP LEVEL — not by unit.
- [ ] Visual inspection of pre-period parallel trends.

## 7. Sample sizes
- [ ] **Table:** Counts of treated, control, dropped (and reason for drops).
  - Two-group design: row per group with N.
  - Cohorted design: row per (cohort, treatment date) with N.

## 8. Estimator

**THREE sub-steps, in order (RULE OF LAW): 8a SELECT → 8b LOCK THE SAMPLE → 8c RUN.**
**8b — pre-estimation sample-lock gate:** before ANY estimator runs, re-run the pipeline, then `/referee2 drift`
to reconcile the analytical-sample N against the anchor across every stage that touched the sample (covariates,
balance, treatment viz, outcome, sample sizes), then `/blindspot` on the sample construction. Samples drift
silently across stages that ran at different times; catching it AFTER estimation is the silent-sample-drift failure mode.
Estimation is BLOCKED until the sample is provably fixed and reconciles to one anchor. Pin it once, here.

Pick one (preference order):
- [ ] **Callaway-Sant'Anna (2021)** — preferred. Doubly robust, transparent, group-time ATT.
- [ ] Saturated TWFE with $X 	imes mathbb{1}[t=k]$ interactions (regression adjustment).
- [ ] SynthDiD (Arkhangelsky et al. 2021) — when parallel trends are suspect.

Record the choice and rationale.

## 9. Estimation and event study
- [ ] Run the estimator.
- [ ] If CS-DiD in R: drop $g-1$ ("universal baseline").
- [ ] **Figure:** Beautiful event study (publication-quality — labels, units, sample, method, time period).
- [ ] **Report the SIMPLE average** (not the group-size-weighted average).

## 10. Falsification

Every $2 \times 2$ DiD identifies $\text{ATT} + \mathbb{E}[\Delta Y(0)_T - \Delta Y(0)_C]$. The bias term is unobservable; falsifications are the discipline of trying to *measure* it under conditions where it should be zero. If a falsification fires, the design's identification is in trouble; if it does not, you have evidence that the design is doing work.

Run as many of the three classes below as the data permits. **Run at least one of 9b or 9c.** A study with no active falsification has no defense against selection bias. The post-falsification claim should be: "if the alternative hypothesis (no causal effect, just selection or trend) were true, we'd expect to see X — and we don't."

### 9a. Same outcome, same units, pre-treatment period

The pre-treatment leads in the event study (already produced in Step 8).

- [ ] **Pre-treatment leads insignificant individually** (no $t > 2$).
- [ ] **Pre-treatment leads jointly insignificant** (Wald F-test or Roth (2022) joint test).
- [ ] **Visual: leads are flat and clustered around zero.**

**What this catches:** the most common identification failure — treated and control units already on different trajectories before treatment.

**Caveat:** flat leads do not prove parallel trends post-treatment. They show only that whatever bias exists hadn't fired yet in the visible pre-period. This is why 9d (sensitivity) exists.

### Before 9b/9c — Claude proposes candidates, then elicits

Before the user fills in the placebo-group or placebo-outcome blank, the AI should **read the project's context** (`CLAUDE.md`, `narrative.md`, `decisions/`, `hypotheses/*.md`, recent `insights/`, `scratch/`) and **propose 2–3 candidates per placebo class** with a one-line rationale each. Then explicitly ask: *"Do you have other candidates I missed?"*

Same pattern as the `/covariates` skill — interview, suggest, confirm. The AI widens the candidate set from project context; the human picks. The AI does not pick a placebo on its own initiative.

```
9b candidates (placebo group):
1. <group A> — <rationale>
2. <group B> — <rationale>
3. <group C> — <rationale>

9c candidates (placebo outcome):
1. <outcome A> — <rationale>
2. <outcome B> — <rationale>
3. <outcome C> — <rationale>

(then ask: "any candidates you'd add?")
```

Document the proposed candidates in the analysis's checklist instance, including the ones the user rejected. The record of what was suggested vs what was chosen is part of the falsification audit trail.

**How to generate candidates:** for 9b (placebo group), surface units that face the same external shocks as the treated but did not receive the treatment's specific mechanism — a population whose Y(0) trend should mirror the treated group's. For 9c (placebo outcome), surface an outcome the treatment's mechanism should NOT move, and separately a positive-control outcome it *should* move (so the test demonstrably has power). Document the candidates proposed and the ones rejected in the analysis's checklist instance — the record of suggested-vs-chosen is part of the falsification audit trail.

### 9b. Same outcome, different (untreated) units

Pick a population the treatment's mechanism should NOT reach. Run the same specification. They should show no effect.

- [ ] **Placebo group identified** and rationale recorded (why is this group structurally untreated?).
- [ ] **Identical specification** (estimator, covariates, time window) run on the placebo group.
- [ ] **Placebo ATT null and insignificant.**
- [ ] **Reported alongside main ATT** in the manuscript.

**Canonical example:** Miller, Johnson, and Wherry (2021, QJE). Main result: Medicaid eligibility expansion to 150% FPL reduces mortality in the near-elderly (<65). Falsification: 65+ are already on Medicare; the policy doesn't bite for them. Same outcome (mortality), different group, no expected effect — and they find none. Strong evidence the near-elderly effect is the policy and not a coincident trend.

**What this catches:** unobserved shocks correlated with the policy environment that affect everyone (including the placebo group), and design failures where the "control" group was actually treated.

### 9c. Different outcome, same units (post-treatment)

Pick a post-treatment outcome the treatment's mechanism should NOT change. Run the same design. It should show no effect.

- [ ] **Placebo outcome identified** and rationale recorded.
- [ ] **Identical specification** run on the placebo outcome.
- [ ] **Placebo effect null and insignificant.**
- [ ] **Reported alongside main outcome** in the manuscript.

**Canonical example:** cigarette tax study, main outcome emphysema. Placebo outcomes: bone fractures, syphilis, accidental drownings. None should respond to a tobacco policy through any plausible channel. Find effects on those and the design is picking up something tobacco-policy-correlated rather than tobacco-specific.

**What this catches:** mechanism mis-specification (the treatment is doing something, but not what you claim), and broad correlates of policy adoption (treated jurisdictions systematically differ in many post-treatment outcomes).

### 9d. Rambachan-Roth sensitivity

Pre-treatment falsification (9a) constrains pre-period bias only. Post-treatment violations are unobservable. Rambachan-Roth (2024, RESTUD) bounds how much could exist before the result flips.

- [ ] **R package:** `HonestDiD` (or Stata `honestdid`).
- [ ] **Report bounds at $\bar{M} = 0, 1, 2$.**
- [ ] **Report the breakdown $\bar{M}$** — the value at which the CI first crosses zero. This is the "how much hidden bias to overturn this result" number.

### Sign-off on 9

- [ ] **At least one of 9b or 9c was run.** Not optional.
- [ ] **All falsifications reported in the manuscript** — including any that fired. Negative falsifications that ran cleanly strengthen the paper; suppressing them weakens it (and is specification searching).

## 11. When estimation misbehaves

If the estimator returns NAs, structural error patterns, or "singular matrix" warnings that don't square with what you see in the data, run these in order before assuming your data is wrong:

- [ ] **Package version against upstream.** CRAN can lag GitHub by months. `packageVersion("did")` vs `curl -s https://raw.githubusercontent.com/bcallaway11/did/master/DESCRIPTION | grep Version`. If they differ, install the dev version into a sandbox library and rerun. Five-second check. The prior is "the package works, my data is wrong" — don't trust that prior.
- [ ] **Encoding alignment between `tname` and `gname`.** Both must live on the same integer scale, with 0 = never-treated. A scale mismatch (e.g., `tname=1..18`, `gname=100..111`) silently produces "no valid groups" or wrong cell-grids.
- [ ] **Universal-baseline reference cells.** Under `base_period = "universal"`, cells at $t = g - 1$ are reference cells with $att = 0$ and $SE = NA$ *by design*. Don't mistake them for failures.
- [ ] **EPV vs covariate count.** If a cohort has fewer than ~10 events per covariate, the doubly-robust regression will fail or be unstable. Drop covariates for that cohort or run unconditional.
- [ ] **Unconditional spec (`xformla = ~1`) as null check.** If the unconditional fit succeeds and the covariate fit fails, the issue is rank/EPV, not the data.
- [ ] **Reproduce one failed cell manually.** `DRDID::reg_did_panel` on the cell's slice. If it computes cleanly outside the wrapper, the wrapper's guard logic is the issue, not your data.

**Why:** four to six hours can disappear into "the data must be wrong" debugging when the actual fix is a one-line version bump. Documented incident: 2026-06-08, CRAN `did` 2.3.0 → GitHub 2.3.1.907 cleared 27 of 51 phantom NA-SE cells immediately.

## Sign-off
- [ ] Steps 1-10 complete.
- [ ] **Every step has a write-up entry in `analyses/<slug>/findings.md`** (the write-up gate — no step advanced without its lesson recorded).
- [ ] Step 7 N's reconcile with Step 5's map (no orphan counties).
- [ ] Step 9 estimator matches Step 8 choice.
- [ ] Step 10 bounds reported and discussed.
- [ ] Step 11 only triggers if estimation misbehaves; if it did, document which check resolved it.
- [ ] **Then, and only then, move to the courtroom** to assemble the produced evidence into the narrative. The courtroom assembles; it does not produce.
- [ ] Filed: a card per defended claim (cards/<claim>.md).
