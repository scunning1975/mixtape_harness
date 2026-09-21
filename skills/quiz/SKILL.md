---
name: quiz
description: Seven multiple-choice questions, asked ONE AT A TIME, to check that Scott actually understands something — a diff, an analysis, a decision, a data pull, a stage's evidence. Use when Scott says "quiz me", invokes /quiz, or asks for help understanding something specific ("/quiz about the evidence we've been working on for xyz", "quiz me on what you just did"). Grounded in Geoffrey Litt's "Understanding is the new bottleneck" (July 2026) and Silicon Central's third row: understanding is HUMAN and hooked via a SCORE. The score, not a click, is what pays down understanding debt.
---

# /quiz — seven questions, one at a time

## Why this exists

**Understanding is the bottleneck, not production.** Agents write faster than Scott can read, and the
verification ledger has been counting the wrong thing: *clicks* (diffs approved) rather than
*comprehension*. Approving a diff you skimmed discharges nothing.

Litt's key distinction, and the reason this skill is not a test:

```
  UNDERSTAND TO VERIFY              UNDERSTAND TO PARTICIPATE
  is the work correct?              can I have the next idea?
  thumbs up / thumbs down           needs a rich set of concepts in mind
  the agent is getting good         ← THIS is the human's irreducible job
  at this itself                      and it is what the quiz protects
```

So the quiz is **not** Claude checking Scott's homework. It is the speed regulator that keeps the loop
running no faster than Scott's understanding — because his fluency with the system is what generates the
next move. Margaret Storey's **cognitive debt**: you can skip understanding short-term, it bites later.
The failure it prevents is "losing the plot" while every box is green.

In this harness's own terms (`decisions/silicon_central.md` §3): footprint → autonomous+hooked;
judgment → human+interviewed, never hooked; **understanding → human+hooked via a SCORE.** Understanding
*feels* like judgment, which is why it went unguarded — but unlike judgment it yields a number, and a
number can gate. This is the row that fixes the skimming.

## THE HARD RULE — re-read the source before writing a single question

**Never write quiz questions from your own memory of the work.** Read the actual artifacts first —
the diff, the script, the data file, the findings, the decision note — even if you produced them
yourself minutes ago, and *especially* if it was in an earlier session.

Why this rule comes first: per CLAUDE.md, Claude's drift mode is **inventing confidently** what it
thinks it knows. A quiz written from a drifted memory grades Scott *wrong for being right* — it
teaches him a hallucination and calls his correct answer a miss. That is worse than no quiz, because
it corrupts the one channel meant to be the ground truth of his understanding. **Every question's
answer must be traceable to something you read on disk during this invocation.** If you cannot point
at the file and line the answer comes from, the question does not ship.

Corollary: if the target has *no* artifacts (a conversation, an unbuilt plan), say so and quiz on the
reasoning as recorded — labelling it as such — or decline and offer to quiz something real instead.

## Resolving the target

Scott will point at something, sometimes loosely: *"quiz me on the data pull," "quiz me about the
evidence for the coverage arm," "quiz me on what you just did," "/quiz the Stage 1 rebuild."*

1. **Name the target back to him in one line** and say what you're about to read. If genuinely
   ambiguous between two targets, ask which — one question, not a menu of four.
2. **Read the artifacts.** Diff → `git show`/`git diff`. Analysis → the scripts + the exhibits + the
   `findings.md`. Data → the file itself and the DAS. Decision → the decision note. Stage → the
   canister's four files.
3. **Bare `/quiz` with no target** = quiz the most recent substantive work of the session.

## ★ STEP ZERO — THE LESSON, BEFORE ANY QUESTION (Scott, 2026-08-07)

**Default to teaching first, then quizzing.** This is the corporate-training shape Scott named: you learn
the thing, you watch it demonstrated, *then* you get tested. A quiz with no lesson in front of it measures
whether he happened to absorb something in passing — which is not the point. The point is that he
understands it afterward.

> **Why this had to be written down.** The "What this skill is NOT" section already said *"Litt's order is
> explainer then quiz — the quiz checks what an explanation taught. If no explanation has been given, teach
> briefly first or expect low scores that measure nothing but the missing lesson."* But the procedure never
> contained an explainer step, so invocations went straight to Q1. Same failure as `/amnesia`'s missing
> interview: a decision that lives only in prose and not in the executable steps gets skipped. Hence Step
> Zero.

### How to teach it — ONE IDEA PER TURN, and he confirms before you move on

**Not a lecture.** The lesson is delivered the same way the questions are: **one piece at a time, waiting
for him after each.** Aim for **3–5 lessons** before the seven questions. Each lesson turn:

1. **One idea only.** The single fact, mechanism, or distinction. If you find yourself writing "and also,"
   that is the next lesson, not this one.
2. **Show it, don't assert it.** Put the actual number, the actual two rows side by side, the actual
   before/after. An ASCII figure beats a paragraph — this is his highest-value channel, and a lesson he
   can *see* survives where a lesson he read does not. **Where the artifact exists, point at the real
   thing** (the table, the figure, the two week-label lists) rather than describing it.
3. **Say why it matters here** — one line connecting it to this project's actual decision. A fact with no
   consequence is trivia and will not stick.
4. **End with a check, not a quiz question.** *"Does that land?"* / *"Want me to show it a different
   way?"* He may say "yes, next" or push back — and **pushback is the most valuable outcome of the whole
   ritual**, because it means the idea reached him well enough to argue with. If he pushes back, teach it
   again differently before moving on. Do not proceed on a shrug.
5. **Keep it SHORT.** A lesson turn should be shorter than a quiz question's worth of reading. Ration the
   prose; lean on the drawn element.

### Then the seven questions, unchanged
After the last lesson, say plainly that the lesson is over and the questions start now — the shift from
teaching to testing must be explicit, so he knows he is being graded and not still being taught. Then run
the protocol below exactly as written (one at a time, four options, anti-guessability, honest scoring).

### The scorecard reads differently after a lesson
Grade the same, but **interpret** differently: a miss after an explicit lesson means **the teaching
failed**, not that Scott failed. Say so on the scorecard and name which lesson did not transfer — that is
feedback on the explainer, and it is the more useful signal. A skipped-lesson quiz can only tell you he
didn't already know something; a taught-then-quizzed one tells you whether the explanation worked.

### When to SKIP the lesson
- He says "just quiz me" / "skip the lesson" — his call, always.
- The quiz is deliberately probing what he retained from *earlier* work (a diff from last week, a decision
  from a prior session). Teaching first would contaminate exactly what you are trying to measure. **Say
  which mode you are in** so the score means something.
- The material was just explained in this session, in depth, minutes ago.

## The seven questions — what to ask about

Seven questions, mixed by *kind* so the quiz measures understanding rather than recall. Aim for
roughly this spread (adapt to the target; don't force a kind that doesn't apply):

| # | Kind | Asks |
|---|---|---|
| 1–2 | **What it is** | the substance: what the thing does, what the number is, what the grain is |
| 3–4 | **Why this and not that** | the fork we took and the alternative we rejected — the reasoning |
| 5 | **What would break it** | the assumption, the fragile step, the thing that would invalidate it |
| 6 | **Where it lives / how it's proven** | provenance: which script, which file, what makes it canon |
| 7 | **What's next / what it implies** | the participate question — what this enables or blocks |

Question 7 matters most and is the one a generic quiz would omit. Understanding-to-participate means
he should finish the quiz better equipped to have the next idea, not just to recite the last one.

**Ask about what is genuinely important.** Do not ask trivia (an exact filename, a column count) unless
the number itself carries meaning. The test for a good question: *would getting this wrong mean he'd
make a worse decision tomorrow?* If no, cut it.

## Anti-guessability — REQUIRED, not optional

A guessable quiz is a fake gate, and this exact failure was observed in the wild: in the
`/explain-diff` gist comments, multiple people found the correct answer was reliably **the longest
option** and often **in position two** — answerable without reading the question at all.

Design against it, every time:

- **Shuffle the correct position per question**, and **balance positions across the seven** — roughly
  even across A/B/C/D, never the same letter three times running. Decide the position *before*
  writing the options so you don't drift toward B.
- **Match options for length, grammar, and specificity.** If the right answer is a precise clause with
  a number, the distractors get precise clauses with numbers. No option should stand out as the
  "careful" one.
- **Build every distractor from a REAL misunderstanding** — not noise. The best sources of distractors:
  - the thing he'd plausibly believe from a *previous* version of the work (a superseded fact);
  - a sibling project's answer (another project's numbers, another stage's sample);
  - the confusion the work itself corrected (if the pull's note said 88,751 and the file has 101,629
    rows, the note's number is the perfect distractor);
  - the intuitive-but-wrong reading of a method.
  A distractor nobody would pick is a wasted option and shrinks the quiz to three choices.
- **Four options** (A–D). No "all of the above," no "none of the above" — both are guessable.

## Protocol — ONE AT A TIME, no exceptions

**Ask one question. Wait for the answer. Then the next.** Never batch. Never show question 2 before
he has answered question 1, and never reveal the full question set up front — seeing later questions
leaks answers to earlier ones.

> This discipline gets skipped when it lives only in prose. `/amnesia` was redesigned into an
> interview, the decision was recorded, but the procedure never listed the questions as a step — so an
> invocation that followed the steps literally produced a summary and skipped the interview entirely.
> Hence: one question per message, and the wait is the step.

**Render each question in a box** — Scott reads boxes and skims prose:

```
  ┌─ Q3 of 7 ────────────────────────────────────────────────────┐
  │                                                              │
  │  <the question, one or two lines>                            │
  │                                                              │
  │    A)  <option>                                              │
  │    B)  <option>                                              │
  │    C)  <option>                                              │
  │    D)  <option>                                              │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

**After each answer, respond in 1–3 lines. Not more.**
- **Right:** confirm, and add the one detail that deepens it. Warm and brief — "yep, and the reason
  that matters is…"
- **Wrong:** say so plainly, give the correct answer and *why the wrong one was tempting* — name the
  misunderstanding the distractor was built from. This is the teaching moment; it's why distractors
  come from real confusions. No scolding, no piling on.
- **"I don't know":** that's an honest, useful answer. Treat it as a wrong answer for scoring, teach
  the point, and move on without ceremony.
- Then go straight to the next question. Do not summarize mid-quiz.

Accept a bare letter, the option text, or a paraphrase. If he answers with reasoning that's right but
picks the wrong letter, say so — the reasoning is what counts, and note it as a near-miss.

## The scorecard

After Q7, one box. This is the artifact — put it last in the reply per the closing-box rule.

```
  ┌─ SCORE: 5 / 7 ───────────────────────────────────────────────┐
  │                                                              │
  │   Q1 what it is        ✓        Q5 what breaks it     ✗       │
  │   Q2 the grain         ✓        Q6 provenance         ✓       │
  │   Q3 the fork          ✓        Q7 what's next        ✗       │
  │   Q4 the alternative   ✓                                     │
  │                                                              │
  │   SOLID:   the substance and the reasoning — you have the     │
  │            fork and why we took it.                          │
  │   THIN:    the fragility, and what it sets up next.          │
  │                                                              │
  │   ONE THING TO RE-READ:  <file / section>                     │
  │                                                              │
  └──────────────────────────────────────────────────────────────┘
```

Rules for the scorecard:
- **Pass = 6/7.** Litt's own rule was "I won't send code to others until I can pass the quiz" — so a
  score under 6 means the thing is not ready to leave the room, and the honest move is to re-teach and
  offer a re-quiz on the missed ground, not to wave it through.
- **Name a pattern, not just a tally.** Two misses on "why this not that" is a different diagnosis than
  two misses on "what it is" — the first means the reasoning didn't transfer, the second means the
  substance didn't. Say which.
- **Exactly ONE thing to re-read.** Not a list. The point is to spend his reading budget where it pays.
- **Be honest about the score.** Inflating it defeats the entire purpose — an ungraded quiz is a click
  by another name. Warmth lives in the tone and the teaching, never in fudging the number.

## Recording the score (understanding debt)

Silicon Central's ledger counts **quizzes unpassed**, not diffs unclicked. So the score is written
down, one line, appended to `understanding_ledger.md` at the project root (create it if absent):

```markdown
| date | target | score | pass | thin on | re-read |
|------|--------|-------|------|---------|---------|
| 2026-08-05 | pulse data pull 080426 | 5/7 | no | fragility, next-step | DATA_SOURCES.md §8 |
```

Keep it to one row per invocation. This is the number a hook can eventually read — do not build the
hook here; just keep the ledger honest so it exists when the hook does.

## What this skill is NOT

- **Not a gate Claude enforces on Scott.** He can stop the quiz, dispute a question, or say "skip it."
  If he disputes a question, take it seriously — re-check the artifact. He may be right and the
  question may be wrong, which is a Claude-drift catch and more valuable than the quiz.
- **Not a substitute for the diff gate.** Paul's unit (the diff is the right bounded thing to verify)
  and Litt's medium (the raw diff is the worst format for understanding it) compose — the quiz changes
  what he reads at the gate, it doesn't remove the gate.
- **NO LONGER separate from the explainer** — as of 2026-08-07 the explainer is **Step Zero of this
  skill**, not a thing that happens elsewhere. See that section. The note below is kept because it states
  the reason. Litt's order is explainer *then* quiz — the quiz checks
  what an explanation taught. If no explanation has been given, teach briefly first or expect low
  scores that measure nothing but the missing lesson.
- **Not for judgment calls.** Do not quiz Scott on a decision that is his to make (which covariates
  matter, whether social/X stays in the sample). Those are the middle row — elicited by interview,
  never graded. Quiz the *understanding* of a decision's consequences, never the decision itself.

## Origin

Created 2026-08-05 at Scott's request, from Geoffrey Litt's "Understanding is the new bottleneck" (AI
Engineer conference talk, July 2026) — the essay that named the problem and supplied the quiz-as-
speed-regulator idea, plus the guessability failure mode found in its `/explain-diff` comments. It
implements the third row of the axis written down two days earlier in
`decisions/silicon_central.md` §3 and §5 (understanding → human, hooked via a score;
the ledger counts quizzes unpassed), and it is the sibling of `/covariates` and `/amnesia` — the
harness's three one-question-at-a-time interviews, each guarding a different row: judgment,
orientation, understanding.
