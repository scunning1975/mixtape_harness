# Dias & Fontes (2024), AEJ:Policy 16(3) — Reading notes, pp. 21–24 (journal pp. 277–280)

These pages give the reduced-form well-being outcomes: **deaths of despair** (suicide, overdose, alcohol-related) and the start of the **homicides** analysis. Bottom line so far: despite a large first stage in care delivery, CAPS has **no detectable effect on mortality** (deaths of despair), and the homicide analysis is introduced (results/figure on pp. 25+). Same staggered dynamic + placebo DiD, −5..+5, municipality-clustered bootstrap.

### BITE / FIRST STAGE
Recap tables carried onto these pages:
- **Table 3** (inpatient admissions per 10,000, repeated): Overall MH −0.839 (0.249) / −0.951 (0.272); Long-stay −0.464 (0.151) / −0.621 (0.155); Schizophrenia −0.602 (0.113) / −0.823 (0.122); substance abuse −0.039 (0.179) / 0.048 (0.183); mood −0.108 (0.091) / −0.077 (0.092); anxiety −0.006 (0.011) / −0.003 (0.011).
- **Table 4** (log spending): log MH hospital spending −0.138 (0.038) / −0.157 (0.032) / placebo −0.003 (0.010) / baseline 8.95; log overall hospital spending −0.004 (0.006) / 0.003 (0.007); log municipal health spending 0.117 (0.092) / 0.048 (0.082).

So the bite for a log-homicide outcome: ~+0.83 MH practitioners per 10k (5-yr, s.e. 0.053), +264 outpatient procedures per 10k (s.e. 27), −0.95 MH admissions per 10k (s.e. 0.27, −7.5%), −0.62 long-stay (s.e. 0.155), −0.82 schizophrenia admissions (s.e. 0.122), −15.7% federal MH hospital spending (s.e. 0.032).

### MAIN RESULTS

**Deaths of despair (mortality per 10,000) — Table 5 & Figure 7 (avg treatment effect (s.e.); baseline):**
- **Deaths of despair (composite): −0.022 (0.032)**; placebo −0.007 (0.010); baseline 2.04. Null; MDE ≈ 0.066 (≈3.2% of baseline).
- **Suicide (X60–X84): 0.002 (0.017)**; placebo −0.008 (0.005); baseline 0.51. Null.
- **Overdose (X40–X45, Y10–Y15, Y45, Y47, Y49): 0.001 (0.003)**; placebo −0.001 (0.001); baseline 0.01. Null.
- **Alcohol-related (K70/K73–K74 + alcohol-linked F-codes): −0.018 (0.027)**; placebo −0.001 (0.009); baseline 1.35. Null; MDE ≈ 0.051 (≈3.8% of baseline).

Authors stress: not a power problem — MDEs are small (3–4% of baseline); effects converge to zero at an 8-yr horizon and cumulative 8-yr effects are also null; signs flip when adding baseline time-trend controls (fragile, consistent with true zero). Caveat: mortality is a coarse proxy; milder mental-health gains could exist.

**Homicides — Section E, Figure 8 & Table 5 (introduced here):** Text notes treated and control municipalities had "very similar" pre-CAPS homicide levels (parallel pre-trends) — the coefficient/figure lands on the next pages (pp. 25+). So on these pages the homicide *point estimate* is not yet stated; capture it from the next chunk. Design intent: log-homicide-type outcome against the large care first stage documented above.

### DiD DESIGN
Weighted average of dynamic estimators (weight ∝ switchers); placebo DiD for pre-trends (joint placebo tests for despair panels: 0.76 despair, 0.41 suicide, 0.01 overdose, 0.97 alcohol). Robustness noted: 8-year horizon, cumulative effects, sensitivity to baseline-trend controls.

### DATA DETAILS
Mortality from **SIM (Sistema de Informações sobre Mortalidade), DATASUS**, ICD-10 external-cause and mental-disorder codes; deaths per 10,000. Homicides also mortality-register based. Municipality-year panel; same control set + state×year FE; baseline = first pre-CAPS period mean.
