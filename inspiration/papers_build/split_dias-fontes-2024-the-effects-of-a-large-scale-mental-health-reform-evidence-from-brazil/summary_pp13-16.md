# Dias & Fontes (2024), AEJ:Policy 16(3) — Reading notes, pp. 13–16 (journal pp. 269–272)

These pages present the paper's **first-stage / supply-side results**: how CAPS (community mental-health centers) changed the supply of mental-health practitioners and the volume of outpatient care. This is the treatment-intensity core the reader wants to place in front of a log-homicide outcome. Estimator is a staggered dynamic DiD with placebo (pre-treatment) DiD, event-study leads/lags −5..+5, municipality-clustered bootstrap SEs.

### BITE / FIRST STAGE

**Supply of MH practitioners (per 10,000 people) — Table 1 & Figure 3.** Columns: 2-yr / 5-yr / placebo / baseline mean.
- **Total MH practitioners:** 2-yr **0.787 (0.051)**, 5-yr **0.834 (0.053)**, placebo 0.159 (0.014), baseline 1.82. (~+46–53%.)
- **Psychiatrists:** 2-yr **0.164 (0.014)**, 5-yr **0.151 (0.015)**, placebo 0.029 (0.004), baseline 0.316.
- **Psychologists:** 2-yr **0.295 (0.030)**, 5-yr **0.342 (0.030)** (53%, rises to 0.43 by yr 5), placebo 0.066 (0.007), baseline 0.819.
- **Occupational therapists:** 2-yr **0.095 (0.011)**, 5-yr **0.104 (0.011)** (+60%), placebo 0.022 (0.003), baseline 0.173.
- **Social workers:** 2-yr **0.234 (0.021)**, 5-yr **0.238 (0.022)** (+50%), placebo 0.043 (0.006), baseline 0.512.
- Placebo-effect subset in Fig 3: total avg treat effect 0.835 (0.053) vs placebo 0.159 (0.014); joint significance of placebo effects = 0 (clean pre-trends). Note: a jump appears at t=−1 (municipalities hire before opening due to lengthy bureaucratic hiring).

**Other practitioners (no effect — placebo/spillover checks):**
- Family doctors: 2-yr 0.030 (0.037), 5-yr 0.044 (0.036).
- General practitioners: 2-yr 0.003 (0.068), 5-yr 0.057 (0.071).
- Overall supply of physicians: 2-yr 0.152 (0.087), 5-yr 0.286 (0.096).

**Outpatient procedures (per 10,000/yr) — first equilibrium bite, Figure 4:** Any MH specialist avg treatment effect **264.214 (27.05)** (+113% of baseline 233.68); psychiatrists 98.209 (10.267); psychologists 89.454 (8.66); occ. therapists 33.068 (6.516); social workers 43.484 (5.278). First-year effects: psychiatrists 132 (13.7), psychologists 83 (9.6), OT 18 (4.4), SW 34 (4.6).

**Untreated margin (psychiatric beds):** online App. Fig A7 — no pre-trends, no significant effect; only imprecise slight decrease after yr 3. So CAPS is a *de facto expansion*, not mere substitution; bed reductions are a downstream consequence, not part of treatment.

### MAIN RESULTS
No reduced-form mortality/homicide results yet on these pages — this is the supply/first-stage block. Reduced-form outcomes (hospitalizations, spending, deaths, homicides) begin pp. 17+.

### DiD DESIGN
Staggered adoption; dynamic DiD with heterogeneity-robust weighting (weighted avg of dynamic estimators, weight ∝ number of switchers — de Chaisemartin–D'Haultfœuille style). Placebo DiD with varying baseline period tests pre-trends; joint significance of placebo effects reported (=0 for supply outcomes). Event window −5 to +5.

### DATA DETAILS
Municipality-year panel; controls = GDP p.c., PBF (Bolsa Família) spending p.c., age×gender population bins, state×year FE, linear trends in pretreatment characteristics (Theil, poverty, unemployment, illiteracy, rural share, log pop, log social spending, # MH providers/offices, area, altitude, distance to capital, temperature, rainfall). Supply data = public-system practitioners (CNES-type). Outpatient procedures from SUS/DATASUS ambulatory data. Baseline = first pre-CAPS period mean.
