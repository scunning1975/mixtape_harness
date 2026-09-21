# Rubin (2008), "Design Trumps Analysis" — pp. 9–12

## Overview of the argument
Section 3 gives the operational advice: design an observational study to approximate a randomized trial. The core conceptual move — "conceptualize the observational dataset as having arisen from a complex randomized experiment, where the rules used to assign the treatment conditions have been lost and must be reconstructed." Section 4 begins with Cochran's (1968) one-covariate smoking example.

## Rubin's design checklist (Section 3)
1. **What hypothetical randomized experiment led to the data?** (§3.2) Name exactly the treatment conditions and outcome variables. One dataset can map to several different hypothetical experiments (e.g., prenatal hormone vs. barbiturate vs. factorial). "Running regression programs is no substitute for careful thinking."
2. **Are sample sizes adequate?** (§3.3) Power calculations, and ratios needed for well-matched samples, *before* plunging ahead.
3. **Strip the outcome data.** Once samples look adequate, "strip any final outcome measurements from the dataset" — "outcome-free design is absolutely critical for objectivity." Hide all outcomes until design is complete. (Subtlety: "intermediate outcome data" like compliance, deferred to §5.)
4. **Who were the decision makers, and what did they see?** (§3.4) Why did some units get treatment vs. control? These background variables are the **"key covariates."** Were there multiple decision makers with different rules? "It is remarkable to me that so many published observational studies are totally silent on how the authors think that treatment conditions were assigned, yet this is the single most crucial feature that makes their observational studies inferior to randomized experiments."
5. **Are key covariates measured well?** (§3.5) If poorly measured or absent, look elsewhere. "No amount of fancy analysis can salvage an inadequate data base." Don't forget interactions and nonlinear terms.
6. **Can balance be achieved on key covariates?** (§3.6) Find subgroups/matched pairs where treated and control "look as if they could have been randomly divided." If balance is impossible, restrict inference to a subpopulation — or forgo the dataset entirely.

## §3.7 The result
The six steps yield a design conceptualizable as a "hypothetical, approximating randomized block (or paired comparison) experiment," blocks = balancing groups, treatment probabilities varying across blocks. Following the steps doesn't guarantee the RCT's answer, "but at least the observational study has a chance of doing so, whereas if these steps are not followed... it is only blind luck that could lead to a similar answer." Design alone (no outcome analysis) can be publishable (Langenskold & Rubin 2008).

## Running example — Cochran (1968) smoking (§4.1)
Compare death rates of male smokers: treatment = cigarette smoking, control = cigar/pipe smoking. **Strip the survival (Y) data first.** Decision maker = the individual smoker; dominant covariate = **age** (most start cigarettes as teens; pipe/cigar smokers start later). Focus on age as the single X. Hypothetical experiment: randomly assign smokers to cigarette vs. cigar/pipe, propensity a function of age. Age is well-measured; cigarette smokers are younger but there is "substantial overlap" — so the design can proceed to subclassification.

## DESIGN-BEFORE-ANALYSIS
- The decisive discipline: strip outcomes and design blind. "Outcome-free design is absolutely critical for objectivity"; "it is critical to hide all outcome data until the design phase is complete."
- Objectivity comes from reconstructing the lost assignment mechanism, not from modeling outcomes: describing regression programs is "entirely inadequate."
- Balance is the target; if it can't be achieved with enough units, the honest move is to walk away from the dataset.

## Quotable lines
- "conceptualize the observational dataset as having arisen from a complex randomized experiment, where the rules used to assign the treatment conditions have been lost and must be reconstructed." (p.9)
- "outcome-free design is absolutely critical for objectivity." (p.10)
- "no amount of fancy analysis can salvage an inadequate data base." (p.11)
- "it is only blind luck that could lead to a similar answer as in the analogous randomized experiment." (p.12)
