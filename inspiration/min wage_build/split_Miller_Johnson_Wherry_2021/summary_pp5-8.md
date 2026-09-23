# Miller, Johnson & Wherry (2021) — Summary, pp. 5-8

## What these pages argue
Continues Background (Sec. II) and covers Data & Outcomes (Sec. III) plus the start of Empirical Strategy (Sec. IV). Reviews prior mortality evidence, then details the three-way data linkage and the event-study/DD specification.

## Prior evidence reviewed
- **Oregon Health Insurance Experiment (OHIE)**: no significant effect on blood pressure, cholesterol, blood sugar; no detectable mortality effect over 16 months — point estimate 16% reduction but CI too wide (Finkelstein et al. 2012; Baicker et al. 2013).
- Aggregate ACA-expansion mortality studies reach conflicting conclusions: no effect (Black et al. 2019); 3.6% reduction ages 20-64 (Borgschulte & Vogler 2020); 1.2% ages 55-64 (Chen 2019); Yan et al. (2020) no all-cause effect but 2.7% drop in healthcare-amenable mortality; Khatana et al. (2019) 2.9% cardiovascular reduction ages 45-64; Swaminathan et al. (2018) 8.5% one-year mortality drop for ESRD dialysis patients.
- Goldin et al. (2021): IRS-letter experiment — one added month of coverage lowered two-year mortality ~0.18 pp (>10%) for uninsured 45-64.
- Three stated advantages of this paper: (1) individual characteristics identify the Medicaid-eligible; (2) administrative enrollment confirms large coverage change (survey Medicaid measures misreport); (3) much larger sample than OHIE.

## Data (Sec. III)
Three linked sources. Sample: ACS respondents in families ≤138% FPL **or** less than high-school degree; exclude non-citizens, SSI recipients, and the 4 early-expansion states + DC (DE, MA, NY, VT). Primary sample: ages 55-64 in 2014. **~566,000 respondents.**

## Figures/Tables on these pages
- **Appendix Table A1** referenced (descriptive stats by expansion status).
- **Equation (1)** — the event-study specification (bottom of p.8).

### DiD ELEMENTS
1. **BITE / FIRST STAGE**: Sec. IV defines Y in the first-stage as "eligibility or coverage in each year." Motivates why individual targeting matters: population coverage rose only ~1 pp (Black et al. 2019); administrative enrollment confirms a large change for their targeted sample. Numbers not yet reported here (come pp.9-12).
2. **FALSIFICATIONS**: Baseline balance in Appendix Table A1 shows expansion states slightly better-off — income 147% vs 140% FPL, less-than-HS 45.3% vs 46.8%, uninsurance 32.6% vs 37.3%; used to gauge comparability.
3. **EVENT STUDIES**: **Equation (1)** is the event study — Yisjt = Expansion_s × Σ β_y I(t−t*_s = y) + β_t + β_s + β_j + γI(j=t) + ε. Leads/lags y = −6..+3, omitted y = −1. State, survey-wave, calendar-year FE. Expect pre-period coefficients (y=−6..−2) ≈ 0.
4. **MAIN RESULTS**: Not on these pages (setup only).
5. **MECHANISM**: Cause-of-death only available via MDAC supplement (limitation noted — Numident has date, not cause).

### DATA DETAILS
- **ACS 2008-2013 restricted** (~50% larger than public-use). Sample = ≤138% FPL OR <HS degree; exclude non-citizens, SSI recipients, 4 early-expansion states + DC. Ages 55-64 in 2014. **~566,000 respondents** (Census rounding rules).
- **Census Numident**: SSA-derived date/county of birth, date of death for SSN holders; deaths through 2017. Total deaths track NCHS closely.
- Linkage via **Census PVS** → PIK (protected ID key). ~90% of ACS respondents PIKed (92% citizens); ~93% of Medicaid records PIKed.
- **CMS Medicaid enrollment** 2008-2016 (2017 imputed for cumulative measures).
- **MDAC**: 2008 ACS linked to NDI death certificates 2008-2015 (cause of death).
- Also uses **NHIS** and **HRS** (restricted, state IDs) for coverage robustness.
- Outcome: annual death indicator (1=died that year), person removed after death. Annual mortality ~1.4% overall; ~1.3% in expansion states pre-expansion.
