# Review — Miller, Johnson & Wherry (2021)
### "Medicaid and Mortality: New Evidence from Linked Survey and Administrative Data," *QJE* 136(3): 1783–1829

*Read through the five-elements-of-a-great-DiD lens: ① bite, ② falsifications,
③ event studies, ④ main results, ⑤ mechanism. Bite gets the most weight.*

---

## The one-paragraph version

MJW link restricted **ACS survey** records to **administrative death** (Census Numident)
and **Medicaid enrollment** (CMS) files, so they observe — for the same low-income
55–64-year-olds — who became eligible, who actually enrolled, and who died. Comparing
Medicaid-expansion to non-expansion states in an event-study DiD, they find a large
first stage (coverage takes off among exactly the targeted people) and a headline
**0.132 pp (≈9.4%) drop in annual mortality** that *grows over four years*, is
concentrated in **disease-related (internal, health-care-amenable) deaths**, and
implies roughly **19,200 lives saved over four years**. It is a near-textbook execution
of all five elements — which is why it teaches so well.

---

## ① BITE — the first stage (your priority)

The bite here is the effect of expansion on **insurance coverage** among the affected
low-income sample. What makes it a *great* first stage is that it's a **ladder**, not a
single number — you can watch the policy convert into coverage step by step:

```
   POLICY  ─────────────────────────────────────────────────────────
   Medicaid eligibility     +0.498  (s.e. 0.026)   ~50 pp newly eligible
        │  (take-up is partial — not everyone eligible enrolls)
        ▼
   Any Medicaid coverage    +0.128  (0.020)        12.8 pp enroll
   Medicaid days / year     +42.99  (8.89)
   Cumulative Medicaid yrs  +0.375  (0.061)
        │  (net of crowd-out from other coverage)
        ▼
   Uninsured                −0.044  (0.010)        4.4 pp fewer uninsured
   ─────────────────────────────────────────────────────────────────
   All significant at 1%. Whole-population coverage gain was only ~1 pp
   (Black et al.) → the sample selection successfully concentrated the bite.
```

Three teaching points fall out of this:

1. **Eligibility ≠ enrollment ≠ coverage.** The 50 pp eligibility jump is the *assignment*;
   12.8 pp is *take-up*; 4.4 pp is the *net* coverage change after crowd-out of private/other
   insurance. A weak first stage would blur these; MJW's is strong enough to show all three.
2. **The bite is what makes the reduced form legible.** The mortality effect only
   means something *relative to how much coverage actually moved*. Scaling the 0.132 pp
   reduced form by the ~0.375 cumulative-years bite is what turns "a DiD coefficient" into
   "the effect of Medicaid on the people it reached."
3. **Targeting is visible in the bite.** They chose the sample (≤138% FPL or <HS, age 55–64)
   precisely so the first stage would be large. The contrast with the ~1 pp whole-population
   number *is* the argument that they're studying the right people.

---

## ② FALSIFICATIONS — where this paper shines

The falsification battery is the element I'd hold up to students, because it's built as a
**dose-response**: the groups that get **no coverage bite** should get **no mortality
effect** — and they don't. (Figure IV, Figure III.)

```
  GROUP / TEST              coverage bite?     mortality effect?     verdict
  ─────────────────────────────────────────────────────────────────────────
  Age 65+ (Medicare)        ~zero              ~zero                 ✓ passes
  400%+ FPL (high income)   tiny               ~zero                 ✓ passes
  Pre-ACA placebo years     n/a                ~zero                 ✓ passes
  External-cause deaths      —                 +0.00038 (wrong sign) ✓ passes
     (injuries/homicide: shouldn't respond to insurance)
```

The external-cause-of-death test is the elegant one: insurance should cut *disease* deaths,
not *injury* deaths. Internal-cause DD = −0.00235; external = +0.00038 (tiny, wrong-signed).
The channel falsification and the population falsification point the same way. Plus the
mechanical robustness: **Goodman-Bacon** shows only 11% of the DD comes from
differently-timed comparisons (so the staggered-timing "bad comparison" problem is minor),
and a **Roth pre-trend power** calc shows the worst-case pre-trend bias (0.089 pp) is far
below the year-3 effect (0.208 pp). Survives ~12 specifications (opioid, trade, labor-demand,
demographic controls; triple-difference against 65+ and 400% FPL).

---

## ③ EVENT STUDIES

Two of them, and the *pairing* is the point:

- **Coverage event study (Fig I):** effect is flat pre-2014, jumps at expansion, stable at
  ~0.11–0.13 across years 0–3. The bite turns on sharply and stays on.
- **Mortality event study (Fig II):** flat pre-trend, then a *growing* effect —
  yr0 −0.089 pp (7.0%) → yr1 → yr2 → **yr3 −0.208 pp (11.9%)**.

The contrast in *shapes* is the mechanism preview: coverage jumps to a plateau immediately,
but mortality accumulates — consistent with health benefits that build with exposure
(managing chronic disease over years), not a one-time level shift. A great classroom example
of reading the *dynamics*, not just the pooled coefficient.

---

## ④ MAIN RESULTS

```
  Pooled DD, annual mortality:  −0.00132  (s.e. 0.00050, p<0.05)
      = −0.132 pp = 9.4% vs. sample mean (8.1% vs. counterfactual 1.63%)
  Grows to −0.00208 by year 3 (11.9%)
  Uninsured-at-baseline subset: −0.150 pp (10.3%)
  Lives saved: ~4,800/year, ~19,200 over four years
  Non-expansion states' "cost": ~15,600 deaths
```

The precision is good enough to *rule out* small effects (yr-3 CI excludes effects below
0.045 pp). The paper
wins by making the null-or-signal *tight*, not merely significant.

---

## ⑤ MECHANISM

Three converging pieces of evidence that it's **health care**, not something else:
- **Cause of death (Table II):** the decline is concentrated in **internal causes
  (−0.00235)** and specifically **health-care-amenable causes (−0.00099)**; external causes
  flat/wrong-signed. Insurance kills disease deaths, not accidents.
- **Timing (Fig II):** the effect *grows* with cumulative Medicaid exposure — a treatment
  that works through sustained access to care, not a one-off.
- **Dose-response across groups:** biggest where the coverage bite is biggest; zero where
  it's zero. Mechanism and falsification are the same evidence read two ways.

(No dollar cost-per-life headline in the results pages; they benchmark against Sommers 2017.)

---

## How this paper nails BITE — the teaching point

```
                    MILLER–JOHNSON–WHERRY
                    (Medicaid → mortality)
 ─────────────────────────────────────────────────────
 What is the bite?  Δ COVERAGE of affected
                    = ladder: elig +50pp →
                      enroll +12.8pp →
                      uninsured −4.4pp
 Shape of it        a LADDER (assignment →
                    take-up → net), engineered
                    by sample selection
 Why it matters     scales reduced form into
                    per-newly-covered effect
 Falsification      age 65+/high-income (no bite,
 tied to bite       no effect); external deaths
 Reduced form       −9.4% mortality, TIGHT
 Shape over time    GROWS over 4 years
```

**The lesson for your students:** the bite is *engineered*, not found — here by selecting a
low-income, near-elderly sample. A strong, visible first stage is what licenses everything
downstream: it makes the falsifications sharp (turn the bite off, the effect vanishes), gives
the event study something to plateau at, and converts the reduced form into a real treatment
effect. **No bite, no interpretable DiD.** That's the whole first element, and the paper puts
it on the page before it shows a single main result. Compare `REVIEW_Dias_Fontes.md`, where
the bite is two-sided.

---

### Files produced by this read
- `papers_build/split_Miller_Johnson_Wherry_2021/summary_pp*.md` — 9 per-chunk summaries,
  each tagged with a **DiD ELEMENTS** section.
- This review: `REVIEW_Miller_Johnson_Wherry.md`.
- Companion: `REVIEW_Dias_Fontes.md`.
