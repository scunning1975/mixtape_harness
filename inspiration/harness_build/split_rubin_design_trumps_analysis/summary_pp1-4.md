# Rubin (2008), "For Objective Causal Inference, Design Trumps Analysis" — pp. 1–4

## Overview of the argument
These opening pages state the thesis and its intellectual lineage. Randomized experiments are the "gold standard" for *objective* causal inference; observational studies are "fraught with problems that compromise any claim for objectivity." Rubin's claim: observational studies must be **carefully designed to approximate randomized experiments — in particular, without examining any final outcome data.** A candidate dataset may have to be *rejected* for lacking key covariates or lacking overlap in covariate distributions between treatment and control, "often revealed by careful propensity score analyses."

He recounts the historical dichotomy: for decades, randomized-experiment causal inference (Fisher, Kempthorne, Cochran & Cox, Cox) was an entirely distinct endeavor from observational causal inference (Blalock, Campbell & Stanley, Cook & Campbell, Rothman, etc.). This began to change in the 1970s when Rubin (1974) extended Neyman's (1923) potential outcomes — used for randomized experiments — to observational studies, and defined **assignment mechanisms** (Rubin 1975), with randomized experiments as special cases. Both study types then lived in one framework Holland (1986) named the **Rubin Causal Model (RCM)**.

## Key concepts / definitions
- **Objectivity of randomization:** decision rules are explicit, each unit's treatment probability strictly between 0 and 1.
- **Propensity scores** (Rosenbaum & Rubin 1983): known from the experiment's design; sufficient to get unbiased average-treatment-effect estimates.
- **Balance:** randomization achieves, in expectation, balance on ALL pre-treatment covariates — measured *and unmeasured*.
- **Prospective / outcome-free:** randomized experiments are "automatically designed without access to any outcome data of any kind."
- **RCM has three parts:** (1) potential outcomes (conceptual), (2) assignment mechanism, (3) optional Bayesian model for the science. Focus here is design, i.e., parts 1–2.

## DESIGN-BEFORE-ANALYSIS
- Central thesis in Rubin's own words: observational studies must "duplicate" the appealing features of randomized experiments, seeking "as closely as possible, the same answer that would have been obtained in a randomized experiment... In this process of design, the usual models relating observed final outcome data to observed covariates and treatment indicators play no part... The only models that are used relate treatment indicators to observed covariates."
- Definition of design: "all contemplating, collecting, organizing, and analyzing of data that takes place **prior to seeing any outcome data.**" Includes matching, subclassification, and specifying the primary analysis plan. "However, any analysis that requires final outcome data to implement is not part of design."
- Randomization's third feature: "there is no way to obtain an answer that systematically favors treatment over control, or vice versa" — the objectivity guarantee.
- Warning on misplaced emphasis: design steps "are often effectively ignored in observational studies relative to details of the methods of analysis," partly because "technical dexterity can be more valued than practical wisdom."
- Continuum, not dichotomy: a badly-run RCT (90% noncompliance, dropout) can be worse than a carefully designed observational study.

## Quotable lines
- "For obtaining causal inferences that are objective... carefully designed and executed randomized experiments are generally considered to be the gold standard." (p.1)
- "observational studies have to be carefully designed to approximate randomized experiments, in particular, without examining any final outcome data." (p.1)
- "technical dexterity can be more valued than practical wisdom." (p.4)
