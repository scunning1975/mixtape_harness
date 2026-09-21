---
name: covariates
description: Interview-based covariate selection for DiD designs. Walks the user through 5 questions ONE AT A TIME, then synthesizes the "10-chapter book by the world's leading expert on Y(0) trends" — those 10 chapters are the covariates. Grounded in Heckman, Ichimura & Todd (1997, RESTUD) approach: find the X that drives E[Y(0)] trends. Then suggests data sources and fetches the data once confirmed.
---

# /covariates — covariate selection by interview

## Theory

The plug-in for the missing counterfactual is justified on the grounds that treated and control are comparable on observables necessary for replacement. For ATT:

$$E[Y(0) \mid D=1, X=x] = E[Y(0) \mid D=0, X=x]$$

Evidence comes from conditional parallel trends:

$$E[Y(0) \mid D=1, \text{Post}, X=x] - E[Y(0) \mid D=1, \text{Pre}, X=x] = E[Y(0) \mid D=0, \text{Post}, X=x] - E[Y(0) \mid D=0, \text{Pre}, X=x]$$

**Heckman, Ichimura & Todd (1997, RESTUD).** They regress $\Delta Y(0) \sim a + \beta X + e$ on $D=0$ only, then predict $\Delta Y(0)$ (call it $\hat\mu$) for the treated. Finding the X that satisfy conditional PT is spiritually equivalent to finding the X that drive $E[Y(0)]$ trends — "the important ordinary drivers of the untreated potential outcome."

## Interview protocol

Ask the FIVE questions below ONE AT A TIME. Wait for the user's answer before asking the next. Take notes on each.

**Q1.** What is your outcome Y, and what is the population/unit and time period of analysis? (e.g., "monthly employment per 100k, US counties, Jan 2024 – May 2026")

**Q2.** Imagine the untreated path of Y — what would have happened to Y in the absence of treatment. What economic, demographic, political, technological, or seasonal forces drive that path? List 3-5.

**Q3.** What predicts WHO gets treated? In your setting, what makes a unit more likely to receive treatment? (Selection mechanism — distinct from Q2.)

**Q4.** What forces affect Y differentially across units, especially between would-be-treated and would-be-control? Are there shocks that hit one group harder than the other?

**Q5.** What measurable, pre-treatment-determined characteristics capture the forces from Q2-Q4? (Actual variable names you'd use.)

## Synthesis

After all five answers, say to the user:

> Imagine the world's leading expert on Y(0) trends — for the exact units of your data, weighted as you'd weight them, in the place you are, in the time period you are. They have written a book with 10 main chapters. The titles of those 10 chapters ARE the covariates we need.

Then generate the 10-chapter table of contents. Cross-reference with the user's Q1-Q5 answers — every force the user named MUST appear as a chapter (or be explicitly justified for omission). Add obvious omissions the user missed. Output as a numbered 10-line list, each line = chapter title = covariate name.

## Data sourcing

For each of the 10 covariates:
1. Suggest 1-2 specific data sources. Likely candidates: ACS (census.gov), FRED (fred.stlouisfed.org), BLS (bls.gov), MIT Election Lab (electionstudies.org), USDA ERS (ers.usda.gov for RUCC), county-level admin data.
2. Ask the user if they have a preferred alternative source.
3. Once confirmed, fetch the data (or write a script that does, e.g. via the censusapi R package or pandas-datareader).

## Output

Write the final list to `data/covariates_proposed.md` with columns:

| # | Covariate | Why (Q-link or expert reasoning) | Source | Variable name in dataset |

Then update the relevant DiD checklist (checklists/did_checklist.md, Step 2) with a backlink to data/covariates_proposed.md.

## When to invoke

- User runs `/covariates` directly.
- User starts a DiD checklist (Step 2 of checklists/did_checklist.md).
- User asks "what covariates should I use" or equivalent.
