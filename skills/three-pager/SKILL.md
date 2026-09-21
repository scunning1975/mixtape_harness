---
name: three-pager
description: Use when turning a completed project DECK into a numbered Word (.docx) three-pager deliverable — invoked via /three-pager, or when the user says "write up the deck," "turn the deck into the doc/three-pager," or "draft the research appendix from the deck." Assumes the deck is finished and its figures/tables are pipeline-produced.
---

# three-pager

## Overview

Turn a finished **deck** into a numbered Word `.docx` three-pager in the project's established
established Word format. The deck is the entire source: its slide order is the outline,
and **every figure and table shown in the deck is an exhibit that MUST appear in the document.**
Multiple agents draft the sections in parallel; one agent assembles them into the docx.

**Core principle:** nothing enters the three-pager that is not in the deck, and nothing in the deck
is left out of the three-pager. The deck ∩ document = the deck's exhibits, exactly.

## When to use

- The deck is DONE (reviewed, numbers verified) and you want the written deliverable.
- The project already has the format template (`manuscript/_template_*.docx`) + a build-script pattern.
- NOT for drafting a deck (that's the deck skills), and NOT for a paper whose exhibits aren't yet in a deck.

## Inputs (read these first)

1. **The deck** — the single HTML/Beamer deck. Its slide sequence is the outline; extract every
   `<img>` / table it shows → the **EXHIBIT LIST** (this is the gate checklist below).
2. **The format guide** — `manuscript/_template_<Name>.docx` and the build-script pattern in
   `code/build_manuscript_docx.py` (the `CONTENT = [(kind, text), ...]` model; kinds:
   title/h1/h2/amznh2/body/bullet/note; styles inherited from the template). This fixes the
   numbered VoComm-style structure and the ~3-page length.
3. **The pipeline** — the source of every exact number (deck-from-pipeline). Sections cite numbers
   that trace to `data/derived/` outputs, never invented.

## Workflow

1. **Parse the deck** into (a) a section map — slides → manuscript sections (title, note, Purpose,
   Background, Problem/Opportunity, Key Findings, FAQs, Appendices A..N) — and (b) the **EXHIBIT LIST**
   (every figure/table the deck shows, by file).
2. **Fan out — one subagent per SECTION.** Each drafts its section FROM THE DECK (+ pipeline for exact
   numbers), in the template's voice and length share, preserving `[INTERNAL]`/`[PUBLIC]` labels.
   Total body ≈ the template's length (~1,300–1,700 words / ~3 pages). Dispatch in parallel.
3. **Assemble — one agent.** Collect the section drafts, write them into a `CONTENT` list, and produce
   a build script mirroring `code/build_manuscript_docx.py` (open the template, clear the body,
   write styled blocks, save the `.docx`). Run it.
4. **Insert exhibits.** Every deck figure/table is placed in the doc (appendices / end). ONLY deck
   exhibits — nothing the deck doesn't show.
5. **THE GATE (below) — mandatory before done.**
6. Report the word count vs the template's, and the exhibit-coverage result.

## THE GATE — every deck exhibit must be in the document

Before the three-pager is complete, enumerate **every figure and table shown in the deck** and confirm
each one appears in the `.docx`. This is a hard stop, not a nicety.

```
for each exhibit in DECK:
    assert exhibit is present in the document  →  else STOP and add it
missing count MUST be 0 before "done"
```

**No exceptions:**
- Not "the doc is already ~3 pages, one figure won't fit" — the length target bends to the gate, not the reverse.
- Not "that exhibit is minor" — if it earned a slide, it earns a place in the doc.
- Not "I'll add it later" — later is never; add it now or it isn't done.
- Not "the number is in the prose, close enough" — the *exhibit* (the figure/table) must be in, not just its number.

Report the coverage explicitly: `EXHIBIT COVERAGE: N of N deck exhibits present (0 missing)`.

## Red flags — STOP

- About to say "done" without having listed the deck's exhibits and checked each → you skipped the gate.
- A figure is in the deck but not the doc → not done.
- A number in the doc that isn't produced by the pipeline → provenance violation; remove or trace it.
- Content in the doc that isn't in the deck → out of scope; the deck is the whole source.

## Output

- `manuscript/<Name>.docx` (built by the run script, from the template).
- The build script on disk (the reproducible artifact; the `CONTENT` list is the prose source of truth).
- An `EXHIBIT COVERAGE` line proving the gate passed.
