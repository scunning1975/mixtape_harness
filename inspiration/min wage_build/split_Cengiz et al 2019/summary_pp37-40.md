# Cengiz, Dube, Lindner & Zipperer (2019), pp. 37–40 (journal pp. 1441–1444)

## What these pages argue
These pages complete the analysis of **wage spillovers** ("ripple effects") from minimum wage increases and open the section on **event-specific estimates**. The authors decompose the total wage gain of affected workers into a mechanical "direct" component (workers moved exactly to the new minimum) and a spillover component (raises granted above the new minimum). They then argue the spillovers reflect real firm behavior, not measurement error, and set up event-by-event estimation.

## Key concepts / equations
- **Equation (3):** the "no spillover" wage increase, %Δw_no spillover = [Σ_{k=−4}^{−1} k(α_k − α_{−1,k})] / (w·b_{−1}) — moves each missing job exactly to the new minimum.
- **Spillover size** = %Δw − %Δw_no spillover; the **spillover share** = (%Δw − %Δw_no spillover)/%Δw.
- Their spillover estimates use the **frequency distribution** of wages (not the density, as in Card-Krueger 1995, DiNardo-Fortin-Lemieux 1996, Lee 1999, Autor-Manning-Smith 2016), so employment changes don't create artificial spillovers.
- **Equation (4):** the event-specific stacked regression, Y_sjth = Σ_τ Σ_k α_{τkh} I^{τk}_{sjth} + μ_sjh + ρ_jth + Ω_sjth + u_sjth, where j indexes $1 wage bins relative to the minimum wage, run separately for each event h.

## Main results / numbers
- Total wage effect **6.8%** (s.e. 1.0%); no-spillover effect **4.1%** (s.e. 0.9%); **39.7%** (s.e. 11.9%) of the wage gain is due to spillovers.
- Spillover shares similar across groups: less than high school 37.0%, teens 34.7%, high school or less 40.2%, women 35.9%. Black/Hispanic much smaller at 17.9% (s.e. 26.5%).
- Tradeable sector spillover near zero/imprecise; nontradeable 23.7%.
- **Incumbents** get a 9.5% total wage rise, spillover share 42.2%; **new entrants** spillover share −17.8% (essentially all their gain is new jobs at the new minimum). This contrast argues against a common measurement-error explanation (contra Autor-Manning-Smith 2016) and against reservation-wage/outside-option stories (Flinn 2006); consistent with optimization frictions (Kleven 2016) and relative-pay norms (Dube-Giuliano-Leonard 2018).

## Figures / tables
- **Table IV — The Size of the Wage Spillovers:** columns %Δw, %Δw_no spillover, spillover share, by subgroup (overall, <HS, teen, HS-or-less, women, black/Hispanic, tradeable, nontradeable, incumbent, new entrant), s.e. clustered by state.

### DATA DETAILS
- Event study exploits **138 state-level minimum wage changes**, period **1979–2016** (Table IV notes).
- Event-specific analysis builds **138 data sets**, one per event h; each includes the treated state plus all "clean control" states (no nontrivial state minimum wage increases in the 8-year window) for an **8-year panel by event time**.
- Unit of observation: **per capita number of jobs in $1 wage bins relative to the minimum wage, by state-by-year**.
- Ω_sjth controls for other primary/federal/small events whose 5-year post-treatment periods fall inside data set h.
- Wage data are **CPS-based**; Online Appendix C validates spillovers with **Washington State administrative data**.
