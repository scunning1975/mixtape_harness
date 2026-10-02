---
name: pipeline
description: Run the project's official pipeline end to end and report which exhibits are confirmed accurate, which changed (were inaccurate), and which are untouched (not produced by the pipeline). Use when the user says /pipeline, "run the pipeline", "run the official pipeline", or wants to verify the dashboard's exhibits before a talk or submission.
allowed-tools: Bash(python3 scripts/run_official_pipeline.py*), Read, Grep, Glob
---

# /pipeline — Run the official pipeline and verdict every exhibit

A narrow skill. It does ONE thing: run the single official pipeline
command, read the report it produces, and tell the researcher plainly
what is confirmed, what was inaccurate, and what is not covered.

## Convention (what makes this skill portable across projects)

The master pipeline file is ALWAYS `scripts/run_official_pipeline.py` at
the project root. That naming convention is the skill's only project
knowledge — same name in every GTD project, so this skill works anywhere
without configuration.

The file's contract: it fingerprints (SHA-256) every tracked artifact,
runs every official step from raw data, fingerprints again, and writes a
report to `audits/pipeline_runs/run_<stamp>.json` with a per-artifact
verdict:

- **confirmed** — byte-identical before and after: reproduced, not just fresh
- **changed** — the pipeline now produces something different: the prior
  version was inaccurate
- **missing** — existed before, not produced now: orphan
- **untouched** — on disk but no official step rewrote it: its generator
  is not in the pipeline (mtime unchanged, so identical bytes prove nothing)
- **new / regenerated / regenerated-identical** — bookkeeping for new
  artifacts and figures

If `scripts/run_official_pipeline.py` does not exist in this project,
STOP and say so. Offer to create one following the reference
implementation in one of your existing projects, but do not
improvise: the researcher decides what counts as official.

## Steps

0. **Tell the user how long it will take, before running.** Read the
   newest report in `audits/pipeline_runs/` and quote its
   `total_seconds`: "The last full run took 1m 5s — expect about that."
   If no report exists, say this is the first run and the duration is
   unknown.

1. **Run it** (from the project root):

   ```
   python3 scripts/run_official_pipeline.py
   ```

2. **Read the report** it just wrote — the newest file in
   `audits/pipeline_runs/`.

3. **Report back in plain language**, in this order:

   - **Steps**: did all stages run clean? If a stage failed, quote its log
     tail and STOP — nothing downstream of a failed stage is official, and
     the failure is the finding.
   - **CHANGED artifacts** (if any): these were inaccurate until this run.
     Name each file; if one feeds the manuscript or a deck, say so.
   - **MISSING artifacts** (if any): recommend cite-or-retire per artifact.
   - **UNTOUCHED artifacts** (if any): for each, identify its generator
     (grep the filename in code/ and scripts/) and ask the user whether to
     add that generator to the pipeline's `STEPS` list or retire the
     exhibit. Do not decide yourself — what counts as official is the
     researcher's call.
   - **Confirmed counts**: tables byte-identical, figures regenerated
     identical.

4. **The dashboard updates itself.** It reads the newest run report on
   every page load. Tell the user to refresh the browser; do not restart
   the server, do not edit the dashboard.

5. **If a sample-flow drift alarm was firing before the run**: the run
   wrote a new checkpoint, which acknowledges the current data state.
   Confirm in your report that the acknowledgment was intentional.

## What this skill must NOT do

- Do not edit any analysis script to "make the pipeline pass." A red
  verdict is information, never an inconvenience.
- Do not run individual stages selectively and call the result official.
  Official means the whole chain from raw data.
- Do not interpret results or update insights/hypotheses — that is
  analysis work, outside this skill's scope.
