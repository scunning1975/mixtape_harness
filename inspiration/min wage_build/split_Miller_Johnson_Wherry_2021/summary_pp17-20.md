# Miller, Johnson & Wherry (2021) — Summary pp. 17–20

## What these pages argue
These pages complete the robustness/validity battery (confounders, placebo tests), report subgroup/heterogeneity analyses, and begin the interpretation section that scales reduced-form mortality by coverage changes into an implied treatment effect on the treated.

## Key concepts / equations
- Placebo tests: (1) shift sample to pre-ACA period (mortality 2004–2013, ACS 2004–2009), treating expansions as if in 2010+t; (2) 10,000 random re-assignments of expansion status → placebo distribution.
- Less-affected groups: age 65+ (Medicare) and ages 55–64 at ≥400% FPL.
- Triple-difference model vs. placebo groups.
- Scaling: reduced-form mortality ÷ first-stage coverage change = implied treatment effect (LATE / compliers, Imbens-Angrist 1994).

## Main numbers / results
- Placebo (pre-ACA period + random reassignment): no effect on Medicaid coverage or mortality; actual estimate falls below 5th percentile of placebo distribution.
- Age 65+: no coverage effect, no mortality effect.
- 400% FPL+: small but sig. Medicaid enrollment gain; small (some years sig.) mortality reduction; enrollees highly selected (high mortality).
- Ages 19–64: Medicaid enrollment +12.7pp; mortality -3.9% (not sig.). Largest sub-effect at 50–54 (not sig.).
- Age bins: largest, significant mortality reductions at 59–61 and 62–64.
- Subgroups: larger effects for white non-Hispanic and males; no effect for non-Hispanic Black; no marital-status differences.
- Uninsured-at-survey (~30% subset): mortality -0.150pp (10.3% of counterfactual 1.46%) vs. -0.132pp (8.1%) main.
- Scaling: 0.375 accumulated Medicaid years → 1 year Medicaid cuts mortality 0.35pp (=0.132/0.375). Contemporaneous enrollment +12.8pp → 1.03pp (=0.132/0.128). Contemporaneous insurance +4.4pp.

## Figures / tables on these pages
- Figure III (triple-diff rows), Figure IV (placebo panels: pre-ACA, age 65+, 400% FPL+), Appendix Figure A4 (placebo distribution), A5 (age bins), Tables A9, A10, A11, A12, Table I.

### DiD ELEMENTS
1. **BITE (first stage):** Contemporaneous Medicaid enrollment **+12.8pp**; contemporaneous insurance coverage **+4.4pp** (Table I); accumulated **0.375** additional Medicaid years. Ages 19–64: Medicaid **+12.7pp**. 400% FPL+ group: small sig. enrollment gain. All age subgroups show sig. enrollment increases.
2. **FALSIFICATIONS:** Pre-ACA placebo (no effect); 10,000-draw random-assignment placebo (actual below 5th pctile); age 65+ (Medicare) no coverage/no mortality effect; China-shock, opioid-policy, demographic controls leave estimate unchanged.
3. **EVENT STUDIES:** Placebo event studies (Figure IV rows) flat pre-ACA; some sig. reductions for 400% FPL+ group in later years.
4. **MAIN RESULTS:** DD -0.132pp reaffirmed; uninsured subset -0.150pp (10.3%). Triple-diff estimates slightly smaller but still sig.
5. **MECHANISM:** Larger effect where baseline uninsurance higher (uninsured subset); heterogeneity by race/sex; adverse selection noted (400% FPL enrollees highly selected). Implied per-year-Medicaid effect 0.35pp; contemporaneous 1.03pp.

### DATA DETAILS
- ACS survey years 2008–2013 linked to mortality 2008–2017 (main); placebo uses ACS 2004–2009 + mortality 2004–2013. CMS admin Medicaid enrollment for accumulated-years. HRS (Table A11) for cumulative coverage of uninsured subset. Sample: ~3.7M meet criteria in expansion states. Ages 55–64 in 2014 main; heterogeneity by age/race/sex/marital/education (<HS or <138% FPL).
