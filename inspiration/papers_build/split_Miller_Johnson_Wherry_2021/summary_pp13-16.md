# Miller, Johnson & Wherry (2021) — Summary pp. 13–16

## What these pages argue
These pages close the first-stage section and open the core mortality results. The ACA Medicaid expansions produced large first-stage effects on eligibility, enrollment, and coverage, and — critically — reduced mortality among low-income adults ages 55–64. The authors then begin the robustness battery: staggered-timing concerns (Sun-Abraham, Goodman-Bacon) and differential pre-trends.

## Key concepts / equations
- Event-study equation (1): event-time coefficients relative to expansion year 0.
- Counterfactual mortality rate: post-expansion mortality in expansion states + |event-study coefficient|, used to express reduced-form effects as % reductions.
- Goodman-Bacon decomposition of the two-way FE DD; Roth (2019) pre-trend power/bias.

## Main numbers / results
- Cumulative insurance coverage (HRS): +0.39 additional years of continuous coverage post-expansion (sig. only at 10%; N=1,359 vs. 566,000 in ACS panel).
- Mortality event study: year 0 = -0.089pp; years 1–2 ≈ -0.1pp+; year 3 = -0.208pp. All significant.
- Proportionate reductions: 7.0% (yr 0), 7.9% (yr 1), 8.2% (yr 2), 11.9% (yr 3). Counterfactual rates: 1.28, 1.51, 1.60, 1.75%.
- Pooled DD: -0.132pp = 9.4% vs. sample mean, 8.1% vs. counterfactual (1.63%).
- Cause of death (MDAC, exploratory): internal/disease-related deaths fall (DD highly sig.); external deaths do not fall (slight upward pre-trend). Cardiovascular ~38% and endocrine/metabolic ~18% of internal-mortality reduction.
- Goodman-Bacon: only 11% of DD from differently-timed comparisons; clean estimate slightly larger.
- Pre-trend power: can detect -0.03235pp linear trend at 80% power; worst-case bias by year 3 = -0.08873pp vs. actual -0.208pp (2.3x larger).

## Figures / tables on these pages
- Figure II (mortality event study), Table I (col. 6 + top DD panel), Table II (cause of death internal/external/amenable), Figure III (DD robustness rows), Appendix Tables A3–A7, Appendix Figures A2–A3.

### DiD ELEMENTS
1. **BITE (first stage):** Cumulative insurance coverage +0.39 years (HRS, p<0.10); text confirms large/significant effects on eligibility, enrollment, and coverage for the target sample; accumulated more years of Medicaid + insurance exposure.
2. **FALSIFICATIONS:** External-cause mortality does NOT decline (should be insurance-insensitive). Pre-trend power analysis (Roth 2019). Robustness to opioid-policy controls, local labor demand, county economic characteristics, Medicare age-in (ages 55–61 subgroup, Table A7).
3. **EVENT STUDIES:** Figure II — pre-expansion coefficients near zero/insignificant; effect emerges year 0, grows to year 3. Sun-Abraham + 2014-only expanders (Figure A2) similar.
4. **MAIN RESULTS:** Pooled DD = **-0.132pp** annual mortality, 9.4% (mean) / 8.1% (counterfactual). Year-by-year -0.089 to -0.208pp.
5. **MECHANISM:** Internal (disease) deaths drive result; cardiovascular ~38%, endocrine/metabolic (diabetes) ~18%; skin/subcutaneous (diabetes risk factor) small sig. negative. External deaths unaffected — points to health-care channel.

### DATA DETAILS
- ACS-mortality panel N≈566,000; HRS supplementary N=1,359. CMS administrative Medicaid enrollment (Table I). MDAC = multiple-cause-of-death administrative file (smaller sample, shorter follow-up, exploratory). Four treatment cohorts: 21 states expand 2014, 3 in 2015, 2 in 2016, 1 in 2017. Sample: ages 55–64 in 2014, low-income/low-education.
