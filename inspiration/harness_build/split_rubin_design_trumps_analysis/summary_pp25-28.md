# Rubin, "For Objective Causal Inference, Design Trumps Analysis" — pp. 25-28

## Argument on these pages
Rubin develops the cardia-cancer example into a full principal-stratification design.
Because *treating* hospital type is confounded (transfer decisions depend on
unmeasured factors), a direct propensity-score analysis of treating type would be
"unsatisfactory." Instead he adopts the template of a randomized experiment with
noncompliance: home-hospital assignment is the (as-good-as-random) encouragement,
and transfers are noncompliance. The design stratifies on the bivariate intermediate
outcome — treating hospital under each possible assignment — even though only one arm
is observed. Crucially, this is all done using intermediate (treatment-receipt) data
but NOT survival outcomes.

## Key concepts / definitions
- **Home hospital type h** (ℓ = large, s = small): where diagnosed; assumed
  unconfounded.
- **Treating hospital type T** (L = large, S = small): where actually treated;
  confounded.
- **Intermediate outcome**: the bivariate (T(ℓ), T(s)); a *partially observed
  covariate*.
- **Principal strata**: LL, LS, SL, SS defined by (T(ℓ), T(s)); LS = compliers.
- **Monotonicity / no-defier assumption**: SL stratum empty (introduced here,
  developed p. 28+).
- Balance diagnostics (Figs. 7-8): difference-in-means for binary covariates and
  t-statistics for continuous covariates, initial vs. after subclassification.

## Running example
Tables 3-7 report, per propensity subclass, observed counts of h and T plus the
inferred principal strata and approximate LS (complier) counts under monotonicity.
Transfers into large hospitals are common; only subclass 5 shows any ℓ → S transfers.

## DESIGN-BEFORE-ANALYSIS
- The single most load-bearing line: "the design phase does here look at intermediate
  outcome data, treating hospital type, but not the outcome data on survival, on
  which decisions will be based. Survival data are not available at this stage!" (p. 26)
- Choosing the right *template* (encouragement design vs. plain block) is itself a
  design decision, made before outcomes.
- Design flags a feasibility problem in advance: whether compliers (LS) even exist
  in each subclass is "a critical design issue with this template" (p. 27).
- Rejecting a direct treating-type analysis — even with perfect covariate balance —
  because key covariates are unmeasured: a design-stage judgment about confounding,
  not an outcome-driven one.

## Quotable lines
- "the design phase does here look at intermediate outcome data ... but not the
  outcome data on survival ... Survival data are not available at this stage!" (p. 26)
- "there is no doubt that ... the assignment of treating hospital type is
  confounded" (p. 25)
- "a critical design issue with this template" (p. 27)
