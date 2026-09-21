# The "Bite" in Cengiz, Dube, Lindner & Zipperer (2019, QJE)

**Bite** = the first-stage effect of a minimum wage increase on the *wages* of affected workers — the percentage change in the average hourly wage of workers who earned below the new minimum before the increase (%Δ affected wage, `%Δw`). It is the empirical "how binding" of the policy and serves as the denominator (first stage) of the own-wage employment elasticity. Headline bite ≈ **6.8% (s.e. 1.0%)**, of which ~40% comes from spillovers/ripple effects above the new minimum.

---

## 1. DEFINITION & MEASUREMENT of the bite

### The building blocks (pp. 1417–1418)
The paper first estimates event-study coefficients `α_τk` (equation 1) for each $1 wage bin `k` relative to the new minimum wage. From these it constructs:

- **Excess jobs (Δa):** jobs at/above the new MW up to $4 above it, netted against the pretreatment counterfactual, normalized by pretreatment EPOP:
  `Δa = (Σ_{k=0}^{4} α_τk − Σ_{k=0}^{4} α_{-1k}) / EPOP_{-1}`
- **Missing jobs (Δb):** jobs below the new MW ($4 below to the MW), same DiD netting and normalization:
  `Δb = (Σ_{k=-4}^{-1} α_τk − Σ_{k=-4}^{-1} α_{-1k}) / EPOP_{-1}`  (Δb is negative)
- **Total employment change:** `Δe = Δa + Δb` (the "EB-bunching" / event-based bunching estimate).
- Baseline window: `W = MW + $4`. Both a and b averaged over the five post-treatment years.

### %Δ affected employment (p. 1418)
Divide the employment change by the pretreatment share of the workforce below the new MW, `b̄_{-1}`:
`%Δe = %Affected Employment = (Δa + Δb) / b̄_{-1}`
(Note: divided by the *actual* share below, not the change in it — the policy-relevant elasticity per footnote 9.)

### The average-wage-of-affected calculation (p. 1418)
Average wage of affected workers = (total wage bill of workers below new MW) / (number of such workers).
- Pretreatment: `w̄_{-1} = wb̄_{-1} / b̄_{-1}`, where `wb̄_{-1}` is the wage bill and `b̄_{-1}` the count below the new MW.
- Post-treatment new average wage: `w̄ = (wb̄_{-1} + Δwb) / (b̄_{-1} + Δe)`.
- Change in wage bill (footnote 10): `Δwb = Σ_{k=-3}^{4} (k + MW̄)·(α_k − α_{-1k})`, where `MW̄` is the sample-average new minimum wage (mean of [MW, MW+1)).

### Equation (2): the bite formula (p. 1419)
```
%Δw = w̄/w̄_{-1} − 1 = (wb̄_{-1} + Δwb)/(b̄_{-1} + Δe) ÷ (wb̄_{-1}/b̄_{-1}) − 1
     = (%Δwb − %Δe) / (1 + %Δe)
```
In words: **the percentage change in the average wage of affected workers equals the difference between the %Δ wage bill and %Δ employment, divided by the retained-employment share (1 + %Δe).**

**Key identifying assumption (stated explicitly, p. 1419):** the formula *implicitly assumes the average wage change of workers who exit or enter due to the policy is the same as the average wage change of affected workers who remain employed.* The `(1 + %Δe)` term is the retained-employment adjustment.

### The bite as the FIRST STAGE of the own-wage elasticity (pp. 1417 fn.6, 1419)
The own-wage (labor-demand) elasticity is a Wald/IV ratio:
```
%Δ Affected Employment / %Δ Affected Wage = (1/%Δw)·((Δa + Δb)/b̄_{-1})
```
Standard errors via the delta method. Footnote 6 (p. 1417) makes the IV logic explicit: this is *effectively a Wald-IV estimate; a weak "first stage" (small wage effect) biases the elasticity toward the OLS estimate of naively regressing employment on wages* (Bound, Jaeger & Baker 1995). Focusing on low-wage jobs guarantees a strong, precise first stage (large, significant wage effect) — the standard whole-distribution approach often fails to produce a significant wage effect, so its first stage is weak.

### Direct bite vs. spillovers (Eq. 3, p. 1441)
- **Direct / mechanical ("no spillover") bite** — move every missing job below the new MW exactly *to* the new minimum:
  `%Δw_noSpillover = Σ_{k=-4}^{-1} k(α_k − α_{-1k}) / wb̄_{-1}`  (equation 3)
- **Spillover / ripple effect** = `%Δw − %Δw_noSpillover`; spillover *share* = `(%Δw − %Δw_noSpillover)/%Δw`.
- The bite uses the **frequency distribution** of wages (not the density), so employment changes don't create artificial spillovers.

### How far up the spillovers extend (pp. 1423–1424, fn.19)
- Statistically significant excess employment appears at the $0 bin (the spike) and at **$3 above** the new MW; $1 and $2 bins positive but insignificant.
- **$3 above the MW ≈ 23rd percentile** of the wage distribution; Autor-Manning-Smith (2016) find spillovers effectively zero by ~25th percentile.
- Employment changes from $5 above the MW up to $17+ are all small and insignificant, individually and cumulatively → "limited wage spillovers."

---

## 2. HEADLINE MAGNITUDES

### The bite and its decomposition (Figure II p. 1423; Table I col 1; pp. 1425, 1441)
| Quantity | Value | s.e. |
|---|---|---|
| Δa (excess jobs) | +0.021 (2.1%) | 0.003 |
| Δb (missing jobs) | −0.018 (−1.8%) | 0.004 |
| **%Δ affected wage (bite)** | **0.068 (6.8%)** | **0.010** |
| %Δ affected employment | 0.028 (2.8%) | 0.029 |
| Employment elasticity w.r.t. MW | 0.024 | 0.025 |
| Emp. elasticity w.r.t. affected wage | 0.411 | 0.430 |
| b̄_{-1} (jobs below new MW) | 0.086 (8.6%) | — |
| %Δ MW (mean real MW increase) | 0.101 (10.1%) | — |

- The own-wage elasticity 95% CI rules out anything more negative than **−0.450**.
- Sample: 138 events, 847,314 wage-bin-state-quarter cells, 4,694,104 individual CPS-MORG observations, 1979–2016.

### Spillover vs. mechanical split (Table IV, "Overall" row; p. 1441)
- Total bite `%Δw` = **6.8%** (s.e. 1.0%)
- Direct/no-spillover `%Δw_noSpillover` = **4.1%** (s.e. 0.9%)
- **Spillover share = 39.7%** (s.e. 11.9%) → ~40% of the wage gain is the ripple effect above the new minimum; ~60% is mechanical.

### The b̄ vs. Δb distinction (fn.18, p. 1424)
- Pretreatment share actually below the new MW: **b̄_{-1} = 8.6%** of total employment.
- Change in jobs below (missing jobs): **Δb = 1.8%** on average — much smaller than 8.6% because (i) tipped/exempt workers, (ii) multiple MW changes in short windows (adjusting for this raises the change from 1.8% to **2.5%**), and (iii) ambient wage growth the design controls for.
- Mean real MW increase: **%ΔMW = 10.1%**.

### Aggregate context (p. 1425)
- Employment elasticity w.r.t. MW = 0.024 (s.e. 0.025); CI rules out Meer-West (2016) −0.074.
- Teen affected share (43.2%) vs. overall (8.6%): scaling ratio 0.432/0.086 = 5.02 gives an affected-share-adjusted employment-elasticity CI of [−0.13, 0.37], ruling out most of the −0.1 to −0.3 teen range.

---

## 3. HETEROGENEITY IN THE BITE

### By demographic group — Table II (p. 1432)
Columns 1–8. Bite (%Δ affected wages) with s.e., and b̄_{-1} (pretreatment affected share):

| Group (col) | b̄_{-1} | Δb (missing) | Δa (excess) | **%Δ affected wage** | own-wage elast. |
|---|---|---|---|---|---|
| No HS degree (1) | 0.264 | −0.065 | 0.075 | **0.080 (0.014)** | 0.475* (0.268) |
| HS or less (2) | 0.145 | −0.032 | 0.038 | **0.076 (0.014)** | 0.570 (0.386) |
| Teens (3) | 0.432 | −0.114 | 0.127 | **0.083 (0.018)** | 0.356 (0.317) |
| Women (4) | 0.102 | −0.023 | 0.026 | **0.072 (0.011)** | 0.343 (0.362) |
| Black or Hispanic (5) | 0.133 | −0.028 | 0.028 | **0.044 (0.012)** | −0.086 (1.005) |
| (col 6) | 0.358 | −0.094 | 0.100 | **0.073 (0.011)** | 0.206 (0.233) |
| (col 7) | 0.104 | −0.020 | 0.021 | **0.051 (0.013)** | 0.304 (0.904) |
| (col 8) | 0.027 | −0.004 | 0.004 | **0.060 (0.032)** | 0.184 (0.841) |

(%ΔMW ≈ 0.100–0.103 across groups.)
- Restricting by education/age produces a **larger bite** (more missing jobs). Δb for no-HS = −6.5% (261% larger than baseline −1.8%); HS-or-less = −3.2% (78% larger).
- Crucially, larger missing jobs are **matched closely by larger excess jobs** → employment effects stay near zero for every group except a marginally-significant positive for no-HS (own-wage elast. 0.475*, sig. at 10%). Teen MW-elasticity = 0.125.

### By sector — tradeable vs. nontradeable (Table IV, p. 1442)
(Table III's restaurant/retail/manufacturing wage numbers are not in the provided page splits; the sectoral bite that IS present:)
- **Tradeable:** bite `%Δw` = 0.058 (s.e. 0.073, insignificant); no-spillover = 0.065** (0.028); spillover share = −0.114 (1.157) → essentially no spillovers, wage effects small in tradeable sector.
- **Nontradeable:** bite = 0.056*** (0.014); no-spillover = 0.043*** (0.006); spillover share = 0.237 (0.191).
- Interpretation: wage effects (and thus spillovers) are muted in the tradeable sector; combined with disemployment risk, suggests more unintended consequences where the tradeable sector is a larger share of affected workers.

### Across events by Kaitz index (min/median) — Figure V (pp. 1445–1446)
Binned scatter of event-specific estimates on the Kaitz index (new MW / median wage), 130 events (8 DC events excluded as too noisy). Slopes (robust s.e.) from weighted linear fits, controlling for decade, state unemployment rate, urban share, Republican-leaning indicator:

| Outcome | Slope on Kaitz | s.e. |
|---|---|---|
| **Missing jobs (Δb)** | **−0.133** | 0.034 (sig.) |
| **Excess jobs (Δa)** | **+0.139** | 0.057 (sig.) |
| **Net employment (Δe)** | **+0.006** | 0.048 (flat, insig.) |

- **Central claim:** a higher Kaitz index = bigger bite ⇒ *both* more missing jobs below AND a nearly equal-sized increase in excess jobs at/above the new MW; the two roughly cancel, so **net employment is virtually unchanged** across the range studied.
- Kaitz range covered: **37% to 59% of the median wage**.
- Conclusion: U.S. minimum wages studied "have yet to reach a point where the employment effects become sizable."
- (Robustness fn.31: only 5.3% of event-specific employment estimates significant at 5%; consistent with sharp null of zero employment effect everywhere despite large bite heterogeneity.)

### Incumbents vs. new entrants — Figure IV / Table IV (pp. 1442–1443)
- **Incumbents** (employed one year before): bite **9.5%** (0.020) — *larger than the 6.8% overall*; no-spillover 5.5% (0.011); **spillover share 42.2%** (0.181)** ≈ the overall 39.7%.
- **New entrants** (not employed one year before): bite **1.9%** (0.013, insignificant); no-spillover 2.3%*** (0.006); **spillover share −17.8%** (0.748) → essentially *all* of entrants' wage gain comes from the creation of jobs *at or very close to* the new minimum, with no upward ripple.
- Implication: incumbents capture the spillover/ripple wage gains; the stark incumbent–entrant difference argues the spillovers are **real** (not common CPS measurement error) and reflect firm "optimization frictions" / relative-pay norms (Kleven 2016; Dube-Giuliano-Leonard 2018), not rising reservation wages of the nonemployed.

---

## 4. SPILLOVER SPECIFICS — Table IV (p. 1442)

Columns: `%Δw` (total bite) | `%Δw_noSpillover` (direct) | spillover share `(%Δw − %Δw_noSpillover)/%Δw`. s.e. in parentheses; ***/**/* = 1/5/10%.

| Group | %Δw (total) | %Δw no-spillover | Spillover share |
|---|---|---|---|
| **Overall** | 0.068*** (0.010) | 0.041*** (0.009) | **0.397*** (0.119)** |
| Less than high school | 0.077*** (0.013) | 0.048*** (0.009) | 0.370*** (0.078) |
| Teen | 0.081*** (0.015) | 0.053*** (0.007) | 0.347*** (0.059) |
| High school or less | 0.073*** (0.013) | 0.043*** (0.011) | 0.402*** (0.100) |
| Women | 0.070*** (0.011) | 0.045*** (0.010) | 0.359*** (0.120) |
| Black or Hispanic | 0.045*** (0.012) | 0.037*** (0.010) | 0.179 (0.265) |
| Tradeable | 0.058 (0.073) | 0.065** (0.028) | −0.114 (1.157) |
| Nontradeable | 0.056*** (0.014) | 0.043*** (0.006) | 0.237 (0.191) |
| Incumbent | 0.095*** (0.020) | 0.055*** (0.011) | 0.422** (0.181) |
| New entrant | 0.019 (0.013) | 0.023*** (0.006) | −0.178 (0.748) |

**Total wage effect at each dollar bin (Figure II, p. 1423):** the spillover is concentrated just above the MW — significant excess at the $0 spike and at **$3 above**; $1 and $2 bins positive but insignificant; $5-above through $17+ all null (individually and cumulatively). So the ripple extends to roughly $3–$4 above the new minimum (≈23rd percentile) and no further.

**Statistical significance summary:**
- Spillover share significantly > 0 at 5% for: overall, less-than-HS, teen, HS-or-less, women, incumbent.
- Not significant: black/Hispanic (17.9%, much smaller — wage gains more muted for this disadvantaged group), tradeable and nontradeable sectors, and new entrants (negative point estimate).

**Note on Table III:** the sector-specific bite for restaurants, retail, and manufacturing (Table III) does not appear in the page splits provided (pp. 25–28 cover Table II and the start of Section III.A; Table III itself was not among the supplied pages). Sectoral bite evidence available here is the tradeable/nontradeable split from Table IV above.
