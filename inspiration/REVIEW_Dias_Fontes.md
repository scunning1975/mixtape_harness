# Review — Dias & Fontes (2024)
### "The Effects of a Large-Scale Mental Health Reform: Evidence from Brazil"

*Read for one purpose: is there a **bite** here you can show students, sitting in front of a
log-homicide outcome? Answer: yes — a rich, two-sided one. Organized around the five
elements of a great DiD, bite first.*

---

## The one-paragraph version

Brazil's 2002 psychiatric reform rolled out **CAPS** (Centros de Atenção Psicossocial,
community mental-health centers) municipality-by-municipality over 2002–2016. Dias & Fontes
use the staggered timing (de Chaisemartin–D'Haultfœuille estimator, 5,180 municipalities) to
show CAPS **sharply raised outpatient mental-health care** and **cut psychiatric
hospitalizations** — a large, clean first stage — but had **null effects on deaths of despair**
(suicide, overdose, alcohol) and **raised homicides by 0.149/10k (+7.7%)**. Their explanation
is **Penrose's hypothesis**: shifting the crime-prone severely-ill (mostly schizophrenia,
long-stay) out of incapacitating institutions into under-resourced community care increases
violence. For your project this paper is doubly useful: it hands you a ready-made bite *and*
it is the very homicide result you'd be replicating or contesting.

---

## ① BITE — the first stage (this is the payoff for your harness)

CAPS gives you a **two-sided bite**, which is even better pedagogy than MJW's ladder because
the two sides move in *opposite* directions — care shifts from institution to community:

```
  TREATMENT GOES UP (community care)          5-yr ATT (s.e.)      vs. baseline
  ────────────────────────────────────────────────────────────────────────────
  MH professionals per 10k          +0.834 (0.053)     +46%   (base 1.82)
     psychiatrists                  +0.151 (0.015)     +60%
     psychologists                  +0.342 (0.030)     +27%
  Outpatient MH procedures per 10k  +264.2 (27.1)     +113%   (base 233.7)  ★ biggest
     by psychiatrists               +98.2  (10.3)
     by psychologists               +89.5  (8.7)

  INSTITUTIONAL CARE GOES DOWN (the "not-in-care"/deinstitution margin)
  ────────────────────────────────────────────────────────────────────────────
  Psychiatric admissions per 10k    −0.951 (0.272)     −7.5%   (base 12.66)
     long-stay (>30 days)           −0.621 (0.155)             (base 6.04)
     schizophrenia (crime-prone)    −0.823 (0.122)             (base 5.36)  ★ mechanism
  Federal MH-hospital spending      −0.157 (0.032)     −15.7%  (log)

  ⚠ Psychiatric BEDS: no clean effect — the bed series was already declining
     since the 1980s independent of CAPS. Do NOT use beds as your bite.
```

**Which bite to actually show students / use for CAPS→log homicides:**

1. **Best single "care went up" bite:** outpatient MH procedures per 10k (+113%) or MH
   professionals per 10k (+46%). Both from **CNES/SIA (DATASUS)**, municipality-year, exactly
   your unit. A vivid, enormous first stage — the visual will land on camera.
2. **Best "not in care" bite — and the one that mechanistically drives homicides:**
   **psychiatric admissions per 10k, −0.95 (−7.5%)**, concentrated in **long-stay schizophrenia
   (−0.82)**. This is the deinstitutionalization margin you were reaching for ("mentally ill not
   in institutional care"), and it is the numerator-partner of their Penrose story.
3. The authors literally use the **homicide ÷ hospitalization ratio (0.149 / −0.95)** as a
   dose-response: ≈**15.7% of deinstitutionalized patients involved in a violent death**. That
   ratio *is* bite-scaling — reduced form over first stage — the same Wald logic as
   MJW's per-covered mortality effect. Perfect for the harness: one arrow from
   BITE to MAIN RESULT.

**Why this is the teaching point.** The bite here is *engineered by the reform's design* (staggered
municipal rollout), and it is **two-directional** — the same policy pushes one care margin up and
another down. That makes "what is the first stage?" a genuinely interesting question rather than a
formality: you have to decide *which* margin is the treatment channel for homicides (answer: the
hospitalization drop, not the outpatient rise).

---

## ② FALSIFICATIONS

- **Placebo/pre-trend:** joint placebo effect = 0 across the supply, hospitalization, and homicide
  outcomes; homicide placebo 0.016 (0.012), pre-CAPS levels parallel between treated/control
  (joint placebo p = 0.45).
- **Outcomes that shouldn't move, don't:** infant mortality −0.001 (ns), all-cause 0.042 (ns) —
  clean placebos on unrelated mortality.
- **Non-MH physician supply:** family doctors / GPs / all physicians show no significant CAPS
  effect — the supply bite is *specific* to mental-health workers, not general health investment.
- **Confounder robustness:** results survive controlling for PSF (family-health program) rollout
  and Bolsa Família, spillover tests (effects confined to treated units, no displacement), and
  alternative specifications.

---

## ③ EVENT STUDIES

Dynamic DiD, event window −5..+5, with anticipation noted the year before opening (municipalities
apply, so timing is partly chosen). Event-study figures for: MH practitioners (Fig 3), outpatient
procedures (Fig 4), hospital admissions (Fig 5), spending (Fig 6), deaths of despair (Fig 7), and
**homicides (Fig 8)** — flat pre-trend, effect emerging post-adoption and building to the 5-yr
0.149. The paired shapes tell the story: supply jumps, admissions fall, homicides drift up with a lag.

---

## ④ MAIN RESULTS

```
  Outcome (5-yr ATT, s.e.; baseline per 10k)
  ────────────────────────────────────────────────────────
  Homicides            +0.149 (0.044)   +7.7%   base 1.94   ★ headline (2-yr: +0.082)
  Suicide               0.002 (0.017)    ns     base 0.51
  Deaths of despair    −0.022 (0.032)    ns     base 2.04
  Overdose              0.001 (0.003)    ns
  Alcohol-related      −0.018 (0.027)    ns     base 1.35
```

The mortality-of-despair nulls are tight (MDE ≈3–4%), converge to zero at 8 years — read as a
true zero, not low power. The homicide increase is the one thing that moves.

---

## ⑤ MECHANISM

**Penrose / lost-incapacitation.** Deinstitutionalization removes the severely mentally ill
(long-stay, schizophrenia) from settings that incapacitate a crime-prone group, into community
care that (in Brazil) is under-resourced — **<3% of municipalities** have 24-hour CAPS with beds
and crisis services. Evidence chain: (i) the hospitalization drop is concentrated exactly in
long-stay schizophrenia; (ii) the homicide/hospitalization dose-response (15.7%) is bracketed by
a back-of-envelope using discharge-to-violent-crime benchmarks (~9.6%); (iii) no effect on
self-directed harm (suicide/overdose), consistent with an *incapacitation* channel rather than a
general mental-health-deterioration channel.

---

## What this means for YOUR CAPS → log-homicide design

```
   YOUR DESIGN, WITH A BITE OUT FRONT
   ──────────────────────────────────────────────────────────────
   ① BITE      CAPS opens ⟶  psychiatric admissions ↓ (−0.95/10k,
               long-stay schizophrenia −0.82)   [+ outpatient care ↑]
                     │
   ③ EVENT     flat pre-trend on both bite and log-homicides
   STUDY             │
   ④ MAIN      ⟶  log homicides ↑
                     │
   ⑤ MECH      Penrose: bite×incapacitation → violence
               dose-response = Δhomicide / Δadmissions
```

- **The bite you asked for exists and is clean.** "Care of the mentally ill" = outpatient
  procedures/professionals (↑); "mentally ill not in [institutional] care" = psychiatric
  admissions (↓). Both are municipality-year DATASUS series you can rebuild.
- **Pick the hospitalization drop as the *causal* first stage for homicides.** The outpatient
  rise is a bite too, but the Penrose logic runs through *lost incapacitation* — so the −0.95
  admissions series is the first stage that mechanistically belongs in front of log-homicides.
- **Decide your stance.** Because the paper already regresses homicides on CAPS, your value-add
  is either (a) a cleaner/updated bite (e.g., bite measured as *long-stay schizophrenia
  discharges*, tightening the Penrose channel), (b) heterogeneity by CAPS *type* (only CAPS III
  has beds — does the bite→homicide link vanish where community care is well-resourced?), or
  (c) a modern-DiD robustness re-examination. Any of these keeps you from merely reproducing
  their Table 5.
- **Data is fully public & replicable.** Replication archive: AEA/ICPSR
  `https://doi.org/10.3886/E195122V1`. Sources: CNES (facilities/professionals), SIA (outpatient),
  SIH (admissions — your bite), SIM (homicides — your outcome), all DATASUS; covariates from
  IBGE/IPEA. You could rebuild both the bite and the outcome from scratch.

**One caution.** CAPS timing is partly *chosen* (municipalities apply), with anticipation effects
the year before opening — so your bite's identification leans on the staggered-DiD parallel-trends
assumption plus their placebo battery. If you make the hospitalization drop your headline first
stage, show its pre-trend as carefully as the homicide pre-trend.

---

### The two-paper bite through-line (for the film)

```
                 BITE = first stage, engineered by design, that licenses everything after
  ───────────────────────────────────────────────────────────────────────────────────────
  MJW   Medicaid  │ Δ coverage (elig→enroll→uninsured)│ a LADDER        +50→+12.8→−4.4pp
  DIAS  CAPS      │ Δ care (outpatient ↑ / admits ↓)  │ TWO-SIDED       +113% / −7.5%
  ───────────────────────────────────────────────────────────────────────────────────────
  Each turns its policy into a measured first stage BEFORE the outcome. That is element ①,
  and it is the folder in your harness where the design is won or lost.
```

### Files produced by this read
- `papers_build/split_dias-fontes-.../summary_pp*.md` — 9 per-chunk summaries (bite-tagged).
- This review: `REVIEW_Dias_Fontes.md`. Companion: `REVIEW_Miller_Johnson_Wherry.md`.
