# Rubin (2008), "Design Trumps Analysis" — pp. 5–8

## Overview of the argument
Section 2 reviews the two RCM parts relevant to design: (1) units/treatments/potential outcomes and (2) the assignment mechanism.

## Part one — potential outcomes (pp. 5–6)
A **unit** is a physical object at a place and time t. A **treatment** is an action that can be initiated or withheld at t; withholding = control. Each unit has two **potential outcomes** at future time t\* > t: Y(1) if treated, Y(0) if control. The **causal effect** is the comparison (difference, ratio, etc.) of Y(1) and Y(0) on the *same* unit.

- **SUTVA** (Stable Unit-Treatment Value Assumption): lets the full set of potential outcomes be an N-row array with columns Y(0), Y(1).
- **Fundamental problem of causal inference** (Holland 1986; Rubin 1978): only one of Y(0), Y(1) is ever observed per unit.
- **Covariates X:** take the same value regardless of treatment (age, pre-treatment blood pressure). The array [X, Y(0), Y(1)] is "the science."
- Part one is conceptual and "should be conducted before seeing any data, especially before seeing any outcome data." It forces manipulative thinking: **"No causation without manipulation."**
- The **observed-outcome notation** Y_obs = W·Y(1) + (1−W)·Y(0) is "inadequate in general" because it "mixes up the science... with what is done to learn about the science" — the assignment W. Errors flow from it (Lord's paradox; even Fisher).

## Part two — the assignment mechanism (pp. 6–8)
The assignment mechanism is a probability model Pr(W | X, Y(0), Y(1)) for how units got treatment vs. control.
- **Unconfounded:** Pr(W|X,Y(0),Y(1)) = Pr(W|X).
- **Probabilistic:** 0 < e_i < 1, where e_i ≡ Pr(W_i=1|X_i) is the **propensity score**.
- When both hold ("strongly ignorable," Rosenbaum & Rubin 1983), the assignment mechanism ∝ product of unit-level propensity scores — "which emphasizes the importance of propensity scores in design."
- Contrast with economics: Roy (1951) self-optimizing behavior and Haavelmo (1944) supply/demand were described *without* explicit assignment-mechanism notation; regression models predicting Y_obs from X and W conflated assumptions about the science and the assignment, "and therefore could, and sometimes did, lead to mistakes."

## DESIGN-BEFORE-ANALYSIS
- The propensity score e_i = Pr(W_i=1|X_i) is "the most basic ingredient of an unconfounded assignment mechanism," and its use "for objectively designing observational studies" is the whole point.
- Assignment-based inference (Neyman's unbiasedness/CIs, Fisher's p-values for sharp nulls) proves "the model for the assignment mechanism is **more fundamental** for inference for causal effects than a model for the science." FDA drug approval treats assignment-based analysis as the gold standard.
- The third RCM part (Bayesian model for the science, e.g., OLS regression) is optional and "generally not relevant to the design of observational studies."
- Objectivity comes from getting the *assignment mechanism* right, before and independent of outcomes — not from a clever outcome model.

## Quotable lines
- "No causation without manipulation." (Rubin 1975, quoted p.6)
- The observed-outcome notation "mixes up the science... with what is done to learn about the science via the assignment of treatment conditions to the units." (p.6)
- "the model for the assignment mechanism is more fundamental for inference for causal effects than a model for the science." (p.8)
