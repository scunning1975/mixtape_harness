# Dias & Fontes (2024), "Effects of a Large-Scale Mental Health Reform: Evidence from Brazil" — pp. 281-284 (Table 5, homicide mechanism, robustness begins)

These pages deliver the paper's headline mortality result — CAPS (community mental-health centers) raise homicide rates — and then build the Penrose/deinstitutionalization mechanism through a back-of-the-envelope dose-response calculation. Section V (Robustness) begins: unobserved policy changes (PBF, PSF) and alternative specifications.

## BITE / FIRST STAGE
The explicit first-stage magnitude used to interpret homicides appears here:
- **Average effect of CAPS on psychiatric (mental-health) hospital admissions = -0.95** (per 10,000). This is the untreated-margin / deinstitutionalization bite — CAPS pull patients OFF inpatient care.
- Ratio interpretation: dividing the homicide effect (0.149) by the hospitalization effect (-0.95) implies **15.7% of deinstitutionalized patients become involved in a violent death**.
- Substitution is concentrated on **long-stay admissions and schizophrenia patients** (the crime-prone margin), stated as the reason the incapacitation loss matters.
- Full first-stage supply/coverage numbers (facilities, visits per 100k) are in earlier chunks; here the operative bite is the -0.95 hospitalization decline.

## MAIN RESULTS / MECHANISM
**Table 5 — Effects of CAPS on Mortality (deaths per 10,000), (1) 2-yr, (2) 5-yr, (3) placebo, (4) baseline mean:**
- Deaths of despair: -0.006 (0.034) / -0.022 (0.032) / placebo -0.007 (0.010); base 2.038
- Suicide: 0.020 (0.018) / 0.002 (0.017) / -0.008 (0.005); base 0.512
- Overdose: 0.002 (0.003) / 0.001 (0.003) / -0.001 (0.001); base 0.015
- Alcohol-related: -0.024 (0.029) / -0.018 (0.027) / -0.001 (0.012); base 1.349
- **Homicides: 0.082 (0.041) / 0.149 (0.044) / placebo 0.016 (0.012); base 1.940**
- Infant mortality: 0.183 (6.341) / -0.001 (2.445) / -0.013 (0.79); base 173.782
- All-cause mortality: -0.040 (0.174) / 0.042 (0.170) / 0.035 (0.063); base 47.104

**Headline: 5-yr homicide effect = 0.149 (s.e. 0.044) deaths per 10,000, = 7.7% of baseline (1.94).** Figure 8 event study: flat, insignificant pre-trends; effect rises monotonically post-treatment (yr 1 ~0.10 to yr 5 ~0.23). Avg placebo 0.016 (0.012); joint significance of placebos p=0.45. Suicide/deaths-of-despair are NULL — the effect is specifically violent homicide, not self-harm.

**Mechanism = Penrose hypothesis / lost incapacitation.** Psychiatric hospitals incapacitate the crime-prone severely mentally ill (esp. schizophrenia); replacing them with under-equipped CAPS releases these patients into the community. Dose-response BOTE: r = (0.18x1)/(0.05x15) = 0.24; x40% benchmark => 9.6% of discharged patients become involved in homicides. Point estimate (15.7%) is within the plausible 8%-28% one-s.e. range. Authors remain cautious given noise. Rule out (weakly) alt channels (neighborhood fear, victim availability).

## DATA DETAILS
Homicides = ICD-10 X85-Y09; suicide X60-X84; overdose X40-X45,Y10-Y15,Y45,Y47,Y49; alcohol K70,K73-K74 + F00-F99. Municipality-level clustered bootstrap s.e. Controls: GDP p.c., PBF spending p.c., age-by-gender pop bins, state×year FE, linear pretrends (Theil, poverty, unemployment, illiteracy, rural share, log pop, log social spending, # MH providers, # MH offices, area, altitude, distance-to-capital, temp, rainfall). Robustness: PSF (Family Health Program) coverage ~80% at reform start; raw timing correlation 0.06 (pop-weighted -0.03) — online App Fig A8, Table A6; infant + all-cause mortality as placebos (App Fig A9). Alt specs in App Table A7 (no controls, pop-weighted, >=5yr exposure, 8yr horizon).
