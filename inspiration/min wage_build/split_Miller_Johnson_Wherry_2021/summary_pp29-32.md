# Miller, Johnson & Wherry (2021), pp. 29-32 — Summary

## What these pages contain
Two content types: (1) the **tail end of the References** (N–Z: National Center for Health Statistics through Zajacova & Dowd), and (2) the paper's **two headline results tables — Table I and Table II**. This is the numeric core of the paper's DiD findings.

## References tail (methods/validation the tables rely on)
- **Mortality data source:** NCHS (2019) Public-use Linked Mortality File; Nolte & McKee (2003) "mortality amenable to health care" — the definition behind the "health-care-amenable causes" column in Table II.
- **Pre-trend inference:** Rambachan & Roth (2019, honest parallel trends); Roth (2019, pre-test caution); Sun & Abraham (2020, dynamic event-study estimator with heterogeneous effects) — the modern DiD toolkit.
- **Death-certificate education validity:** Rostron et al. (2010); Sorlie & Johnson (1996) — matters because the sample is defined partly on education.
- **Self-rated-health validity:** Dowd & Zajacova; Zajacova & Dowd — supports SRH as a mechanism proxy.

## Table I — Impact of ACA Expansions on Coverage and Mortality (DiD + event study)
Columns: (1) Medicaid Eligibility, (2) Any Medicaid Coverage in Year, (3) Days of Medicaid in Year, (4) Cumulative Medicaid Years, (5) Uninsured, (6) Died in Year.

**DiD (Expansion x Post) row:**
- Medicaid **eligibility +0.498*** (0.026)** — ~50 pp of this population made newly eligible.
- **Any Medicaid coverage +0.128*** (0.020)** — ~12.8 pp coverage gain.
- **Days of Medicaid +42.99*** (8.89)** per year.
- **Cumulative Medicaid years +0.375*** (0.061)**.
- **Uninsured -0.044*** (0.010)** — 4.4 pp drop.
- **Died in year -0.00132** (0.00050)** — the headline mortality reduction (~0.13 pp per year).

Event-study rows (Years -6 to +3, Year -1 omitted): pre-period coefficients small and insignificant for all outcomes (parallel trends hold); post-period coverage jumps immediately and mortality effect grows (Year 3 died = -0.00208**).

Sample sizes: eligibility/uninsured N=714,673 person-years; coverage/days from CMS ~3.49M person-years, 566,000 individuals; mortality N=4,030,000 person-years.

## Table II — Cause of Death
Columns: (1) Internal causes, (2) Health-care-amenable causes, (3) External causes.
- **Internal causes -0.00235*** (0.00675)** — deaths from internal (disease) causes drive the effect.
- **Health-care-amenable -0.00099* (0.00050)** — consistent with the insurance mechanism.
- **External causes +0.00038* (0.00020)** — tiny, wrong-signed (accidents/injury not reduced), a useful specificity check.
N=683,000 person-years, 88,500 individuals (MDAC). DRB approval CBDRB-FY19-310.

### DiD ELEMENTS
- **BITE (first stage) — STRONG:** +0.128 (12.8 pp) Any Medicaid coverage; +0.498 eligibility; -0.044 (4.4 pp) uninsured; +42.99 Medicaid days/yr; +0.375 cumulative Medicaid years. All significant at 1%.
- **FALSIFICATIONS:** event-study pre-trends (Years -6..-2) are near-zero/insignificant for every outcome; external-cause deaths do not fall (specificity).
- **EVENT STUDIES:** full leads-and-lags in both tables; coverage rises sharply at Year 0, mortality effect strengthens to Year 3.
- **MAIN RESULTS:** DiD mortality = **-0.00132 (s.e. 0.00050), p<0.05**; Year-3 = -0.00208.
- **MECHANISM:** Table II — reduction concentrated in internal + health-care-amenable causes, not external causes, pointing to a health (not behavioral/injury) channel.

### DATA DETAILS
- Survey: **ACS 2008-2017**; admin coverage: **CMS enrollment 2008-2016**; mortality: NCHS linked deaths; cause-of-death from **MDAC** (Mortality Disparities in American Communities).
- **Unit:** individual x year (person-year).
- **Sample:** U.S. citizens ages 55-64 in 2014, not SSI recipients, with less than HS degree OR family income below 138% FPL.
- **Treatment:** state Medicaid expansion x post-2014 (Expansion x Post).
- **Restricted access:** Census RDC; sample sizes rounded per Census disclosure rules; DRB #CBDRB-FY19-310.
