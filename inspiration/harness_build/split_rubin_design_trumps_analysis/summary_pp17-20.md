# Rubin (2008), "Design Trumps Analysis" — pp. 17–20

## Overview of the argument
The GAO breast-cancer design finishes and its results are read; then the large-sample marketing example (sales reps visiting doctors) demonstrates propensity-score subclassification, balance improvement, and — critically — the honest recognition of regions with NO overlap where causal inference must be refused.

## GAO breast cancer, completed (§4.3, p.17–18)
Propensity scores estimated by logistic regression; women ranked and split into five 20% subclasses. Within each subclass, balance was checked on the propensity-score covariates AND all other important covariates (e.g., average treated age ≈ control age; proportion married ≈). When a subclass showed less balance than randomization would give, "terms were added to the propensity score model and balance was reassessed" — the iterative design loop. Balance was achieved "not perfectly, but close enough to believe in the hypothetical underlying randomized block experiment."

**Results (Table 2):** BC vs. Mastectomy 5-year survival across the five subclasses is essentially equal — consistent with the randomized trials, "no advantage to recommending one treatment over the other." Note: overall SEER survival is lower than the specialized trial centers (Table 1), as expected. Rubin also flags interpretation: if the effect were truly constant, the drift across subclasses could signal "a confounded and nonignorable treatment assignment (i.e., an omitted key covariate)."

## Marketing example (§4.4, pp.18–20)
Large-sample power: 100,000 "treated" doctors (visited ≥ once by a sales rep detailing a weight-loss drug) vs. 150,000 control (not visited). Outcome Y = scripts written in the following six months, obtained LATER from a third-party vendor — so the design is naturally outcome-free at design time. Over 100 covariates (sex, race, age, years since degree, practice size, specialty, prior scripts).

Decision maker = the sales rep, who prefers high-prescribing, large-practice, relevant-specialty doctors. **Figures 1–2** show dramatic initial imbalance: visited doctors have much higher prior-Rx scores (mean 55.9 vs 38.2) and different specialty mix (ob-gyns visited less — they don't prescribe weight-loss drugs to pregnant patients).

Propensity scores estimated by logistic regression, binned into 15 subclasses. **Overlap failure is named honestly:** in the 2 highest bins (linear PS > 1.0) there are ONLY visited doctors; in the 4 lowest bins (< 0.1) ONLY not-visited. "No causal inferences are possible for them without making model-based assumptions relating outcomes to covariates for which there are no data to assess the underlying assumptions." In the other nine overlapping bins, within-bin covariate distributions become "strikingly more similar" (Figs 4–5 vs 1–2) — so similar that visited doctors look like "a random sample from all doctors in that bin."

## DESIGN-BEFORE-ANALYSIS
- Balance is iterative and pre-outcome: estimate PS → check balance on all covariates → add terms → reassess, all before outcomes.
- **The strongest lesson of the marketing example: where there is no overlap, refuse to estimate.** Causal inference in no-overlap regions rests only on "unassessable assumptions" — so it should not be attempted. Objectivity means knowing where the data cannot answer.
- The design outputs the analogue of a randomized block experiment: within each overlapping bin, treatment looks randomly assigned given covariates.
- Outcomes arriving later (next year's vendor data) make outcome-free design natural here — the ideal Rubin urges everywhere.

## Quotable lines
- "No causal inferences are possible for them without making model-based assumptions relating outcomes to covariates for which there are no data to assess the underlying assumptions." (p.20)
- "they are so similar that one could believe that, within that bin, the visited doctors are a random sample from all doctors in that bin." (p.20)
- "these changing results across propensity subclasses could be viewed as evidence of a confounded and nonignorable treatment assignment (i.e., an omitted key covariate)." (p.18)
- "such balance was achieved—not perfectly, but close enough to believe in the hypothetical underlying randomized block experiment that led to the observed data." (p.17)
