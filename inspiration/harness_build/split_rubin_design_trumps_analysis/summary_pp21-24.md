# Rubin, "For Objective Causal Inference, Design Trumps Analysis" — pp. 21-24

## Argument on these pages
These pages close the propensity-score "doctor-visit" example and open the third
(cardia-cancer / large-vs-small-volume-hospital) example. Rubin shows how, at the
design stage, balance is assessed bin-by-bin so that a randomized block experiment
is effectively "reconstructed" from observational data. He then introduces a harder
case: sometimes the hypothetical underlying experiment must be conceptualized as a
randomized block *with noncompliance* (an "encouragement" design), which motivates
principal stratification.

## Key concepts / definitions
- **Reconstructing a randomized block experiment**: balance checked for all
  covariates in all propensity-score bins with both treated and control units.
- **Prognostically important covariates**: imbalance in outcome-related covariates
  matters more than imbalance in irrelevant ones — an "aspect of art."
- **Encouragement / noncompliance design**: assignment randomizes only the
  *encouragement*; people cannot be forced to take treatment or control.
- **Love plots** (Ahmed et al. 2006): visual diagnostics of covariate balance
  before vs. after subclassification.
- **Unconfoundedness**: home-hospital-type assignment treated as random within
  levels of measured covariates X (age, date, sex, urbanization).

## Running example
Karolinska cardia-cancer data: 158 patients (79 large-volume, 79 small-volume
hospitals), 1988-1995. Policy question: can small-volume centers be closed without
harming survival? Propensity scores (with nonlinear terms in X) restricted ages to
35-84, leaving 148 patients sorted into five subclasses. Transfers complicate
things: 33 of 75 small-hospital-diagnosed patients transferred to large hospitals.

## DESIGN-BEFORE-ANALYSIS
- Balance is the object of the design stage; the goal is to make observational data
  look like a "reconstructed randomized block experiment."
- "Better guidance on how to conduct this process more systematically is needed"
  (points to Imbens and Rubin 2008b, Ch. 13-14) — design as a disciplined procedure.
- The design phase is declared *complete* before any model-based within-bin
  adjustments and before ranking — outcomes not yet consulted.
- Warning about investigator judgment: correcting imbalance in prognostically
  important covariates is partly "art," so "the field of statistics will always
  benefit from scientifically informed thought."

## Quotable lines
- "there is an aspect of 'art' operating here" (p. 22)
- "the design phase was complete, except for the specification of model-based
  adjustments" (p. 22)
- assignment "considered by medical experts to be unconfounded, that is,
  essentially assigned at random within levels of measured covariates" (p. 23)
