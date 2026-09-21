# Cengiz, Dube, Lindner & Zipperer (2019), pp. 41–44 (journal pp. 1445–1448)

## What these pages argue
These pages show how the employment effect varies with the **bite** of the minimum wage (the Kaitz index) across events, then open Section IV, which uses the distributional approach to **diagnose the classic two-way fixed effects on log minimum wage (TWFE-logMW)** specification. The central message: higher-bite minimum wages produce more missing jobs but a nearly identical number of excess jobs, so net employment is flat; and the classic TWFE-logMW model attributes disemployment to implausible upper-tail bins, revealing confounding.

## Key concepts / equations
- **Kaitz index** = new minimum wage / median wage at the time of increase — a measure of how binding the policy is.
- **TWFE-logMW distributed-lags model:** for each $1 wage bin, regress bin employment per capita on contemporaneous log minimum wage plus **four annual lags and two annual leads**, with state and year fixed effects; cumulative post-treatment effect averaged over event dates 0–4, divided by mean employment-to-population, gives an elasticity per bin. Weighted by state population; standard errors clustered by state.

## Main results / numbers
- Across events, the coefficient on Kaitz is **−0.133 (s.e. 0.034)** for missing jobs and **+0.139 (s.e. 0.057)** for excess jobs — nearly offsetting.
- Net employment slope vs. Kaitz is **0.006 (s.e. 0.048)** — essentially flat over minimum-to-median ratios spanning **37% to 59%**.
- In the TWFE-logMW model, minimum wage shocks show large employment shifts in the **$6–$9/hour** bins (drop at $6–$7, rise at $8–$9) — the expected bunching. But the model also shows implausible negative effects far above the minimum.

## Figures / tables
- **Figure V (Panels A & B):** binned scatter of missing jobs, excess jobs (Panel A), and total employment change (Panel B) against the Kaitz index, for **130 events** (excludes 8 noisy DC events). Controls: decade dummies, state unemployment rate at time of increase, urban share, Republican-leaning indicator; weighted by state population.
- **Figure VI:** employment elasticity by $1 wage bin from the TWFE-logMW model, with a running-sum (cumulative) line and a final aggregate bar; reported aggregate **employment elasticity = −0.089 (s.e. 0.025)**.

### DATA DETAILS
- Source: **Current Population Survey (CPS)**, **1979–2016**, total wage-earning employment.
- For Figure VI, employment is divided into **inflation-adjusted $1 wage bins by state and by year**; outcome is jobs per capita in each state-wage bin.
- Kaitz analysis covers **130 event-specific estimates** (138 minus 8 DC events); Online Appendix Figure A.10 gives the raw scatter including DC.
- Aggregate elasticity outcome is the **state-level employment-to-population rate**.
- Weighting: **state population**; SEs clustered at **state** level.
