---
name: r1
description: >
  Rubin's R1 — "name the experiment." Interview-based skill that draws the
  hypothetical randomized experiment OUT of the user (3 questions, one follow-up
  max each), translates what it heard into Rubin-speak, then works out the target
  parameter (the prince's question + weighting + ATT/ATE/ATU, constrained by the
  design). Ends by offering to write a flippable/biggable R1 card to the dashboard.
  Use when the user says "/r1", "name the experiment", "what's my target", or is
  starting Step 1 of a DiD/causal analysis.
---

# /r1 — Name the experiment (Rubin's front door)

## What this is

Rubin (2008), "Design Trumps Analysis": before anything, **"conceptualize the observational
dataset as having arisen from a complex randomized experiment, where the rules used to assign the
treatment conditions have been lost and must be reconstructed."** R1 is that first act — naming the
experiment. Target (the estimand) is a *subset* of R1; assignment is what comes next.

This skill does NOT lecture. It **interviews** — it pulls the experiment out of the user, because
the user knows the science and just needs the right questions to articulate it Rubin's way. The
questions below are lifted from what Rubin says R1 requires: a manipulable treatment ("no causation
without manipulation"), a named outcome, and the lost randomization / decision-maker.

**R1 produces THREE cards, in order — each falls out of the one before:**
```
  1. THE EXPERIMENT      units · manipulable treatment · outcome · the lost randomization
  2. RESEARCH DESIGN     which identification the assignment story implies:
                         DiD · synthetic control · IV · RDD · unconfoundedness
  3. TARGET PARAMETER    the estimand + weighting — CONSTRAINED by card 2
```
How treatment was assigned (Q2) tells you the design (card 2); the design tells you which estimands
are even available (card 3). Draw them in that order.

## The rules of the interview

- Ask **ONE question at a time.** Wait for the answer. Then the next.
- **One follow-up maximum** per question — only if the answer is genuinely unclear or ducks the point.
- Warm, short, plain. You are drawing it out, not testing them.
- Grade silently against what a clean R1 needs; nudge only when an answer is missing a piece.

## PART A — the experiment (3 questions)

**Q1 · THE MANIPULATION.** "Describe the treatment as something someone could switch ON or OFF for a
unit. What is the unit, what is the intervention, and what is the outcome you'd measure afterward?"
- *Extracts:* unit, treatment, outcome.
- *Follow-up (only if needed):* "Could that treatment genuinely have been withheld from a treated
  unit, or given to a control one? If not, we may not have a well-defined experiment yet." (No
  causation without manipulation.)

**Q2 · THE LOST RANDOMIZATION.** "Picture the RCT this data stands in for. Who — or what — decided
which units got treated, and what did they know at the moment they decided?"
- *Extracts:* the assignment mechanism / decision-makers → these drivers are the **key covariates**
  (feeds R4 and Step 3). Rubin: being silent on how treatment was assigned is the single biggest
  weakness of an observational study.
- *Follow-up (only if needed):* "One decision-maker with one rule, or several with different rules?
  And of what they saw — how much can *we* also see in the data?"

**Q3 · THE PRINCE.** "Who wants this answer, and what will they do with it?"
- Al Roth: experiments serve three ends — (1) establish facts about the world, (2) talk to theorists
  and get them to change their theories, (3) **"whisper in the ears of princes."** Find the prince
  (a policymaker, a CEO). What decision rides on the number?
- *Follow-up (only if needed):* "Does the prince care about the average **unit** (e.g., the average
  county) or the average **person**?" — this is the weighting fork, handled in Part B.

## PART A.5 — the research design (card 2)

Read the assignment story straight off Q2 and NAME the identification strategy it implies. State it
in one line, then confirm with the user (a suggestion they own, not a verdict):
```
  sharp cutoff in a running variable, treatment flips at a threshold      → RDD
  an instrument / encouragement that shifts treatment but not Y directly  → IV
  treatment turns on at different times, untreated periods exist, a
    parallel-trends story is plausible                                    → DiD (incl. staggered)
  one (or a few) treated unit + a donor pool of untreated units           → SYNTHETIC CONTROL
  selection into treatment is captured by observed covariates; no
    discontinuity / instrument / timing leaned on                         → UNCONFOUNDEDNESS
```
This is card 2. It decides what estimands are even reachable in Part B.

## PART B — the target parameter (card 3 — synthesize, then suggest)

After the three answers, work out the estimand out loud with the user. Two moving parts:

**1. Population / weighting** (draw the distinction; don't assume):
- Average **unit** (e.g. average county) → **do NOT weight** → `(1/N_T) · Σ Y`.
- Average **person** → **weight by population** → `Σ Sᵢ·Yᵢ / Σ Sᵢ`, where `Sᵢ` = unit population.
- Same data, different question, different number. Make sure the prince's question picks one.

**2. Which estimand — constrained by the design:**
```
  DiD / synthetic control   →  ATT ONLY. Emphasize this — it is not a choice.
  Unconfoundedness          →  ATT / ATE / ATU all on the table. Default ATT.
  IV                        →  LATE / CACE — the effect for COMPLIERS only. Say so plainly.
  RDD                       →  effect LOCAL to the cutoff — a weighted ATT at the threshold.
```
- **ATT is the default** everywhere it's available. Only move off it with a reason tied to the
  prince's question.

## The close

1. **Translate to Rubin-speak.** "Here's your experiment: units = ___, treatment (manipulable) =
   ___, outcome = ___, the lost randomization = [who assigned, on what they saw], key covariates =
   ___. It's standing in for a [randomized block / encouragement] experiment."
2. **Suggest the target parameter** in one line, with the reason: e.g. "I'd suggest the
   **population-weighted ATT** — your design is DiD so ATT is all that's identified, and the prince
   wants the effect on the average *person*, not the average county."
3. **Offer the dashboard write:** ask verbatim — **"Would you like me to update the dashboard now?"**
   On yes, write/refresh the **THREE R1 cards** for this analysis (each flippable + biggable):
   ```
     Card 1 · The Experiment     FRONT one-line experiment · BACK units/treatment/outcome/
                                 lost-randomization/key-covariates in Rubin-speak
     Card 2 · Research Design    FRONT the design (DiD/synth/IV/RDD/unconfoundedness) ·
                                 BACK why the assignment story implies it
     Card 3 · Target Parameter   FRONT the estimand (e.g. pop-weighted ATT) · BACK the prince's
                                 question, the weighting choice, and why the design allows it
   ```
   Store where the dashboard reads the stage (e.g. `analyses/<slug>/stages/01_target/r1.md`, one
   section per card), so all three render in the R1/Target stage.

## Honest limits
- If the treatment isn't manipulable, say so and stop — there may be no well-defined experiment.
- If the design is DiD/synth, do not let the user believe they can get ATE/ATU. Say it plainly.
- Suggest a target; never impose one. The user names the experiment — you just hand them the words.
