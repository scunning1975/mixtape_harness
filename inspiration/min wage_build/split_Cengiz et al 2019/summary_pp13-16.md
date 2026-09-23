# Cengiz, Dube, Lindner & Zipperer (2019) — Summary pp. 13–16 (QJE pp. 1417–1420)

**What these pages argue.** Completes II.B (how the α_τk coefficients map to employment/wage/elasticity estimates) and details II.C (Data and Sample Construction).

**Key concepts/equations.**
- Change in below-minimum jobs (event date −1 to τ): Σ_{k=−4}^{−1} α_τk − Σ_{k=−4}^{−1} α_{−1k} (a DiD, netting the counterfactual). Analogous for jobs between MW and W̄. Baseline **W̄ = MW + 4**.
- **Excess jobs** Δa_τ and **missing jobs** Δb_τ each normalized by **EPOP_{−1}** (pretreatment employment-to-population ratio). Five-year averages Δa, Δb.
- **"EB-bunching"** (event-based bunching) estimator: Δe = Δa + Δb = % change in total employment.
- **Employment elasticity w.r.t. MW** = (Δa+Δb)/%ΔMW.
- **%Δ affected employment** = (Δa+Δb)/b̄_{−1} (divide by pretreatment share earning below new minimum).
- **%Δ affected wage** (Eq. 2) = (%Δwb − %Δe)/(1+%Δe); assumes exiting/entering workers have same wage change as retained. **This is the "bite."**
- **Own-wage (labor demand) elasticity** = %Δaffected emp / %Δaffected wage; SEs by **delta method**.
- Elasticities don't require binning — a simpler state×quarter regression (jobs or wage bill under $15/hr) gives similar estimates/SEs.
- Fn 6: own-wage elasticity is effectively **Wald-IV**; weak first stage biases toward OLS (Bound, Jaeger & Baker 1995).

**Figures/tables.** None on these pages (equations/text). References Online App. Tables A.1, A.2, A.3, A.5; Figure A.2.

### DATA DETAILS
- **Primary microdata**: **NBER Merged Outgoing Rotation Group (MORG) of the Current Population Survey**, individual-level, **1979–2016**. URL: **http://www.nber.org/morg/**.
- Used to build **quarterly, state-level hourly-wage distributions**. Hourly workers: reported hourly wage; others: usual weekly earnings ÷ usual weekly hours.
- **Imputed wages excluded** (measurement error); imputation defined per **Hirsch & Schumacher (2004)** — BLS allocation flags for 1979–1988 & Sept 1995–2016; missing/zero unedited but positive edited earnings for 1989–1993.
- **Jan 1994–Aug 1995 excluded** (no reliable imputation data). **Analysis sample: 1979q1–1993q4 and 1995q4–2016q4.**
- Wages deflated to **2016 dollars** via **CPI-U-RS**.
- **117 wage bins**, $0.25 wide, $0.00–$30.00: (0.00,1.25), [1.25,1.50), …, [29.75,30.00), [30,∞). All wages $0–$1 in one bin; above $30 in the $30 bin.
- Employment counts E_swt collapsed by state-quarter using **person-level ORG sampling weights**.
- **Denominator N_st**: state-level population **aged 16+** from CPS-MORG (census-based).
- Primary sample: all wage earners + entire state population; subgroups explored separately.
- **QCEW (Quarterly Census of Employment and Wages)** used to benchmark the CPS employment-to-population ratio (near-universe of quarterly employment, but no hourly wages). Improves precision, little effect on point estimates (Online App. F).
