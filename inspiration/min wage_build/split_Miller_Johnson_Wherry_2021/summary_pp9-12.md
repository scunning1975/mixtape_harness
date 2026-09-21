# Miller, Johnson & Wherry (2021) — Summary, pp. 9-12

## What these pages argue
Finishes Empirical Strategy (Sec. IV) and covers Results Sec. V.A — Medicaid Eligibility, Enrollment, and Insurance Coverage: the paper's **FIRST STAGE / BITE**. Establishes that the targeted sample experienced large, well-identified increases in eligibility, enrollment, and coverage.

## Empirical strategy details
- Event study (Eq. 1) plus a summary **difference-in-differences** using Expansion_s × Post_t (turns on in year of expansion).
- Linear probability model, heteroskedasticity-robust SEs **clustered at state level**; ACS survey weights.
- Nonlinear checks (logit, Cox PH) modestly smaller but still large/significant (App. Table A2); inference robust to Census-division clustering and Conley (1999) spatial correlation (App. Table A8).
- Because the fixed cohort ages, mortality rises mechanically over time; they build a **post-period counterfactual** = average post-period mortality in expansion states minus the DD estimate (per Goodman-Bacon 2016), not the pre-period rate.
- Expansion-year coding: expansions Jul 1 or later coded to next year. Lists 2014 expanders (AR, AZ, CA, CO, CT, HI, IL, IA, KY, MD, MI, MN, NJ, NM, NV, ND, OH, OR, RI, WA, WV); 2015 (NH, PA, IN); 2016 (AK, MT); 2017 (LA).

## The FIRST STAGE / BITE — main quantitative content
- **Medicaid eligibility rose 49-51 pp** per post-expansion year (vs. year just before).
- **Probability enrolled in Medicaid in a year: +12.8 pp.**
- **+43 additional Medicaid-enrolled days per year** (non-enrollees coded 0 days).
- **Cumulative Medicaid: +0.38 years on average; ~0.67 additional years by end of sample.**
- **Uninsurance (ACS): −4.4 pp on average** post-expansion (years 1-2 larger than year 3, aging into Medicare).
- **NHIS uninsurance: −4.9 to −9.5 pp** across years; **average −5.8 pp** (App. Fig A1, Table A3).
- Substantial "crowd-out": many new enrollees would have had some coverage otherwise (partly subsidized exchange).

## Figures/Tables on these pages
- **Figure I** — first-stage coverage/eligibility results.
- **Table I** — first five columns report eligibility, enrollment, days, cumulative years, uninsurance.
- **Appendix Figure A1 / Table A3** (NHIS, self-reported Medicaid); Appendix Tables A2, A8.

### DiD ELEMENTS
1. **BITE / FIRST STAGE** (core of these pages): eligibility **+49-51 pp**; annual Medicaid enrollment **+12.8 pp**; **+43 enrolled days/yr**; cumulative Medicaid **+0.38 yrs (0.67 by end)**; ACS uninsurance **−4.4 pp**; NHIS uninsurance **−4.9 to −9.5 pp (avg −5.8)**. Effects "substantially larger than population overall" — confirms the low-SES targeting worked. Presumptive & retroactive eligibility mean eligible ≈ effectively covered ("conditional coverage," Cutler-Gruber 1996).
2. **FALSIFICATIONS**: Not on these pages (elderly/higher-income placebos come later).
3. **EVENT STUDIES**: Figure I shows the dynamic first-stage; DD summary defined. Event-study coefficients from Eq. 1.
4. **MAIN RESULTS**: Mortality reduced-form not yet — this section is the first stage.
5. **MECHANISM**: Cumulative-coverage measure motivated by long-term health effects of coverage beyond the enrollment period.

### DATA DETAILS
- First-stage eligibility & insurance use **repeated cross-sections of ACS 2008-2017** (55-64 in 2014), since panel only observes characteristics in ACS-interview year.
- Enrollment uses **CMS longitudinal administrative Medicaid** data (three DVs: enrolled indicator, days/year, cumulative days/365).
- Coverage robustness: **NHIS** (best national coverage estimates, state-specific Medicaid/CHIP names, uninsured verification) and **HRS** panel (cumulative coverage) — restricted versions with state IDs, same sample criteria.
