# Review — Rubin (2008), "For Objective Causal Inference, Design Trumps Analysis"
### *Annals of Applied Statistics* 2(3): 808–840

*Read as the philosophical spine of the harness: objectivity is manufactured at the
**design** stage — before outcomes are ever seen — not rescued at the analysis stage.*

---

## The one-paragraph version

Rubin's thesis is a single discipline: an observational study earns objective causal
inference only by **reconstructing the hypothetical randomized experiment** that could have
produced the data — naming the treatment, the assignment mechanism, the decision makers, and
the key covariates they used — and achieving covariate balance **with all outcome data
stripped away and hidden**. Randomized experiments are trustworthy because they are
prospective and outcome-blind: you physically *cannot* tune them to favor a result. An
observational study inherits that trust only if the analyst imposes the same blindness by
construction. The propensity score is the observational analogue of randomization (used to
balance covariates, *not* to model outcomes), and where covariate distributions don't
overlap, the honest act is to **refuse** to infer rather than lean on unassessable model
assumptions. Analysis — the regressions everyone fixates on — is the last and least important
step.

---

## The argument, in five moves

```
  1. NAME the hypothetical randomized experiment the data pretend to be
        (exact treatment, exact outcome, block vs. block-with-noncompliance)
                         │
  2. FIND the assignment mechanism — who decided, on what covariates?
        "the model for the assignment mechanism is more fundamental ...
         than a model for the science" (p.8)
                         │
  3. HIDE the outcomes. Design with covariates only.
        "outcome-free design is absolutely critical for objectivity" (p.10)
                         │
  4. BALANCE via propensity score → subclassify/match; document balance
        bin by bin. If no overlap → REFUSE inference. If covariates badly
        measured → get better data: "no amount of fancy analysis can
        salvage an inadequate data base" (p.11)
                         │
  5. ONLY THEN analyze. Model-based adjustment, if any, specified a priori.
        "not simply running mindless regression programs and looking at
         coefficients" (p.32)
```

The worked escalation: he starts with propensity-score subclassification (doctor-visit and
cardia-cancer balance, Figs. 3–8), then raises the difficulty to a **randomized encouragement
design with noncompliance** — where he deploys principal stratification (LL/LS/SL/SS),
monotonicity (no defiers), the exclusion restriction, and the IV identity CACE = ITT / π_LS.
The tell: he does the *entire* design **using intermediate treatment-receipt data but with the
survival outcomes deliberately withheld** — "Survival data are not available at this stage!"
(p. 26). Even for a randomized experiment, he argues, un-randomized covariates should be
balanced outcome-free, because a-posteriori adjustment "would compromise that objectivity."

---

## The quotes worth putting on camera

> "Observational studies have to be carefully designed to approximate randomized experiments,
> in particular, **without examining any final outcome data**." (p. 1)

> "**Outcome-free design is absolutely critical for objectivity.**" (p. 10)

> "No amount of fancy analysis can salvage an inadequate data base." (p. 11)

> "The propensity score is the observational study analogue of complete randomization ... its
> use is not intended to increase precision but only to **eliminate systematic biases**." (p. 14)

> "Final outcome data cannot be used in design without compromising the objectivity of the
> study design." (p. 32)

> "Most important is for the worker in observational studies to stay focused on approximating a
> plausible hypothetical underlying randomized experiment." (p. 32)

---

## Why this is the spine of your harness

Your harness is a set of "conceptual folders" that force the work to happen in the right
order so you don't get lost in everything the AI can generate. Rubin gives that ordering its
justification: **the sequence isn't bureaucracy, it's where objectivity comes from.** The
folders that come before "results" exist precisely so that no downstream flexibility can cook
the answer.

```
  RUBIN'S STAGE            →  YOUR HARNESS FOLDER (the DiD five elements)
  ───────────────────────────────────────────────────────────────────────
  Name the experiment       →  ① TARGET / estimand  ("what randomized trial?")
  Assignment mechanism      →  the treatment-timing / cohort structure
  Key covariates, balance   →  ① BITE + covariates + overlap, done blind
  Outcome-free design       →  the whole left side of the harness, BEFORE
                               you ever regress on the outcome
  Refuse if no overlap      →  a real STOP gate, not a footnote
  Analysis last             →  ④ MAIN RESULTS — the smallest folder
```

Two things to say to camera:

1. **The bite lives on the design side of Rubin's line.** In all three empirical papers we
   read, the first stage (wage bite, coverage ladder, care bite) is measured and shown
   *before* the outcome — it's a design-stage object. Rubin tells you *why* that ordering
   matters: you're checking that the "experiment" actually happened (treatment moved something
   real) without letting the outcome contaminate the check. Bite is Rubin-compliant by
   construction.

2. **A harness enforces outcome-blindness the way randomization does.** The reason "design
   trumps analysis" is hard to live by is that outcomes are *right there* and the temptation to
   peek is constant. A harness that literally puts outcomes in a later folder — that makes you
   finish target, bite, balance, and event-study design first — is a machine for manufacturing
   the objectivity Rubin says you can only get by not looking. That's the pitch: **the harness
   is how you keep the outcome data "not available at this stage" on purpose.**

---

## Strengths / limits (brief)

**Strengths.** The most quotable, teachable statement of the design-first creed; the
encouragement-design example proves the discipline is *possible* even with noncompliance;
the "refuse when there's no overlap" ethic is bracing and rare.

**Limits.** It's a manifesto, not a recipe — "an aspect of 'art'" (p. 22) does a lot of work
where you'd want an algorithm. It's framed around selection-on-observables / propensity
design; your DiD world buys identification from *parallel trends* instead, so the analogue of
"balance" is pre-trend and event-study design, not covariate overlap per se. The spirit
transfers cleanly; the specific tools need translation.

---

### Files produced by this read
- `harness_build/split_rubin_design_trumps_analysis/summary_pp*.md` — 9 per-chunk summaries.
- This review: `REVIEW_Rubin.md`. Companions in this folder:
  `REVIEW_Miller_Johnson_Wherry.md`, `REVIEW_Dias_Fontes.md`.
