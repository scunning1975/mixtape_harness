# Continuous-Treatment Difference-in-Differences Checklist

Run this checklist for every analysis with a **continuous dose** $D_i \in [0, \bar d]$ rather than a binary treatment indicator. Each step has a deliverable. If a step is genuinely irrelevant, write "N/A — reason" in place of the deliverable.

**Zero error is a constraint, not a goal.** Same discipline as the staggered/binary checklist. The reason this is a separate document is that the failure modes of continuous-treatment DiD are different in kind: TWFE on a continuous dose does not identify the parameter you want under heterogeneity, and pretending it does is the modal mistake. Step 0 below is the show-bite that earns the right not to use TWFE.

## How this checklist relates to the staggered/binary checklist

The staggered/binary `did_checklist.md` is the entry point for any DiD analysis in this project. Its **Step 1 (Target parameter)** routes here:

> **If your target parameter is a function of a continuous dose** — $\text{ATT}(d \mid d)$ (level), $\text{ACRT}(d)$ (slope), or any dose-response curve — **stop the staggered checklist and switch to `checklists/continuous_did_checklist.md`.** Continuous-treatment DiD has its own Step 0 (TWFE decomposition pedagogy) and its own per-step structure. Do not try to express a continuous parameter in the staggered checklist's framework.

The two checklists are siblings, not cousins. They share Steps 2–6 (covariates, balance, treatment viz, outcome-over-time, sample sizes) almost verbatim. They diverge at Step 0, Step 1, Step 7 (estimator), and Step 9 (falsification). Sign-off discipline is identical: produce `analyses/<slug>/manifest.yaml` per the staggered template's sign-off section.

## What this checklist actually is: an ATT(d|d)-or-ACRT(d) checklist

The target parameter is a function of dose. Two natural options:

- **ATT(d|d)** — *level* effect of being at dose $d$ vs being at zero, for units that actually received dose $d$. $E[Y(d) - Y(0) \mid D=d]$. Identified under **Standard PT** ($E[\Delta Y(0) \mid D=d] = E[\Delta Y(0) \mid D=0]$ for all $d$).
- **ACRT(d)** — *marginal* effect at dose $d$. $\partial E[Y(d) \mid D=d] / \partial d$. Identified under **Strong PT** (the Standard-PT condition holds for the *level* of every potential outcome $Y(d')$, not just $Y(0)$). Strong PT rules out selection on dose-response gains.

These are *different objects*. Standard PT identifies the level curve. Only Strong PT identifies the slope as the ACRT. **Reporting ACRT without defending Strong PT is the modal mistake.**

Every falsification class still targets Y(0) — see the staggered checklist's longer treatment.

---

## 0. Package preflight — the human looks

Same Gawande-style pause as the staggered checklist. The frontmatter `packages:` block must declare every package the analysis depends on, including version and install source. The user types each entry by hand.

- [ ] All packages with `# REQUIRES:` declarations in their consuming scripts.
- [ ] Package cards rendered on the dashboard for visual review.
- [ ] User has confirmed for at least one package: "I know what changed in this version vs. a month ago."

**Specific to continuous DiD:** declare versions of `contdid` (Callaway, Goodman-Bacon, Sant'Anna's continuous-DiD package; install via `devtools::install_github("bcallaway11/contdid")`) and any spline / kernel-regression dependencies (`splines`, `splines2`, `npiv`).

---

## 0b. **TWFE decomposition exhibit (the show-bite)**

This is the load-bearing pedagogical step that earns the right not to use TWFE. **Skipping it is not an option for a continuous-treatment DiD analysis.** The point is to show the audience that the canonical TWFE specification

$$Y_{it} = \alpha_i + \gamma_t + \beta^{\text{twfe}}\,(D_i \cdot \text{Post}_t) + \varepsilon_{it}$$

does not identify any clean causal parameter under heterogeneous dose-response. The decomposition is **algebra, not estimation** — pure FWL on the cross-section of doses.

### What to compute

The TWFE coefficient admits four mathematically equivalent rewrites as a weighted average of dose-specific effects:

| # | Question | Weight formula |
|---|---|---|
| Level | Effect of being at dose $\ell$ vs zero | $w^{\text{lev}}(\ell) = \dfrac{(\ell - E[D])\, f_D(\ell)}{\text{Var}(D)}$ |
| Scaled level | Effect per unit of dose | $w^s(\ell) = \ell \cdot w^{\text{lev}}(\ell)$ |
| ACRT | Marginal effect at $\ell$ | $w^{\text{acrt}}(\ell) = \dfrac{(E[D \mid D \geq \ell] - E[D])\, P(D \geq \ell)}{\text{Var}(D)}$ |
| 2x2 | Compare dose $h$ to dose $\ell$ | $w^{2\times2}(\ell, h) = \dfrac{(h - \ell)^2 f_D(\ell) f_D(h)}{\text{Var}(D)}$ |

All four are built from six features of the dose distribution computed before any outcome is loaded: $E[D]$, $\text{Var}(D)$, $f_D(\ell)$, $P(D \geq \ell)$, $E[D \mid D \geq \ell]$, and $d_L$ (the minimum positive dose).

### Deliverables

- [ ] **Multi-panel figure: the six ingredients.** One panel per ingredient, plotted over the dose support. (Glasgow deck slides 5-10.)
- [ ] **Multi-panel figure: the four weights.** One panel per weight formula, plotted over the dose support. The level weight should be visibly **negative** in the below-mean dose region; the ACRT weight should be non-negative; the 2×2 weight is a heatmap with mass on far-apart pairs. (Glasgow deck slides 11-14.)
- [ ] **Synthesis figure** overlaying all four weights on the same axis. (Glasgow deck slide 15.)
- [ ] **Hand reconstruction of $\hat\beta^{\text{twfe}}$.** Run OLS on $\Delta Y_i$ against $D_i$ on the pre/post-collapsed county-level data. Save $\hat\beta_{\text{OLS}}$. Compute level weights $W_i = (D_i - \bar D) / \sum_j (D_j - \bar D)^2$ by hand. Verify $\sum_i W_i \cdot \Delta Y_i$ equals $\hat\beta_{\text{OLS}}$ to machine precision (typical residual ~$10^{-16}$). The point: the decomposition *is* the regression.
- [ ] **Negative-weight tally.** Count how many treated units fall in the negative-weight region. Report as: "Of $N$ ever-treated units, $K$ have negative implicit weight under the level decomposition."

**Deliverable files:**
- Figure (single multi-panel): `output/figures/<slug>_twfe_decomposition.png`
- FWL identity check: print to script log; record residual in `analyses/<slug>/notes.md`.
- Negative-weight tally: append to `analyses/<slug>/decisions.md`.

### Why this comes before Step 1

You cannot pick a target parameter intelligently until you have seen what $\hat\beta^{\text{twfe}}$ would deliver and why it is not the parameter you want. Step 0b is the motivation; Step 1 is the commitment.

---

## 1. Target parameter — interview

This is the analog of the staggered checklist's Step 1, but with the questions sharpened for continuous treatment. **The user answers three questions, one at a time, and the answers are recorded as a one-paragraph "target parameter statement" in `analyses/<slug>/decisions.md`.** The statement is binding for the rest of the analysis: any later step that contradicts it fails the gate.

The questions:

### Q1. Static or dynamic?

**Static.** Collapse the panel to one observation per unit: $\Delta Y_i = \bar Y_{i,\text{post}} - \bar Y_{i,\text{pre}}$. Estimate one dose-response curve $\widehat{\text{ATT}}(d \mid d)$ from this collapse. This is the CGBS Option 1 default, the Lu-Yu setup. Hides the within-post dynamics.

**Dynamic.** Estimate a curve per event-time $\ell = -K, ..., +K$. Surfaces lag structure and pre-trend tests. Equivalent to running the static estimator separately for each event time. Deliverables multiply by $2K+1$.

**The choice has implications:**
- Static needs only Standard PT on the pre/post level difference.
- Dynamic surfaces the per-period structure but multiplies the comparisons and the assumptions (one parallel-trends assumption per event time).
- Most papers use static for the headline and dynamic for a robustness panel / pre-trend test.

### Q2. ATT(d|d) — level — or ACRT(d) — slope?

**ATT(d|d).** *Level* effect of being at dose $d$. "Units at dose 6 saw their outcome change by $X$ relative to the no-dose counterfactual." Identified under **Standard PT**.

**ACRT(d).** *Marginal* effect at dose $d$. "An additional article at dose 6 changes browsing by $Y$ per article." Identified under **Strong PT**.

**The choice has implications:**
- Reporting ACRT without defending Strong PT is the modal mistake. Strong PT requires the dose-response to be the same for any unit at any dose, regardless of which dose they actually received — i.e., no selection on dose-response gains.
- Most empirical papers should report level and only mention ACRT under "if Strong PT held" caveats.
- Bins is the safest primary spec (Standard PT only, easy to communicate). Linear is a no-bias-only-noise robustness against bins. B-spline / sieve is the smooth version of bins.

### Q3. Single-cohort or staggered?

If your design has only one treatment cohort (everyone who is ever treated gets their first dose at the same time), this question is trivial: single-cohort.

If your design has multiple staggered treatment cohorts, the question is real:

**Single-cohort (Phase 1).** Restrict the analysis to one cohort vs not-yet-treated. Run CGBS on this clean 2x2-shaped design. Document Phase 1; defer staggered to Phase 2.

**Staggered (Phase 2).** Run CGBS per cohort against not-yet-treated, then aggregate. The current `contdid` API may or may not support this directly; if not, run cohort-by-cohort manually and aggregate.

**The choice has implications:**
- Single-cohort gets you a clean Lu-Yu-shaped result fast. The Phase 1 result is publishable on its own.
- Staggered tests whether the dose-response is consistent across cohorts. Worth doing once the single-cohort result is in.
- Going straight to staggered without the single-cohort baseline makes it harder to debug if something looks weird.

### Output of the interview

A paragraph in `analyses/<slug>/decisions.md` that names: (a) static or dynamic, (b) ATT(d|d) or ACRT(d), (c) cohort scope, (d) which estimators (bins primary, linear/spline robustness), (e) the identifying assumption to be defended in Step 9. Example:

> Target parameter is $\widehat{\text{ATT}}(d \mid d)$ — the static, level dose-response curve, evaluated for the Feb 13 cohort against the 3,000 never-treated counties. Identification rests on Standard PT applied to the pre/post collapse: $E[\Delta Y(0) \mid D = d] = E[\Delta Y(0) \mid D = 0]$ for all $d$. ACRT(d) is reported only as a derivative of the level curve and not relied upon for inference, since Strong PT is not defended. Primary spec is bins (D ∈ {1, 3-4, 6, 8} → 3 bins). Linear and B-spline are robustness. Step 9 falsification: 9a (one-year-earlier mirror, already built) plus 9b (labor-treated counties as placebo group). Phase 2 (per-cohort) deferred.

**Deliverable file:** `analyses/<slug>/decisions.md` with the target-parameter paragraph.

**Other Step 1 declarations** (same as staggered checklist):

- [ ] Population weight? (Yes / No, and rationale.)
- [ ] Unit of observation (county, individual, firm)?
- [ ] Time unit (day, week, month)?

---

## 2. Understand the treatment and its assignment mechanism

**Identification work, not narrative — made HERE, displayed in the courtroom.** (Same step as the binary checklist; for a continuous dose the "assignment" includes *how much* dose a unit gets, not just whether.) Three facets:

- [ ] **Document the treatment.** What is the treatment/dose, when did it arrive, where did it land? For a media event: article timeline, sentiment, geographic spread (the "bite"). Deliverable: figures/tables showing the treatment occurred and its intensity distribution.
- [ ] **Is there a first-stage effect?** Did the dose actually vary and land — is there real variation in the cause? If not, the dose-response is uninterpretable.
- [ ] **Understand the assignment / selection mechanism.** Who gets treated, and who gets *more* dose? What predicts treatment and dose intensity? Covariates that drive **dose selection** are mechanically confounders and feed Step 3. (Note: selection on dose-response *gains* is what breaks Strong PT for ACRT — characterize it here so the ACRT caveat is grounded, not asserted.)

**Why this matters:** the dose-response is only interpretable once you know who received which dose and why. Build that characterization here; the courtroom displays it.

---

## 3. Covariates

Same as staggered checklist. Run `/covariates` if not already done. Output: `data/covariates_proposed.md`. The Y(0) trend is the target; Heckman-Ichimura-Todd discipline applies. Informed by Step 2's dose-selection mechanism.

The continuous-dose specific concern: covariates that drive **dose selection** (which units get high dose vs low dose) are mechanically confounders. List explicitly any covariate you believe drives both dose and outcome trend.

---

## 4. Balance and overlap

- [ ] Control group decision (typically: never-treated, since dose = 0 is the no-dose baseline).
- [ ] **Figure:** Propensity score for $P(\text{treated} \mid X)$, by treatment status. Overlap diagnostic only — the estimator uses regression adjustment, not propensity scores, since the control group is dose=0.
- [ ] **Figure (continuous-specific):** Dose distribution $f_D(d)$ on a histogram or density plot. The audience needs to see the support of $D$ — where the curve is identified.
- [ ] **Table:** Normalized differences in means. Imbens-Rubin |0.25| threshold. Bold rows where imbalance is meaningful.

**Deliverable files:**
- `output/figures/<slug>_pscore.png`
- `output/figures/<slug>_dose_distribution.png`
- `output/tables/<slug>_balance.tex`

---

## 5. Treatment visualization

For continuous treatment: a **dose-by-county map or scatter** rather than a binary treated/control map. Several options:

- A choropleth where treated counties are shaded by dose intensity (color ramp on $D_i$), control counties gray.
- A scatter of (some county feature) vs $D_i$ on the treated subset, to surface how dose was assigned.

If your design is staggered-and-continuous, also produce the staggered rollout figure.

**Deliverable file:** `output/figures/<slug>_dose_map.png` (or `<slug>_dose_scatter.png`).

---

## 6. Outcome over time (aggregated)

Plot mean $Y$ over time, **stratified by dose bin** rather than by treatment indicator. Use the same bins you will report in Step 8 (typically: D=0, low-dose, mid-dose, high-dose). Visual inspection of pre-period parallel trends across the bin trajectories.

If dynamic (Q1 = dynamic), this is also where you spot non-parallel pre-trends that will doom the dynamic spec.

**Deliverable file:** `output/figures/<slug>_outcome_by_dose_bin.png`.

---

## 7. Sample sizes

Same as staggered checklist. Counts of: D=0 (control), each dose level / bin (treated), drops with reasons.

For continuous-treatment specifically: report the **dose distribution table** — how many units at each $D_i$ value, plus min, max, median, mean, sd of dose among treated.

**Deliverable file:** `output/tables/<slug>_sample_sizes.tex` (combined with the dose distribution table).

---

## 8. Estimator

**THREE sub-steps, in order (RULE OF LAW): 8a SELECT → 8b LOCK THE SAMPLE → 8c RUN.**
**8b — pre-estimation sample-lock gate:** before ANY estimator runs, re-run the pipeline, then `/referee2 drift`
to reconcile the analytical-sample N against the anchor across EVERY stage that touched the sample (covariates,
balance/overlap, treatment viz, outcome-over-time, sample sizes, + the anchor), then `/blindspot` on the sample
construction. Analytical samples DRIFT silently across stages that ran at different times (a filter tightens, a
covariate join drops rows, `complete.cases` bites); discovering it AFTER estimation is the silent-sample-drift failure mode
(a censored month moved an estimate 3×). Estimation is BLOCKED until the sample is provably fixed and every
stage reconciles to one anchor (or names its documented sub-sample + why). Pin the certified estimation sample
ONCE, here.

**GATE:** Do not proceed past this point until Steps 1-6 have deliverables, the 8b sample-lock passes, AND Step 10 preflight passes.

The CGBS framework gives three forward-engineered options, all consistent with the Step 1 target. Listed in order of safest to least-safe assumption profile:

### Option 1 — Bins (PRIMARY)

Partition the dose into intervals; estimate one ATT per bin against the no-dose group. Identified under **Standard PT** only.

- Pros: easy to communicate, easy to estimate (sequence of 2×2 DiDs), policy thresholds can be chosen to match bin breaks.
- Cons: averages over within-bin doses; bin width is a discretion knob.

Use as the **primary** spec for any continuous-DiD analysis. Reviewers can argue with bin choice but cannot argue with the assumption profile.

### Option 2 — Linear in dose (ROBUSTNESS)

OLS of $\Delta Y_i$ on $D_i$ (after demeaning by the no-dose group). Imposes linearity. Useful as a robustness check against bins: if linear and bins agree on sign and rough magnitude, the dose-response is plausibly monotone. If they disagree, the dose-response is non-linear and bins is right.

### Option 3 — B-spline / sieve (ROBUSTNESS)

`contdid::cont_did(target_parameter = "level")` on the long panel. Returns a smooth dose-response curve with pointwise (or uniform) confidence bands. Identified under Standard PT for `target_parameter = "level"`; Strong PT for `target_parameter = "derivative"`. **Set `target_parameter = "level"` unless you have explicitly defended Strong PT in Step 1.**

### What NOT to use

- TWFE with $D_i \cdot \text{Post}_t$ as the regressor. Step 0b should have made this clear; if it did not, re-do Step 0b before continuing.
- Any specification where $D$ is interacted with covariates without first running bins on a stratified sample. Interactions on a continuous dose multiply the negative-weight problem.

**Deliverables:**
- [ ] Estimator specification recorded in `decisions.md` (which bins, which spline degree, which knot count).
- [ ] Rationale recorded.

---

## 9. Estimation and dose-response curve

- [ ] Estimator run on the validated panel.
- [ ] **Figure:** Dose-response curve. Bins as bar/step plot; linear and spline overlaid as lines with confidence bands.
- [ ] **Table:** Bin estimates with point estimate, SE, 95% CI, p-value per bin.
- [ ] **(Dynamic spec only)** Event-study figure: per-event-time dose-response curve, or per-bin event-study trajectories.

**Deliverable files:**
- `output/figures/<slug>_dose_response.png`
- `output/tables/<slug>_results.csv` (long form: spec, bin, estimate, SE, CI)
- `output/tables/<slug>_aggregates.tex` (preview-ready bins-vs-linear-vs-spline comparison)

---

## 10. Falsification — adapted for continuous treatment

The same three classes as the staggered checklist. **At least one of 9b or 9c must run** before sign-off; 9a is a baseline that should also run.

- **9a — same units, same outcome, different time.** Pre-period leads built into the dynamic event-study spec, OR a one-period-earlier placebo estimated with the same machinery. Should yield a flat curve near zero.
- **9b — different units, same outcome.** A placebo group with a different policy that should not move $Y$ via the same mechanism. Run the same continuous-dose machinery (with the placebo's dose, if available, or as a binary placebo if not). The dose-response curve should be flat / zero.
- **9c — same units, different outcome.** A placebo outcome that the treatment should not affect. Same machinery. Same expected null.
- **9d — Rambachan-Roth bounds.** Apply HonestDiD to the dose-response curve at each bin. Report bounds at $M = 0$, $M = 1$, $M = 2$.

**Deliverable files:**
- `output/tables/<slug>_falsification_<class>.tex` per falsification run
- `output/tables/<slug>_sensitivity.tex` for 9d

---

## 11. Estimator preflight (run BEFORE Step 7)

Same machinery as staggered checklist's Step 10. Continuous-specific items:

- [ ] **`contdid` version against frontmatter.** `packageVersion("contdid")` ≥ declared.
- [ ] **Dose-distribution overlap with the spline support.** If the bins or knots fall outside the empirical dose support, the estimator extrapolates. Verify all knots are inside $[d_L, \bar d]$ where $d_L$ is the minimum positive dose.
- [ ] **Static-vs-dynamic Step-1 commitment honored.** If Step 1 said static, no dynamic specification appears anywhere downstream without an explicit "robustness" label.
- [ ] **ATT-vs-ACRT Step-1 commitment honored.** If Step 1 said ATT(d|d), no ACRT estimate is reported as headline. The ACRT can appear only as "derivative of the fitted level curve, reported under the Strong PT caveat."
- [ ] **Negative-weight tally from Step 0b is greater than zero.** This is a sanity check — if the level weight has *no* negative region, your dose distribution is degenerate and you should not be running continuous-DiD at all.

If any preflight fails, file an incident at `audits/incidents/<YYYY-MM-DD>_<slug>_<failure-mode>.md`.

---

## Sign-off

Same convention as the staggered checklist: the canonical artifact is `analyses/<slug>/manifest.yaml`, produced by `scripts/r/_manifest.R::write_manifest("<slug>")`. The helper refuses to write if anchor counts mismatch, deliverable paths are missing, or the latest `/referee2 drift` verdict is not Clean.

Continuous-DiD-specific sign-off checks:

- [ ] Step 0b deliverable (TWFE decomposition multi-panel + FWL hand-reconstruction) exists.
- [ ] Step 1 target-parameter paragraph in `analyses/<slug>/decisions.md` is binding and consistent with the estimator chosen in Step 7.
- [ ] No ACRT result reported as headline unless Strong PT is explicitly defended in Step 9.
- [ ] At least one of 9b or 9c has run.
- [ ] `/referee2 drift` returns Clean.
- [ ] `_manifest.R::write_manifest("<slug>")` runs without error.
- [ ] Filed: a card per defended claim from this analysis.
- [ ] Frontmatter `status` updated to `complete`.
