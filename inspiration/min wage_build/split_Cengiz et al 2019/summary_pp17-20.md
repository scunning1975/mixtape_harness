# Cengiz, Dube, Lindner & Zipperer (2019) — Summary pp. 17–20 (QJE pp. 1421–1424)

**What these pages argue.** Finishes II.C (event specification, sample sizes, measurement-error robustness) and opens Section III (Results) with the headline wage-distribution figure.

**Key concepts/results.**
- **Event definition**: state-level MW = quarterly maximum of the daily minimum-wage series of **Vaghul & Zipperer (2016)**. Across the 138 events, on average **8.6% of workers** were below the new minimum the prior year, and the **mean real MW increase was 10.1%**.
- **Sparse-bin concern addressed**: employment estimate sums **36 cells** over a **$9 range [MW−$4, MW+$4]** × ≥4 (typically 20) quarters. ~7 workers/quarter per $0.25 bin in $5–$15 range; ~112 individual obs per $1-bin-year-state coefficient; **~5,040 individual obs per event**.
- **Measurement-error robustness**: classical/nonclassical misreporting attenuates Δb but is offset by an equal reduction in Δa, so **Δa+Δb is unaffected** (as long as error support ⊂ [MW−W̄, W̄−MW]). Validated against microaggregated administrative hourly-wage data from three states (Online App. E); structural measurement-error model of Autor-Manning-Smith (2016) and deconvolution give similar estimates (Online App. F, Table F.3); Washington admin-data replication similar (Online App. C).

**Main results (Figure II).**
- **Δa = 0.021 (0.003)**; **Δb = −0.018 (0.004)**; **%Δ affected employment = 0.028 (0.029)**; **%Δ affected wage = 0.068 (0.010)** — the bite.
- Clear significant drop below new minimum = **1.8% (s.e. 0.4%)** of pretreatment employment; ~¾ in the $1 bin just under MW.
- Significant spike at MW ($0 bin); significant rise at $3-above bin; modest insignificant $1/$2 bins → limited spillovers (Autor-Manning-Smith 2016; $3 above ≈ 23rd pct).
- **Excess jobs (MW to +$4) = 2.1% (s.e. 0.3%)**.
- Upper-tail bins ($5-above to $17+) small and insignificant individually and cumulatively (red running-sum line).
- Adjusting for multiple MW changes raises the below-minimum drop from **1.8% to 2.5%**; tipped-worker exemptions and background wage growth explain the gap vs. the 8.6% level.

**Figures/tables.**
- **Figure II** (p. 1423): "Impact of Minimum Wages on the Wage Distribution." Bars = difference between actual and counterfactual employment count relative to pretreatment total, by $ wage bin from −4 to 17+; error bars = 95% CI (state-clustered); red dashed line = running sum. Inset reports Δa, Δb, %Δ affected employment, %Δ affected wage.

### DATA DETAILS
- **Minimum wage series**: **Vaghul & Zipperer (2016)** daily state-level series; quarterly maximum taken. URL: **https://github.com/benzipperer/historicalminwage/releases**.
- **Overall sample size**: **847,314 wage-bin-state-period observations**, built from **4,694,104 individual-level observations** (≈ 5.5 workers per $0.25 bin; denser in the $5–$15 range).
- **Per-event**: ~5,040 individual worker observations; employment effect summed over 36 cells in [MW−$4, MW+$4].
- **QCEW** benchmarking of the CPS E/POP ratio (Online App. F).
- Across 138 events: mean **8.6%** of workers below new minimum prior year; mean real MW increase **10.1%**. All MW increases in Online App. Figure A.1.
- Administrative hourly-wage data from **three US states** (incl. **Washington**) used to validate CPS.
