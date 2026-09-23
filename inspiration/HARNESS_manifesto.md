# Design Trumps Analysis, and a Harness to Make Me Live By It
### Why I work causal inference through a checklist — and why AI made that non-negotiable

*Scott Cunningham · a working statement for the mixtape harness*

---

## 1. The principle: all observational causal inference should follow Rubin

I believe observational causal inference should follow Rubin's discipline. Objectivity is
not something you recover at the analysis stage with a clever regression — it is something
you **build at the design stage, before you ever look at the outcome.** A randomized
experiment is trustworthy because it is prospective and outcome-blind: you physically cannot
tune it to the answer you want. An observational study earns that same trust only by
imposing the same blindness on yourself — reconstruct the hypothetical experiment, find the
assignment mechanism, balance what needs balancing, and refuse to infer where the data can't
support it. *Then* analyze. Rubin's line is the whole creed:

> "Final outcome data cannot be used in design without compromising the objectivity of the
> study design." — Rubin (2008), *Design Trumps Analysis*

I've spent years trying to spell this out concretely, as practical guides in *Causal
Inference: The Mixtape* — one per research design. They look like four different checklists,
but they are the **same outcome-blind ritual** wearing four costumes:

```
  RUBIN'S STAGE        UNCONFOUNDEDNESS      RDD                IV                 DiD
  ─────────────────────────────────────────────────────────────────────────────────────────
  name the experiment  pick estimand /       define cutoff +    know the           define target +
                       population first       running variable   assignment mech.   timing/cohorts
  ─────────────────────────────────────────────────────────────────────────────────────────
  the ASSIGNMENT /      propensity score =    treatment prob.    FIRST STAGE Z→D,   rollout table +
  the BITE             analogue of            jumps 0→1 at       shown separately   event-study
                       randomization          the cutoff         & visually         design
  ─────────────────────────────────────────────────────────────────────────────────────────
  balance, outcome-    covariate balance +    McCrary density    effective-F,       parallel PRE-
  blind                common support         + covariate        Anderson-Rubin     TRENDS, honest
                       (trim off-support)     smoothness         CIs (weak-iv)      sensitivity
  ─────────────────────────────────────────────────────────────────────────────────────────
  refuse if no         drop off-support       placebo cutoffs    reduced form       placebo /
  overlap              units                  (find nothing)     Z→Y shown raw      falsification
  ─────────────────────────────────────────────────────────────────────────────────────────
  analyze LAST         estimate ATT last      estimate jump      OLS vs IV          robust estimator
                                              last               side-by-side       (CS/SA/dCDH/BJS)
```

The row I care about most is the second one — the **assignment mechanism**, which in my
teaching I call the **"bite."** It's the first stage: proof that the treatment actually moved
something real, shown *before* the outcome. In IV I say it as a commandment — *present the
first stage separately and visually, even if you'll estimate with 2SLS.* In RDD it's the
jump in treatment probability at the cutoff. In unconfoundedness it's the propensity score,
"the observational analogue of complete randomization." In DiD it's the first-stage shock —
the wage bite in Cengiz et al., the coverage ladder in Miller-Johnson-Wherry, the mental-
health-care bite in Dias-Fontes. **Same object, four designs.** Bite sits on the design side
of Rubin's line, by construction, and everything downstream depends on it.

So: I did not invent this. I am trying to embody Rubin — and Imbens, and others — in
practical, do-this-then-that language, so that ordinary researchers (me included) can
actually follow it.

---

## 2. Why AI made this urgent — and changed *why* it matters

Here is the turn. The checklist was always good practice. I think of it the way Atul Gawande
does in *The Checklist Manifesto*: **experts skip steps.** Not novices — *experts.* The more
fluent you are, the more you trust yourself to hold it all in your head, and the more
confidently you skip the boring verification that turns out to be the thing that saves you.
Overconfidence is not a beginner's disease; it scales *with* expertise. That's why surgeons
with decades of experience still kill people by forgetting a step a checklist would have
caught.

AI agents make this worse, and they make it worse for a **new reason.**

```
  BEFORE AI                          WITH AI AGENTS
  ─────────────────────────────────  ──────────────────────────────────────────
  I wrote the code line by line.     The agent writes 200 lines in one shot.
  Producing and verifying were       Production is nearly free; verification is
  the SAME motion — I understood     not. The two have been torn apart.
  it because I built it.
                                     I can approve work I did not produce and do
  Skipping a step cost me time,      not fully understand. The agent is confident
  so I felt the skip.                even when it's wrong — so the skip is silent.
```

This is the real problem, and it's psychological as much as methodological. The agent does so
much of the work that it **divorces the production of the work from my verification and
understanding of it.** I get output without having earned the understanding that used to come
free with the labor. That's a loss — of comprehension, of the felt sense of what's solid and
what's shaky, of the thing that made me trustworthy as the author.

So I am building a harness — grounded in Rubin, Imbens, and others — and I want to be precise
about what it's *for*. **It is not primarily for autonomous research.** It is to **restore
what I have lost by working with agents.** It re-couples production and verification so that I
understand my own work again: every figure traces to a script, every stage is gated, every
claim is defended before it advances, and the record lives on disk — because both the human
*and* the AI drift, differently, and neither can be the other's safety net. The harness is how
I keep the outcome data "not available at this stage" on purpose, the way randomization does
it for free. It is Rubin's discipline, made into machinery, because I no longer trust
willpower to enforce it against an agent that will happily do the next step before I've
checked the last one.

---

## 3. The prototype: `mixtape_harness`

I have a working prototype: **https://github.com/scunning1975/mixtape_harness**

It is a *research harness* — a set of interlocking rules, checklists, skills, and a live
dashboard that keep an AI-assisted causal-inference project honest, reproducible, and
resistant to drift. It's a template: clone it, point it at your own study, and it enforces the
discipline as you work. What's in it:

```
  THE LAW           CLAUDE.md — the constitution of the harness. Defines the
                    zero-error CONSTRAINT (not a goal — a constraint you bend
                    everything else around), the provenance rules, the figure
                    standards, and the AI's standing job: be keeper of the rules
                    and stop me when I try to skip a gate.

  THE CHECKLISTS    checklists/ — the DiD / continuous-DiD / synth checklists every
                    analysis walks, top to bottom: target parameter → covariates →
                    balance → bite/treatment viz → outcome-over-time → sample sizes
                    → estimator (CS-DiD preferred) → event study → Rambachan-Roth
                    sensitivity. The estimator will not run until the design steps
                    before it are signed off. That gate is the whole point.

  THE STAGES        analyses/<slug>/ — one folder per analysis, each stage a
  (canisters)       self-contained "room" holding its ideas, todos, findings, and
                    exhibits, so any stage is re-enterable tomorrow after the amnesia
                    sets in. A "You Are Here" stage-lock model colors each stage:
                    green = locked/done, amber = the one room you're in, red = open.
                    Exactly one amber at a time.

  THE DASHBOARD     dashboard_server.py — a live localhost:8080 dashboard that reads
                    the filesystem on every request, so it never goes stale. It's the
                    visual enforcement layer: stale outputs, orphaned figures,
                    unreviewed diffs, and unearned claims all show up in color.
                    Nothing enters the "Pipeline" tier without me clicking approve.

  THE INSTRUMENTS   skills/ — /amnesia (reorient after a gap), /newproject, /covariates
                    (interview-based covariate selection grounded in Heckman-Ichimura-
                    Todd), /pipeline (re-derive every exhibit from raw data), /referee2
                    (fresh-session adversarial audit), /blindspot (perception audit),
                    /drift-sweep, /bibcheck.

  WORKING MEMORY    STATE.md — the always-current "where am I" file I read on entry and
                    update continuously, because session amnesia is the resting state
                    and my memory of the work is the thing that drifts.
```

The spine of every analysis is the five-stage blueprint — the same one I teach: **(1) show
the bite** (the shock was real), **(2) falsification**, **(3) event study**, **(4) main
results**, **(5) mechanisms.** Bite first, outcome last. Rubin, made operational.

The `analyses/main/` folder ships a minimum-wage study as an *illustration* of what a walked
checklist looks like — the shape of an analysis, not a runnable pipeline. Delete it and
`/newproject` when you start your own.

**This is a prototype.** We'll be working through it to perfect it — the mechanisms are real
but rough, and the point of the next stretch of work is to sand them into something I'd hand
to anyone. But the idea is already here and already load-tested against my own drift: the
harness is Rubin's "design trumps analysis," turned into a machine that makes me live by it
even when an agent is offering to skip ahead.

---

## 4. Status

- Prototype lives at `github.com/scunning1975/mixtape_harness`.
- **Cloned locally to `~/mixtape_harness`.**
- Next: work through it to perfect it.
