---
slug: <kebab-case-slug>
started_date: <YYYY-MM-DD>
estimator: <CS-DiD | TWFE | SynthDiD | did2s | manual-DRDID>
status: in_progress  # in_progress | complete | abandoned
target_population: <one-line description>
treatment_definition: <one-line description>
time_window: <YYYY-MM-DD to YYYY-MM-DD>

packages:
  # Step 0: the user has TYPED these in after looking with their own eyes.
  # The dashboard renders each as a flippable card; the cards are a reading
  # aid, not an enforcement gate. Every field below is required and the user
  # types it by hand — no scripts populate this for you.
  - name: did
    installed_version: "<run packageVersion('did') and type the result>"
    install_source: "<CRAN | GitHub bcallaway11/did | local sandbox path>"
    install_date: "<YYYY-MM-DD>"
    required_version: ">= 2.3.1"
    url: https://github.com/bcallaway11/did
    description: Callaway-Sant'Anna doubly-robust DiD with multiple periods and groups.
    behavior_note: "<one line: what does this version do that the previous version did not>"
    known_bugs:
      - version: "2.3.0"
        note: "CRAN release silently fails ATT(g,t) cells with bogus 'singular design matrix' warnings; rcond is nowhere near machine epsilon. Fixed in 2.3.1.907 on GitHub."
  - name: HonestDiD
    installed_version: "<fill in>"
    install_source: "<CRAN | GitHub asheshrambachan/HonestDiD>"
    install_date: "<YYYY-MM-DD>"
    required_version: ">= 0.2.6"
    url: https://github.com/asheshrambachan/HonestDiD
    description: Rambachan-Roth (2024 RESTUD) sensitivity to violations of parallel trends.
    behavior_note: "<one line>"
---

# DiD Checklist — <slug>

This is an instance of `checklists/did_checklist.md`. Fill in deliverables as you complete each step. Do not edit the global template; edit this file. Steps must be completed in order. Step 7 (estimation) is gated by completion of Step 0 (human-attention package preflight) AND Steps 1–6.

**Scope.** This is an ATT checklist for designs where the missing counterfactual is Y(0). It applies as written to DiD (any flavor), SynthDiD, synthetic control, matching for ATT, and panel event-study with no-anticipation. If your design targets ATU, ATE, or uses non-parallel-trends identification (RDD, sharp IV), Step 9's falsification class needs adapting — flag in `notes.md` and adapt as you go.

## 0. Package preflight — the user looks (Gawande pause)

This is a human-attention checkpoint, not an automation. **The user verifies the package versions with their own eyes and types them into the frontmatter.** That act of typing is the verification. The dashboard's package cards are a reading aid; they do not gate the analysis.

- [ ] **For every estimation package: I ran `packageVersion("<pkg>")` and typed the result into the frontmatter.** Not the version I wished was installed. Not the version I think is current. The actual one.
- [ ] **For every package I typed the install source** (CRAN vs GitHub `user/repo` vs local sandbox path). These are different packages with different behavior even when the version string matches.
- [ ] **For every package I typed a one-line behavior note for *this version*.** What does this version do that the previous version did not? If I cannot answer that question, I am using human capital I do not have — I pause and consult the upstream changelog before continuing.
- [ ] **Every estimation script in this analysis declares `# REQUIRES: <pkg> [op] <version>` at its top.** This is the grep-able paper trail for six months from now.
- [ ] **I have read the `packages:` block aloud or written it on paper.** The point of Step 0 is the looking.

**Deliverable:** the frontmatter `packages:` block, with every entry's `installed_version`, `install_source`, `install_date`, and `behavior_note` filled in by hand.

**Why no automation:** the failure mode is not "wrong version installed" (a machine can catch that) but "user did not realize this version's behavior differs from the version they think they're using" (a machine cannot catch that). Step 0 forces the user to look. See `checklists/did_checklist.md` Step 0 for the longer argument and the Cunningham (2026) "Claude Code 53" reference.

## 1. Target parameter and weighting
- [ ] Estimand: <write in expectation form, e.g. $E[Y(1) - Y(0) \mid D=1]$ for ATT>
- [ ] Population weight: <yes/no, with rationale>
- [ ] Unit of observation: <county / individual / firm>
- [ ] Time unit: <day / week / month>

**Deliverable file:** N/A (decision recorded above)

## 2. Covariates

**Run the `/covariates` skill** (`~/.claude/skills/covariates/SKILL.md`) before adding any covariate. The interview is the discipline against specification searching. Free-form selection is how analyses drift toward whatever covariate set produces a publishable result.

- [ ] Ran `/covariates` for this analysis.
- [ ] Covariates list:
- [ ] Theoretical justification recorded ($E[Y(0) \mid D=1, X] = E[Y(0) \mid D=0, X]$).
- [ ] Source data verified.

### EPV check — within cohort, not total

- [ ] **Computed $\text{EPV}_g = n_g / k$ for every treated cohort** ($n_g$ = treated units in cohort $g$; $k$ = number of covariates).
- [ ] Smallest-cohort EPV recorded: ___ (≥ 10 preferred, ≥ 7 hard floor).
- [ ] **If smallest-cohort EPV < 7, remediation recorded** (drop covariates for that cohort, run RA only, or document as IPW-unidentified).
- [ ] **Confirmed: EPV is computed on within-cohort treated count, not total treated count.** The aggregate often passes while the binding cohort fails. Hypothetical example: 51 treated counties / 7 covariates = 7.3 looks fine, but cohort sizes 33/5/8/5 give EPVs 4.7/0.7/1.1/0.7 — three of four cohorts fail. The aggregate metric hides the problem.

**Deliverable file:** `analyses/<slug>/decisions.md` or `data/covariates_proposed.md`

## 3. Balance and overlap
- [ ] Control group: <never-treated / not-yet-treated / restricted subset, with rationale>
- [ ] Propensity-score overlap figure
- [ ] Normalized-differences table (Imbens-Rubin |0.25| threshold)

**Deliverable files:**
- Figure: `output/figures/<slug>_pscore.png`
- Table: `output/tables/<slug>_balance.tex`

## 4. Treatment visualization
- [ ] Staggered: panelView rollout figure. Two-group: county map.

**Deliverable file:** `output/figures/<slug>_rollout.png`

## 5. Outcome over time (aggregated)
- [ ] Mean outcome by group, plotted over the full time window
- [ ] Visual inspection of pre-period parallel trends documented in notes

**Deliverable file:** `output/figures/<slug>_outcome_by_group.png`

## 6. Sample sizes
- [ ] Counts of treated, control, dropped (with reasons)
- [ ] N's reconcile with Step 4's map

**Deliverable file:** `output/tables/<slug>_sample_sizes.tex`

## 7. Estimator
**GATE:** Do not proceed past this point until Steps 1–6 have deliverables AND Step 10 preflight passes.

- [ ] Estimator chosen:
- [ ] Rationale recorded:

## 8. Estimation and event study
- [ ] Estimator run on the validated panel
- [ ] Universal baseline (CS-DiD): drop $g-1$ cells from event-study display
- [ ] Event-study figure with publication-quality labels
- [ ] Simple-average ATT reported (not group-size-weighted)

**Deliverable files:**
- Figure: `output/figures/<slug>_event_study.png`
- Table: `output/tables/<slug>_results.csv`

## 9. Falsification

Every $2 \times 2$ DiD identifies $\text{ATT} + \mathbb{E}[\Delta Y(0)_T - \Delta Y(0)_C]$. Falsifications measure that bias under conditions where it should be zero. Run at least one of 9b or 9c — a study with no active falsification has no defense against selection bias. See `checklists/did_checklist.md` Step 9 for the full taxonomy.

### 9a. Same outcome, same units, pre-treatment (event-study leads)

- [ ] Pre-treatment leads individually insignificant.
- [ ] Pre-treatment leads jointly insignificant.
- [ ] Visual: leads flat and clustered around zero.

**Deliverable:** the leads in `output/figures/<slug>_event_study.png` (already produced in Step 8).

### Falsification candidates — Claude proposes, user picks

Before filling in 9b and 9c, the AI reads the project context (`CLAUDE.md`, `narrative.md`, `decisions/`, `hypotheses/*.md`, `insights/`, `scratch/`) and proposes 2–3 candidates per class. Both AI suggestions and any user additions are recorded here so the audit trail is complete.

**9b candidates (placebo group)** — Claude proposed:

1. <candidate group> — <rationale>
2. <candidate group> — <rationale>
3. <candidate group> — <rationale>

User added:

- (none, or: <additional candidates>)

**9b chosen:** <which one and why>

**9c candidates (placebo outcome)** — Claude proposed:

1. <candidate outcome> — <rationale>
2. <candidate outcome> — <rationale>
3. <candidate outcome> — <rationale>

User added:

- (none, or: <additional candidates>)

**9c chosen:** <which one and why>

### 9b. Same outcome, different (untreated) units (placebo group)

- [ ] Placebo group identified and rationale documented:
- [ ] Identical specification run on placebo group.
- [ ] Placebo ATT null and insignificant.
- [ ] Reported alongside main ATT in manuscript.

**Deliverable file:** `output/tables/<slug>_falsification_placebo_group.csv`

### 9c. Different outcome, same units (placebo outcome)

- [ ] Placebo outcome identified and rationale documented:
- [ ] Identical specification run on placebo outcome.
- [ ] Placebo effect null and insignificant.
- [ ] Reported alongside main outcome in manuscript.

**Deliverable file:** `output/tables/<slug>_falsification_placebo_outcome.csv`

### 9d. Rambachan-Roth sensitivity to remaining parallel-trends violation

- [ ] HonestDiD (or equivalent).
- [ ] Bounds at $\bar{M} = 0, 1, 2$.
- [ ] Breakdown $\bar{M}$ reported.

**Deliverable file:** `output/tables/<slug>_sensitivity.tex`

### Step 9 sign-off

- [ ] At least one of 9b or 9c ran (not just 9a + 9d).
- [ ] All falsifications reported in the manuscript, including any that fired.

## 10. Estimator preflight (run BEFORE Step 7)

This is the version-and-encoding gate. Run it before any estimator function call.

- [ ] **Package version against upstream.** `packageVersion("did")` ≥ frontmatter `package_versions.did`. If installed < required, STOP. Ask the user before installing or upgrading.
- [ ] **Encoding alignment between `tname` and `gname`.** Both on the same integer scale; never-treated = 0.
- [ ] **Universal-baseline reference cells understood.** Cells at $t = g - 1$ have ATT = 0, SE = NA by design — not failures.
- [ ] **EPV vs covariate count.** Each cohort has events ≥ 10× covariates, OR covariates dropped for that cohort.
- [ ] **Unconditional null check (`xformla = ~1`)** runs cleanly — confirms data is OK before adding covariates.
- [ ] **One failed cell reproduced manually** (only if estimator returned NAs in earlier run): `DRDID::reg_did_panel` on the cell's slice.

If any of these surface a problem, file an incident at `audits/incidents/<YYYY-MM-DD>_<slug>_<failure-mode>.md` naming which sub-check resolved it. Do not silently work around the issue.

## Sign-off

The canonical sign-off artifact for an analysis is **`analyses/<slug>/manifest.yaml`**. This is the contract — a machine-readable record of what was produced, what package versions produced it, what panel hash it ran on, and what anchor it claims. Everything else (PDFs, .tex includes, dashboard cards) is a derived view. The manifest is what `/referee2 drift` reconciles, what the dashboard reads, and what the writeup cites.

**Manifest convention:** see `analyses/README.md` for the full schema and required keys. Build it with `scripts/r/_manifest.R::write_manifest(slug = "<slug>")` (or `scripts/python/_manifest.py`). The helper computes the panel SHA-256, captures `sessionInfo()` package versions, and verifies that every deliverable path in the manifest actually exists on disk. It refuses to write if any path is missing.

**Sign-off checks (in order):**

- [ ] Steps 1–9 complete (or N/A documented).
- [ ] Step 6 N's reconcile with Step 4's map (no orphan units).
- [ ] Step 8 estimator matches Step 7 choice.
- [ ] Step 9 bounds reported and discussed in notes.
- [ ] Step 10 preflight passed before Step 7 ran; any failures filed as incidents.
- [ ] **`/referee2 drift` returns Clean** (or all flagged drift events are documented in the manifest's `drift.documented_drops` block).
- [ ] **`scripts/r/_manifest.R::write_manifest("<slug>")` runs without error.** Records: panel path + SHA-256, anchor reference, package versions, every deliverable path (verified to exist), the sign-off timestamp, the cards produced.
- [ ] Filed: a card per defended claim from this analysis (`cards/<claim>.md`), referenced from the manifest's `cards:` list.
- [ ] Frontmatter `status` updated to `complete`.

**What the manifest produces downstream (no manual work required):**

- Dashboard reads `analyses/<slug>/manifest.yaml` and renders a `status: complete` row showing the slug, sign-off date, package versions (linked to package cards), anchor (linked to YAML), and a flip-card with the event-study PNG on the front and every deliverable path on the back.
- (Optional) `scripts/r/render_manifest_pdf.R <slug>` produces a one-page summary PDF. Not required for sign-off; convenience for sharing.
- (Optional) `scripts/r/render_manifest_tex.R <slug>` emits a `\input{...}` block for the manuscript. Not required for sign-off.
