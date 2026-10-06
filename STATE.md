# STATE: project working memory

**Last updated:** 2026-10-02 — *(full session logs in `audits/` when written)*

## CURRENT OBJECTIVE (2026-10-02)

Bite stage of `analyses/brazil_caps` (ACTIVE_STAGE = 02_bite): make a beautiful national-trend
figure of CAPS's effect on psychiatric admissions (`sih_tnet_F`) and schizophrenia admissions
(`sih_tnet_F_esquizofrenia`) over 2002–2016, then pipe it into the dashboard (Evidence→Figures,
Machinery→Code). Estimation is NOT yet in scope — these are descriptive bite figures.

## STATE OF MIND (2026-10-02)

Momentum session, Scott firing rapid context. Keeper-of-rules duty is live: Step 0 (package
preflight) and Step 1 (target estimand) are still OPEN — they gate the estimator, not these
figures, but must not be skipped before any att_gt call. Hard honesty line held: brazil.dta is
not on the machine, so no figure yet — never fabricate the data.

## Just completed (2026-10-02) — FIRST-DIFFERENCE STATE MAPS

- Built two choropleths (`scripts/r/02_bite_maps.R`): within-municipality first difference
  (mean post-g minus g−1 baseline, pop-weighted to state) for schizophrenia and all-MH admissions.
  Most states fell; RS/RR rose. Figures + script registered in FIGURE_SCRIPT_MAP + PIPELINE_SCRIPTS.
- KEY LIMITATION recorded: teaching brazil.dta has no municipality map key (cod is anonymized
  1..5476), so municipality-level choropleth is impossible → mapped at state level via `uf`.
  Upgrade needs the geocoded replication file (IBGE codes).
- geobr install was broken (duckdb dep timed out); used a states GeoJSON via sf instead
  (cached at data/derived/br_states.geojson).

## Earlier 2026-10-02 — BITE FIGURE BUILT + DASHBOARD WIRED

- Intaked real `brazil.dta` (82,140 × 117) → sealed `data/raw/`; inspected (vars are already per-10k rates).
- Built `output/figures/brazil_caps_bite.png` via `scripts/r/01_bite_national_trends.R`:
  population-weighted national trend of psych + schizophrenia admissions, 2002–2016 (both fall).
- Wired dashboard (`dashboard_server.py`): Figures tab now renders the gallery (was a placeholder);
  lightbox gets click-to-spin + F-fullscreen (added) alongside existing ←→/Esc; code viewer gets
  cool-color syntax highlighting (`hlCode`). Figure registered in FIGURE_SCRIPT_MAP.
- Scaffolded dirs + instantiated `analyses/brazil_caps/` (ACTIVE_STAGE = 02_bite); wrote theme + inspector.
- Recorded canister `findings.md` + `exhibits.md` for 02_bite.

## IN PROGRESS

- Bite figure DONE and live on the dashboard. Next natural step is the rollout/bite-vs-control
  view or moving toward Steps 0–1 before the estimator. Nothing half-done.

## NEXT SESSION — START HERE

1. Intake `brazil.dta` → `data/raw/` once Scott gives the path.
2. Run `scripts/r/00_bite_inspect.R`, LOOK at real columns; decide national quantity
   (population-weighted rate per 10k vs mean municipal rate — they differ; record the choice).
3. Write `scripts/r/01_bite_national_trends.R` → `output/figures/brazil_caps_bite.png` (+ PDF).
4. Pipe figure into dashboard (Evidence→Figures: click-to-spin, F fullscreen, ←/→ nav, Esc back)
   and code into Machinery→Code (scrollable, syntax-colored, show directory). Code review LATER.

## OPEN QUESTIONS / BLOCKERS

- (2026-10-02) **Where is `brazil.dta`?** Awaiting path — hard blocker; no figure until intaked.
- (2026-10-02) National quantity choice (pop-weighted vs mean municipal rate) — decide after inspection.
- (2026-10-02) Estimator CS-DiD is a candidate; confirm after Step 3 overlap/covariates.

## CANONICAL FILES

- `CLAUDE.md` — harness law. `MANIFESTO.md` — design-without-peeking principle.
- `analyses/brazil_caps/checklist.md` — DiD procedure (Step 0 pkg preflight + Step 1 target still OPEN/red).
- `scripts/r/_theme_bite.R`, `scripts/r/00_bite_inspect.R` — bite-stage code so far.
- `inspiration/REVIEW_Dias_Fontes.md` + `papers_build/split_dias.../summary_pp*.md` — paper notes.
- `dashboard_server.py` — live dashboard (localhost:8080); figure/code wiring pending.
