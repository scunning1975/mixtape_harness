# Structured Extract — Cengiz, Dube, Lindner & Zipperer (2019)
### "The Effect of Minimum Wages on Low-Wage Jobs," *Quarterly Journal of Economics* 134(3): 1405–1454

Built from a 13-chunk deep read (4 pages/chunk). Per-chunk summaries live in
`min wage_build/split_Cengiz et al 2019/summary_pp*.md`; the dedicated first-stage
("bite") deep-dive is in that folder's `bite.md`.

---

## 1. Research question
Does raising the minimum wage destroy low-wage jobs? Reframed as a *distributional*
question: where in the wage distribution do jobs disappear (below the new floor) and
appear (at/above it), and does the net add up to job loss? Motivated by the 2014 CBO
report that extrapolated employment losses from teen elasticities.

## 2. Audience
Labor economists in the minimum-wage/employment debate; the applied-micro / DiD-design
community (the method travels); inequality researchers (wage-distribution tools); public
finance / bunching estimator users.

## 3. Method / identification
**Stacked event-study "bunching" design** over 138 state MW increases. For each event,
estimate the change in the number of jobs in each $0.25 wage bin relative to the new
minimum, netted against clean control states (no own MW change in the 8-year window),
3 years pre to 5 years post. Two objects:
- **Missing jobs (Δb):** the drop in jobs *below* the new minimum (negative).
- **Excess jobs (Δa):** the rise in jobs *at/above* the new minimum, up to $4 above.
- **Net employment: Δe = Δa + Δb** ("EB-bunching" estimate). Upper-tail bins ($5+ above)
  are a placebo/falsification check.
Identifying assumption: parallel trends across the *entire* wage distribution.

## 4. Data  (see the deep dive in §"Dataset" of REVIEW.md)
- **Primary microdata:** NBER Merged Outgoing Rotation Group (MORG) of the CPS,
  individual-level, 1979–2016. http://www.nber.org/morg/
- **Unit of observation:** state × $0.25 wage-bin × quarter, counts normalized by
  state-quarter population (age 16+, census-based, from CPS-MORG).
- **Sample size:** 847,314 wage-bin-state-quarter cells, from 4,694,104 individual obs.
- **Analysis span:** 1979q1–1993q4 and 1995q4–2016q4 (Jan-1994–Aug-1995 dropped: no
  reliable wage-imputation flags).
- **Policy events:** 138 state MW increases. Selection = state raised MW by ≥ $0.25 AND
  ≥ 2% of workers directly affected. Federal increases excluded (no control group);
  very small increases excluded but controlled for.
- **MW policy series:** Vaghul & Zipperer (2016), daily state/sub-state, quarterly max.
  https://github.com/benzipperer/historicalminwage/releases
- **Wage construction:** hourly workers → reported hourly wage; others → usual weekly
  earnings ÷ usual weekly hours. Imputed wages dropped (Hirsch–Schumacher 2004).
  Deflated to 2016$ via CPI-U-RS. 117 bins, $0.25 wide, $0–$30.
- **Benchmarking:** QCEW (near-universe of employment, no hourly wages) used to
  benchmark the CPS E/POP ratio → tighter precision, ~same point estimates.
- **Validation:** microaggregated administrative hourly-wage data from MN, OR, WA state
  employment agencies (restricted; Online Apps C/E).
- **Replication archive:** Harvard Dataverse, doi:10.7910/DVN/TJCTC7.

## 5. Statistical methods
Core event-study regression (Eq. 1): employment share per bin on event-time × bin-distance
dummies, with state×bin and period×bin fixed effects; SEs clustered by state. Elasticities
built as ratios (delta-method SEs). Own-wage elasticity is a **Wald-IV**: %Δaffected
employment ÷ %Δaffected wage (the bite is the first stage).

## 6. Findings (headline)
| Quantity | Value | s.e. |
|---|---|---|
| Missing jobs Δb | −1.8% | 0.4% |
| Excess jobs Δa | +2.1% | 0.3% |
| **Net %Δ affected employment** | **+2.8%** | **2.9%** |
| **%Δ affected wage (BITE)** | **+6.8%** | **1.0%** |
| Own-wage employment elasticity | 0.41 | 0.43 |
| Employment elasticity w.r.t. MW | 0.024 | 0.025 |
- 95% CI rules out own-wage elasticities below −0.45.
- ~40% of the wage gain is spillover (ripple) above the new floor; extends to ~$3 above
  (≈23rd pctile), no further. Incumbents capture the ripple; new entrants do not.
- No labor-labor substitution; near-zero net employment across demographic groups, across
  the Kaitz range 37–59%, and in the sectors where MW workers concentrate (restaurants,
  retail, nontradeable). Tradeable/manufacturing point estimates negative but imprecise.

## 7. Contributions
A design that jointly measures the wage effect (first stage) and the employment effect
(reduced form) of the MW *without* a parametric wage model, using the whole low-wage
distribution rather than a proxy group (teens). Diagnoses why two-way FE log-MW
regressions (Meer–West 2016) find disemployment: an implausible upper-tail drop driven by
pre-1992 confounding. The bunching-plus-stacking estimator is now widely borrowed.

## 8. Replication feasibility
**High.** CPS-MORG public (NBER), MW series public (GitHub), replication code+data on
Harvard Dataverse (doi:10.7910/DVN/TJCTC7). The only non-public inputs are the three-state
administrative validation files. A capable RA can rebuild the main figures from public data.
