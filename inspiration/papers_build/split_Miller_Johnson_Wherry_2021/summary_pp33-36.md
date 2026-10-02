# Miller, Johnson & Wherry (2021), pp. 33-36 — Summary

## What these pages contain
Four exhibits — the paper's **visual first-stage, main result, robustness, and placebo battery**: Figure I (coverage event studies), Figure II (mortality event study), Figure III (alternative specifications), Figure IV (placebo tests).

## Figure I — Effect on Eligibility and Coverage (five panels)
Event-study plots (event time -6 to +3, ref = -1) for: (a) Medicaid **eligibility** (ACS) — flat pre, jumps to ~0.50 post; (b) **Any Medicaid enrollment** (CMS) — flat pre, ~0.12-0.13 post; (c) **# days Medicaid/year** (CMS) — jumps ~35-50; (d) **cumulative Medicaid years** (CMS) — rising 0.1→0.7; (e) **uninsured** (ACS) — flat pre, drops to ~-0.05 post. This is the graphical first stage: clean pre-trends, sharp break at expansion.
Source note: ACS 2008-2017, CMS 2008-2016; sample = citizens 55-64 in 2014, non-SSI, less than HS OR below 138% FPL.

## Figure II — Effect on Annual Mortality
Single event-study plot. Pre-period coefficients scatter around zero (no differential pre-trend); post-period (Years 0-3) all negative, drifting more negative to ~-0.002 by Year 3. Sample uses ACS 2008-2013 respondents. This is the graphical main result matching Table I col 6.

## Figure III — Alternative Specifications (robustness forest plot)
Twelve DiD estimates plotted against the baseline (dotted line ~-0.0013): Baseline; 2014 Expanders Only; Linear State Pre-Trends; Trends by County Char.; Control for Labor Demand; Economic Controls; Opioid Controls; Trade Controls; Demographic Controls; All Controls; Triple Diff Age 65+; Triple Diff 400% FPL+. All cluster tightly near the baseline and remain negative — the mortality effect is robust to confounders (opioids, trade shocks, labor demand) and to triple-difference designs.

## Figure IV — Placebo Tests (three rows x two columns)
- **Row 1 (Pre-ACA years):** coverage (a) and mortality (b) — no effect when the "treatment" is applied to pre-ACA years (falsification passes).
- **Row 2 (Age 65+ in 2014):** Medicare-eligible group unaffected by Medicaid expansion — coverage (c) flat, mortality (d) flat. Placebo passes.
- **Row 3 (Income 400% FPL+):** higher-income group — small coverage bump (e) but mortality (f) flat/near-zero. Confirms mortality effect is concentrated where the coverage bite is largest.

## Main numbers / results
Consistent with Table I: coverage +~0.13, uninsured -~0.05, mortality baseline ~-0.0013 (robust across ~12 specifications).

### DiD ELEMENTS
- **BITE (first stage) — Figure I, STRONG & VISUAL:** eligibility ~+0.50; Any Medicaid ~+0.12-0.13; uninsured ~-0.05; days ~+35-50/yr; cumulative years rising to ~0.7. Clean flat pre-trends in every panel.
- **FALSIFICATIONS — Figure IV (full battery):** pre-ACA placebo years; age 65+ Medicare group (no coverage bite → no mortality effect); 400% FPL+ group (little bite → no mortality effect). Figure III adds opioid/trade/labor-demand/economic controls and triple-difference checks.
- **EVENT STUDIES — Figures I & II:** dynamic leads/lags, ref period -1; pre-trends flat, effects emerge post-2014 and grow over Years 0-3.
- **MAIN RESULTS — Figure II & III:** mortality ~-0.0013, robust across specifications; effect grows to ~-0.002 by Year 3.
- **MECHANISM — Figure IV rows 2-3:** effect absent where coverage bite is absent (Medicare-age, high-income) — dose-response linking coverage gain to mortality decline, ruling out generic secular trends.

### DATA DETAILS
- **ACS 2008-2017** (eligibility, coverage, uninsured); **CMS administrative enrollment 2008-2016** (any enrollment, days, cumulative years); **mortality** linked to death records (ACS 2008-2013 cohort for Fig II).
- **Unit:** individual x event-year. **Sample:** U.S. citizens ages 55-64 in 2014, non-SSI, less than HS degree OR family income below 138% FPL.
- **Treatment:** state Medicaid-expansion status, event-time indexed to 2014 expansion.
- Medicaid eligibility determination detailed in Appendix Section 2; analysis in Section V.A; placebos in Section VI.D.
