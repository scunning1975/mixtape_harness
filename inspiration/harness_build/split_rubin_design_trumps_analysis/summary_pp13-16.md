# Rubin (2008), "Design Trumps Analysis" — pp. 13–16

## Overview of the argument
The smoking example completes; propensity-score methodology is introduced for the many-covariate case; and the first real-data example (GAO breast cancer) begins, showing a careful observational study reproducing randomized-trial conclusions.

## Completing the Cochran smoking example (p.13)
Cochran subclassified age into nine equal subclasses. Within each, treated (cigarette) and control (cigar/pipe) age distributions are nearly identical — "just as if the men had been randomly assigned within the age subclasses" — and both conditions are present in every subclass. **Design complete → now look at outcomes.** Averaging over the nine blocks, cigarette-smoker death rates are ~50% higher. Strikingly, "the full data set with no subclassification leads to nearly the opposite conclusion" — a vivid demonstration that design (subclassification) drives the answer.

The curse of dimensionality motivates propensity scores: 4 covariates × 5 levels = 625 subclasses; 20 dichotomous covariates = 2^20 > 1 million subclasses, most with a single unit and no treatment–control comparison.

## Propensity score methodology (§4.2, pp.13–14)
Rosenbaum & Rubin (1983): a class of methods to achieve balance with many key covariates.
- **The propensity score is "the observational study analogue of complete randomization"** — its purpose is to eliminate systematic bias, not increase precision (though sometimes it does).
- Defined as Pr(treatment | observed covariates), including decision-maker indicators/interactions. Rarely known; estimated (often logistic regression, "by no means mandatory or even ideal").
- **The critical aspect: it models the reasons for treatment assignment at the level of the decision maker.**
- The estimated linear propensity score is then treated as a single covariate (like age) for matching/subclassification.
- **Then check balance.** If the score is correct and balanced, R&R (1983) prove balance is achieved on ALL observed covariates. "The achieved balance within matched pairs or subclasses must be assessed and documented before the design phase is finished."

## GAO breast cancer example (§4.3, pp.15–16)
Question: is breast-conserving surgery (BC) as good as mastectomy (Mas) for less-severe (node-negative) cancer? Six randomized trials (Table 1) showed ~equal 5-year survival; NCI recommended BC. GAO worried this wouldn't generalize to ordinary surgeons/patients, but a new RCT was infeasible. So GAO used the observational **SEER** database (~5,000 relevant cases, ~20 key covariates, outcomes available). **Outcomes stripped; design phase proceeded.** Decision makers = surgeon + woman (± family). Key covariates: tumor size, age, marital status, plus less-obvious ones (urbanization, region, year, race, interactions like age×marital status) — all present in SEER.

## DESIGN-BEFORE-ANALYSIS
- The lament: many propensity-score papers "do not use them correctly" — they "use the outcome data to help choose propensity score models, and use the propensity score only as a predictor in a regression model with the outcome... as the dependent variable." That is exactly the analysis-stage cheating the design discipline forbids.
- Propensity score = the observational analogue of randomization: it targets bias elimination, mimicking what randomization does automatically.
- Balance must be assessed and *documented* before the design phase ends — objectivity is a paper trail, produced before outcomes are seen.
- Same-answer promise: careful design "can (not necessarily will) reach the same general conclusions as expensive randomized experiments."

## Quotable lines
- "the full data set with no subclassification leads to nearly the opposite conclusion." (p.13)
- "The propensity score is the observational study analogue of complete randomization... its use is not intended to increase precision but only to eliminate systematic biases." (p.14)
- "many of the articles that use propensity score methods do not use them correctly... use the outcome data to help choose propensity score models." (pp.13–14)
- "such balance was achieved—not perfectly, but close enough to believe in the hypothetical underlying randomized block experiment that led to the observed data." (p.17, from balance work described here)
