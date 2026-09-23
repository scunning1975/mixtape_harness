# Dias & Fontes (2024), AEJ:Policy 16(3) — Reading notes, pp. 17–20 (journal pp. 273–276)

These pages complete the equilibrium first-stage story: CAPS sharply cut **mental-health hospitalizations** (deinstitutionalization / substitution toward outpatient care), concentrated in long-stay and schizophrenia admissions, and cut **federal spending on MH hospitalizations** — while leaving other hospitalizations and local spending unchanged. Same staggered dynamic + placebo DiD, event window −5..+5, municipality-clustered bootstrap SEs.

### BITE / FIRST STAGE

**Outpatient care — Table 2 (per 10,000; 2-yr / 5-yr / placebo / baseline):**
- Total outpatient by MH practitioners: **206.754 (24.357)** / **264.213 (27.050)** / 11.548 (4.05) / 233.683.
- Psychiatrists: 102.864 (12.801) / 98.209 (10.267) / 2.331 (1.275) / 64.644.
- Psychologists: 62.409 (8.647) / 89.454 (8.660) / 7.005 (1.767) / 110.192.
- Therapists: 14.089 (4.889) / 33.068 (6.516) / 0.845 (1.045) / 23.375.
- Social workers: 27.392 (5.283) / 43.484 (5.278) / 1.366 (0.828) / 35.473.
- Antipsychotic drugs: 3.672 (6.795) / 16.693 (12.396) / −0.112 (0.613) / 7.691 (noisy, insignificant; ~+48% to +217%).
- Occupational therapy: 0.579 (0.191) / 0.794 (0.204) / −0.001 (0.028) / 0.717 (+60%).

**Inpatient care — the "untreated margin" / deinstitutionalization. Table 3 & Figure 5 (admissions per 10,000; 2-yr / 5-yr / placebo / baseline):**
- **Overall MH admissions (ICD-10 F00–F99): −0.839 (0.249) / −0.951 (0.272)** / −0.076 (0.066) / 12.662. Avg effect −0.948, ~ **−7.5%** of baseline. Joint sig. of placebo = 0.76 (clean).
- **Long-stay (>30 days): −0.464 (0.151) / −0.621 (0.155)** / −0.074 (0.054) / 6.035. Long-stay = 65.5% of the effect (80% by year 5).
- **Schizophrenia (F20–F29): −0.602 (0.113) / −0.823 (0.122)** / −0.033 (0.033) / 5.359. The only diagnosis with a significant reduction; accounts for 86.6% of effect.
- Psychoactive substance abuse (F10–F19): −0.039 (0.179) / 0.048 (0.183) / baseline 4.280 — null.
- Mood disorders (F30–F39): −0.108 (0.091) / −0.077 (0.092) / baseline 1.632 — null.
- Anxiety/stress (F40–F48): −0.006 (0.011) / −0.003 (0.011) / baseline 0.111 — null.

Interpretation: CAPS shifts care from inpatient to outpatient; diverted patients are mainly severe schizophrenia cases no longer held long-term in hospitals.

**Public spending (bite on the fisc) — Table 4 & Figure 6 (logs; 2-yr / 5-yr / placebo / baseline):**
- log(MH hospital spending, federal): **−0.138 (0.038) / −0.157 (0.032)** / −0.003 (0.010) / 8.95. ≈ −15.7 pp average reduction.
- log(Overall hospital spending, federal): −0.004 (0.006) / 0.003 (0.007) / baseline 13.969 — null (no savings elsewhere).
- log(Municipality health spending): 0.117 (0.092) / 0.048 (0.082) / baseline 14.609 — null.

Net fiscal: policy cost 2002–2014 ≈ 950M BRL; 11,545 municipality-years with CAPS; est. hospital-spending saving ≈ 720M BRL ⇒ **net cost ≈ 230M BRL** (CAPS costs money on net).

### MAIN RESULTS
Still first-stage/mechanism outcomes here. Footnote 18: no effects on diabetes/heart-attack hospitalizations (comorbid conditions) or other-cause hospitalizations. Deaths-of-despair and homicides come next (pp. 21+).

### DiD DESIGN
Weighted average of dynamic estimators (weight ∝ switchers); placebo DiD with varying baseline confirms parallel pre-trends (joint placebo tests 0.44–0.97 for inpatient panels). Event window −5..+5.

### DATA DETAILS
Hospitalization admissions from SIH/SUS (DATASUS) by ICD-10 group; long-stay = >30 days. Spending: federal expenses on MH hospitalizations vs total hospitalizations; municipal health spending. Municipality-year panel; same control set (Theil, poverty, unemployment, illiteracy, rural, log pop, log social spending, # MH providers/offices, area, altitude, distance-to-capital, temperature, rainfall) + state×year FE.
