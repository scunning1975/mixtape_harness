# Rubin, "For Objective Causal Inference, Design Trumps Analysis" — pp. 29-32

## Argument on these pages
The technical payoff and the paper's Discussion. Under monotonicity (no defiers),
observed groups map to principal strata: ℓ → S must be SS, s → L must be LL, while
ℓ → L and s → S are mixtures of compliers (LS) and noncompliers. Stratum proportions
are recovered by simple subtraction within each propensity subclass. Rubin then defines
ITT and CACE (= ITT_LS), invokes exclusion restrictions to zero out the noncomplier
effects, and derives the instrumental-variables estimator CACE = ITT / π_LS. The
planned analysis is Bayesian, within subclass then averaged. Page 32 is the Discussion
+ start of references.

## Key concepts / definitions
- **Monotonicity**: SL empty, so only LL, LS, SS remain; "very plausible" here.
- **ITT**: average of Y_i(ℓ) − Y_i(s) over all N patients.
- **CACE ≡ ITT_LS**: Complier Average Causal Effect (Imbens and Rubin 1997); the only
  stratum where treating-type effects are learnable.
- **Exclusion restrictions**: for i ∈ LL and i ∈ SS, Y_i(ℓ) = Y_i(s) — no effect of
  assignment for always-takers/never-takers, since outcome depends on where treated
  not diagnosed.
- **IV estimator**: ITT = π_LS·ITT_LS ⟹ ITT_LS = ITT / π_LS.

## DESIGN-BEFORE-ANALYSIS
The Discussion (p. 32) is the paper's thesis in concentrated form:
- Observational studies "need to be designed to approximate randomized experiments,"
  requiring "careful thought and execution, and not simply running mindless regression
  programs and looking at coefficients."
- Design is *harder* than for the analogous randomized experiment.
- The core objectivity principle: "final outcome data cannot be used in design without
  compromising the objectivity of the study design."
- Propensity scores = tools for "reconstructing the underlying hypothetical experiment";
  principal stratification handles complications like noncompliance.
- Extension to *actual* randomized experiments: for covariates not used in
  randomization, applying these design techniques "with no access to final outcome data,
  preserves the objectivity of the experiment, whereas model-based adjustments, unless
  fully specified a priori, would compromise that objectivity" (vouchers: Barnard et al.
  2003; vertical transmission: Zell et al. 2007).

## Quotable lines
- "final outcome data cannot be used in design without compromising the objectivity of
  the study design" (p. 32)
- "not simply running mindless regression programs and looking at coefficients" (p. 32)
- "stay focused on approximating a plausible hypothetical underlying randomized
  experiment" (p. 32)
- "model-based adjustments, unless fully specified a priori, would compromise that
  objectivity" (p. 32)
