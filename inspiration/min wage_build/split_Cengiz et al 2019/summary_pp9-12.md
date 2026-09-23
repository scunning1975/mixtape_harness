# Cengiz, Dube, Lindner & Zipperer (2019) — Summary pp. 9–12 (QJE pp. 1413–1416)

**What these pages argue.** Formalizes the conceptual framework (II.A) and empirical implementation (II.B): the core regression, normalization, and identifying assumptions.

**Key concepts/equations.**
- **Missing jobs**: Δb = Emp¹[w < MW] − Emp⁰[w < MW]; reflects the "bite."
- **Bite** (fn 2): function of (i) share below new minimum, (ii) legal coverage, (iii) compliance.
- Not all missing jobs destroyed — some preserved at MW (spike) or pushed above (Flinn 2011). Ripple effects fade at W̄.
- **Net effect**: Δb + Δa = Emp¹[w < W̄] − Emp⁰[w < W̄]; a bunching estimator (Kleven 2016).
- **Upper-tail calibration**: MW-worker share ≈ 2%; elasticity of substitution ≈ 1.4 (Katz & Murphy 1992), output demand elasticity ≈ 1 (Aaronson & French 2007) → implied upper-tail elasticity ≈ **0.006** (Online App. Table B.1); positive, so ignoring it overstates job losses.

**Main regression (Eq. 1):** E_sjt/N_st = Σ_{τ=−3}^{4} Σ_{k=−4}^{17} α_τk·I^{τk}_sjt + μ_sj + ρ_jt + Ω_sjt + u_sjt.
- E_sjt = employment in $0.25 bin j, state s, quarter t; N_st = state-quarter population.
- I^{τk} = 1 if MW raised τ years from t, for bins k to k+1 dollars from new minimum. τ=0 = first year post; τ=−1 = year prior. k=0 = four $0.25 bins MW to MW+$0.99; k=−1 = below bin.
- μ_sj = state×bin, ρ_jt = period×bin (controls wage-inequality evolution), Ω_sjt = small/federal controls. SEs **clustered by state**.
- Fn 4: small/federal events via {BELOW,ABOVE}×{EARLY,PRE,POST} (within $4; EARLY −3≤τ≤−2, PRE τ=−1, POST 0≤τ≤4).

**Identifying assumption.** Parallel trends across the entire wage distribution. Checked via leading terms and event-by-event sharp-null test; upper-tail changes as added falsification.

**Figures/tables.** None (equation/text). References Online App. Tables A.4, A.6, B.1.

### DATA DETAILS
- **Unit of observation**: state × $0.25 wage bin × quarter; counts normalized by state-quarter population N_st.
- **Wage bins**: **$0.25**; regression spans k = −4 to +17 dollars from new minimum.
- **Event window**: **8-year** — 3 pre, 5 post.
- **Event selection**: 138 state-level events where state raised MW by **≥ $0.25** AND **≥ 2% of workers directly affected**.
- **Federal increases excluded** from primary sample (no control states); Online App. Table A.4 shows similar with federal included.
- **Very small increases excluded** but controlled for.
- Geographic level: **U.S. states**; time: **1979–2016**.
- Robustness to window length (up to 7-year post) in Online App. Table A.6.
- Framework similar to Autor, Donohue & Schwab (2006).
