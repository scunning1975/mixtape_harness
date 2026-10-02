# Dias & Fontes (2024), Mental Health Reform / Brazil — pp. 9-12

## What these pages argue
Finishes the data section, fully specifies the estimation strategy, presents identification checks, and delivers the FIRST set of main results (mental-health care supply). Confirms the balanced panel and the de Chaisemartin-D'Haultfoeuille aggregation of 2x2 DIDs. Runs two credibility checks: (1) a HAZARD model of the probability a municipality gains a CAPS on baseline characteristics — correlations exist but are tiny (a 1 SD change moves probability <2 pp; crucially, NO correlation with pretreatment dynamics of mental health, crime, economic indicators); (2) placebo/pre-trend estimator (short comparisons) — placebo effects generally indistinguishable from zero. Then Section IV.A shows CAPS caused a large, immediate jump in mental-health professional density = the first stage.

### BITE / FIRST STAGE
THE explicit first-stage numbers are here (Figure 3 + Table 1), all in professionals per 10,000 people, ATT vs. year-before-event baseline:
- **Total MH professionals:** ATT = **+0.835 (s.e. 0.053)**, = **+46%** over baseline of 1.82. Placebo 0.159. Jumps immediately, peaks after policy.
- **Psychiatrists:** avg ATT +0.151 (s.e. 0.015); baseline 0.32; +0.18 (60%) one year post, decaying to 0.13 (s.e. 0.02) by year 5. Placebo 0.029.
- **Psychologists:** ATT +0.342 (0.03); baseline 0.82; text notes +0.22 (27%). Placebo 0.066.
- **Occupational therapists:** ATT +0.104 (0.011); baseline 0.17. Placebo 0.022.
- **Social workers:** ATT +0.238 (0.022); baseline 0.51. Placebo 0.043.
- All "joint significance of placebo effects = 0" (i.e., pre-trends flat).
- Some ANTICIPATION: increases begin the year BEFORE CAPS opens (relevant if using event-time k for a bite instrument).
- General practitioners/family doctors: positive but imprecise, smaller than psychiatrists; overall physician supply rises, driven by psychiatrists (no cross-specialty substitution).
- This IS the paper's explicit first stage: professional density and (per intro) outpatient visits and drug dispensing all jump when CAPS opens. Hospitalization DECLINE (substitution/untreated margin) comes in later chunks (Section IV, not fully in pp9-12).

### DiD DESIGN
- Staggered CAPS rollout; treatment = first CAPS in municipality; unit = municipality.
- Estimator: de Chaisemartin & D'Haultfoeuille (2020); noted equivalent to Sun-Abraham (2021) and Callaway-Sant'Anna (2021) in the no-covariate case. TWFE rejected (Goodman-Bacon 2021).
- Inference: municipality-level clustered bootstrap SEs.
- Identification: state-specific nonparametric trends; interactions of baseline covariates x linear trend (Theil index, poverty, illiteracy, rural share, population, social spending, MH providers/offices, area, altitude, distance to capital, temperature, rainfall); controls for GDP p.c., age-by-gender composition, per-capita Bolsa Familia (PBF). Placebo estimator = short comparisons (t'-1 to t'), pseudo-ATTs.
- Outcomes (five sets tied to Figure 2): MH care supply, market equilibrium (in/outpatient), spending, mortality, violent crime.

### DATA DETAILS
- **Balanced yearly panel: 5,180 municipalities, 2002-2016** (summary stats Appendix Table A2).
- **SIM** mortality (DATASUS 1979-2024c): deaths by ICD-10 cause — alcohol, overdose, suicide, "deaths of despair" (sum of the three, Case-Deaton), plus HOMICIDES (proxy for violent crime, Dix-Carneiro-Soares-Ulyssea 2018); overall & infant mortality as placebos (live births DATASUS 1979-2024b).
- Covariate sources: IBGE municipal GDP (2002-2016), MDS/SAGI Bolsa Familia, DATASUS age/gender, IPEA geography, IBGE AMS 2002 (baseline MH providers/offices), 2000 Census.

## Figures/Tables on these pages
- **Figure 3** (Panels A-E): Effects of CAPS on MH practitioners per 10,000 — Total, Psychiatrists, Psychologists, Occupational therapists, Social workers (event-study, k = -5..+5, with placebos & 95% CIs). This is the first-stage figure.
- **Table 1**: Effects on MH practitioner supply (referenced; the numeric first stage).
- Referenced: Appendix Tables A2 (summary stats), A3 (ICD groupings), A4 (hazard model), Figure A4 (GPs/family doctors).
