# Review — Cengiz, Dube, Lindner & Zipperer (2019)
### "The Effect of Minimum Wages on Low-Wage Jobs," *QJE* 134(3): 1405–1454

*A reading review with two co-headlines — the **bite** (first stage on wages) and the
**employment** effect — and a dataset section written for idea-generation.*

---

## 1. The one-paragraph version

CDLZ take 138 state minimum-wage increases (1979–2016) and, instead of asking "what
happened to average teen employment," they ask *where in the wage distribution jobs moved*.
They count the **jobs that vanish below** the new minimum (missing jobs, Δb = −1.8%) and the
**jobs that appear at/just above** it (excess jobs, Δa = +2.1%). The two nearly cancel: net
employment among affected workers is +2.8% (s.e. 2.9%) — a precise zero. Meanwhile the
**wages** of those same workers rise 6.8% (s.e. 1.0%). Same design, two numbers: a strong
wage effect and a null employment effect. The ratio is an own-wage elasticity of 0.41 whose
95% CI rules out anything more negative than −0.45.

---

## 2. BITE — the first stage on wages (your priority)

This is the part you care about, so it leads. **Bite = the first-stage effect of the MW on
the wages of affected workers** — `%Δw`, the change in the average hourly wage of workers who
were below the new minimum before it took effect.

**Why it is the load-bearing object.** The famous result is the *elasticity*, and the
elasticity is a **Wald-IV ratio**:

```
                    %Δ affected employment        (Δa + Δb)/b̄₋₁
   own-wage elast. = ──────────────────────  =  ─────────────────
                     %Δ affected wage  ← BITE         %Δw
```

The bite is the **denominator / first stage**. Footnote 6 is explicit: a *weak* first stage
(a small, imprecise wage effect) biases the elasticity toward the naive OLS of employment on
wages (Bound–Jaeger–Baker 1995). The whole methodological payoff of "look only at low-wage
jobs" is that it *guarantees a strong first stage* — a large, tightly-estimated wage effect —
where the conventional whole-distribution regression often can't even produce a significant
one. **The bite is what makes the elasticity credible.** If you take one design idea from
this paper, take that: engineer your estimand so the first stage is mechanically strong.

**How they build it (Eq. 2):**
```
   %Δw = (%Δ wage bill − %Δ employment) / (1 + %Δ employment)
```
It rests on one stated assumption: workers who *exit or enter* because of the policy have the
same average wage change as workers who *stay*. The `(1 + %Δe)` term is the retained-share
adjustment. No parametric wage model — it falls straight out of the binned counts.

**Decomposition — mechanical vs. ripple (Table IV):**
| | value | s.e. |
|---|---|---|
| Total bite `%Δw` | **6.8%** | 1.0% |
| Direct / mechanical (push everyone up *to* the floor) | 4.1% | 0.9% |
| **Spillover (ripple) share** | **~40%** | 11.9% |

So ~60% of the bite is mechanical and **~40% is a ripple** that reaches up to ≈$3 above the
new minimum (the 23rd percentile) and then dies. The cleanest evidence it's *real* and not
CPS measurement error: **incumbents** (employed a year before) get a **9.5%** bite with a 42%
ripple share, while **new entrants** get essentially nothing above the floor. Only people
already in a job get the raise-above-the-minimum — exactly what optimization-friction / pay-
norm models predict, not what measurement error would produce.

**Heterogeneity in the bite — this is where the design earns its keep.** Figure V regresses
event-level estimates on the **Kaitz index** (new minimum ÷ median wage, range 37–59%):

```
   Kaitz ↑ (bigger bite)  ⟶  missing jobs Δb: slope −0.133 (0.034)   [more jobs lost below]
                          ⟶  excess  jobs Δa: slope +0.139 (0.057)   [~equal gain at/above]
                          ⟶  net employment Δe: slope +0.006 (0.048)  [FLAT]
```

The bigger the bite, the more jobs move *below* the floor — **and** an almost identical number
reappear *at/above* it. The disemployment and the bunching scale **together**, so net
employment stays flat across the whole observed Kaitz range. That is the paper's real
punchline: not "the MW never bites" but "**even where it bites hard, the jobs relocate rather
than disappear** — up to a min/median of ~0.59."

**Bite by group** (Table II, %Δ affected wage): teens 8.3%, no-HS 8.0%, HS-or-less 7.6%,
women 7.2%, Black/Hispanic 4.4% (notably smaller and with a smaller, insignificant ripple).
**Bite by sector, via missing jobs** (Table III): restaurants bite hardest (Δb = −10.1%),
nontradeable −6.6%, manufacturing −1.7%, tradeable −1.6%, construction ≈ 0. The MW barely
touches tradeable/manufacturing wages — which is why the (imprecise) negative employment
signs there are more about composition than a real disemployment margin.

---

## 3. EMPLOYMENT — the reduced form

The null is *tight*, not just "insignificant." Net %Δ affected employment = **+2.8% (2.9%)**;
own-wage elasticity **0.41 (0.43)**, 95% CI excludes anything below −0.45; MW-elasticity
0.024 (0.025), ruling out Meer–West's −0.074. It survives: adding time-varying inequality
controls, dropping weights, post-1992-only, no-tip-credit states, FTE counts, raw vs. QCEW-
benchmarked CPS, and alternative windows/endpoints. The upper-tail bins ($5+ above the floor)
are the built-in placebo — flat, as they should be. And the diagnosis of *why* TWFE-logMW
finds job loss (Meer–West 2016) is surgical: decompose their coefficient by bin and the loss
sits in implausible upper-tail bins, driven entirely by pre-1992 events where MW changes are
few and confounded. That's a reusable move — **decompose someone's suspicious aggregate
coefficient into the bins that generate it.**

---

## 4. DATASET — deep dive + ideas for you

You asked for special attention here. The data spine is almost entirely **public**, which is
the main reason this paper is so reusable.

```
 SOURCE                     ROLE                         ACCESS
 ─────────────────────────────────────────────────────────────────────────────
 CPS-MORG (NBER)            wage distribution, per bin   PUBLIC  nber.org/morg
 Vaghul–Zipperer (2016)     daily state MW series        PUBLIC  github.com/benzipperer/
                                                                  historicalminwage/releases
 QCEW                       benchmark the E/POP ratio    PUBLIC  BLS
 MN / OR / WA admin wages   validate CPS misreporting    RESTRICTED (state agencies)
 Replication archive        code + data                  PUBLIC  Dataverse 10.7910/DVN/TJCTC7
```

**The construction, in one picture:**
```
 4,694,104 individual CPS-MORG obs (1979–2016, imputed wages dropped)
        │  assign each worker to a $0.25 real-wage bin (117 bins, $0–$30, 2016$)
        ▼
 collapse by  state × bin × quarter,  weight by ORG weights
        ▼
 847,314  (state × bin × quarter) cells        ← the estimation dataset
        │  normalize each cell by state-quarter population 16+
        ▼
 stack 138 events, re-center bins on each event's NEW minimum, ±$4 window, −3..+5 yrs
```

**Ideas this hands you** (tuned to what you work on):

1. **"Bite-first" design for any bunching-at-a-threshold policy.** The transferable engine is:
   *bin the running variable → count missing below / excess above a policy notch → net =
   bunching estimate, and the average shift = your first stage.* It isn't about wages — it's
   about any policy that relocates mass across a threshold (licensing floors, tax notches,
   eligibility cutoffs, price floors). For your **cannabis employment** work, the analogue is:
   is there a margin with a *notch* where you can measure a first stage (the "bite") before
   you report the employment reduced form? Reporting the bite makes a null employment result
   *interpretable* instead of just underpowered.

2. **The QCEW-benchmarking trick.** They have a rich-but-noisy survey (CPS) and a near-universe-
   but-thin admin file (QCEW), and they use the admin file to pin the *level* (E/POP) while the
   survey supplies the *distribution*. Cheap precision gain, point estimates barely move. If you
   have a survey + an admin count on the same units, steal this.

3. **The measurement-error argument as a design feature, not an apology.** Misreporting inflates
   Δb but *equally* deflates Δa, so the **net Δa+Δb is robust** as long as the reporting error
   stays inside the window. That's a lovely property — a design where the headline estimand is
   first-order immune to the classic complaint about your data. Ask whether your estimand can be
   written as a *difference* that cancels the error you're most worried about.

4. **Public + replicable end to end.** CPS-MORG + the Vaghul–Zipperer GitHub series + the
   Dataverse archive means you (or an RA) can literally rebuild Figure II from scratch — a good
   teaching asset and a good template for how to release your own project.

5. **The Kaitz-index dose-response as a template.** Rather than one ATT, they trace how the
   *whole decomposition* moves with treatment intensity (Kaitz). For a staggered-adoption design
   like yours, plotting each event's effect against an intensity measure — and showing the two
   opposing channels scale together — is far more persuasive than a single pooled coefficient.

**One caution if you borrow the data.** The bins are built from *self-reported* CPS wages with
imputed values dropped; the Jan-1994–Aug-1995 gap (no imputation flags) is a real hole. And the
whole thing is a **repeated cross-section** — no worker followed over time except the short
incumbent/entrant match via the ORG month-4 re-interview. If your question needs true panel
wage dynamics, CPS-MORG won't give it to you; you'd want LEHD/QWI or state UI wage records
(the very MN/OR/WA files they could only use for validation).

---

## 5. Strengths / limits (brief)

**Strengths.** Measures wage and employment effects in one coherent design; strong, honest
first stage; a built-in placebo (upper tail); a convincing forensic account of the opposing
literature; near-total public replicability.

**Limits.** External validity capped at the observed Kaitz range (≤0.59) — it explicitly does
*not* speak to a $15 floor in a low-median state. Tradeable/manufacturing elasticities are
negative but too imprecise to lean on. Eq. 2 leans on the exit/entry-wage-change assumption.
Repeated cross-section, not panel. And "affected employment" is defined by wage position, so
adjustment on *hours* rather than headcount would sit partly outside the frame.

---

### Files produced by this read
- `Cengiz et al 2019_text.md` — reusable structured extract (8 dimensions).
- `min wage_build/split_.../summary_pp*.md` — 13 per-chunk summaries.
- `min wage_build/split_.../bite.md` — the full first-stage deep dive with every table number.
