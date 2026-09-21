---
name: newproject
description: Scaffold a new research project with standard directory structure, CLAUDE.md template, and documented README. Use this at the start of every new project to ensure consistent organization.
allowed-tools: Bash(mkdir*), Bash(cp*), Bash(ls*), Write, Read
argument-hint: [project-name]
---

# New Project Scaffold

Create a new research project folder with Scott's standard structure. This skill is invoked at the start of every project.

## What Gets Created

```
[project-name]/
├── CLAUDE.md              # Permanent research rules (copied from template)
├── README.md              # Project-specific overview (auto-generated)
├── code/
│   ├── R/
│   ├── python/
│   └── stata/
├── data/
│   ├── raw/               # Original source data (never modify)
│   └── clean/             # Cleaned/merged datasets
├── output/
│   ├── tables/
│   └── figures/
├── documents/             # Outside PDFs, papers (use /split-pdf on these)
├── decks/                 # Beamer presentations (rhetoric of decks)
├── notes/                 # Scratch notes, random ideas, misc
└── progress_logs/         # Session continuity across Claude conversations
```

## Execution

1. **Get the project name** from the argument. If none provided, ask.
   - Convert spaces to hyphens, lowercase

2. **Determine location** — default is current working directory. Confirm if unclear.

3. **Create all directories — including the full harness architecture:**
   ```bash
   # base research layout
   mkdir -p [project-name]/{code/{R,stata,python},data/{raw,clean,derived},output/{figures,tables},documents,decks/html,notes,progress_logs}
   # harness: checklists, per-analysis canisters, audits, working memory
   mkdir -p [project-name]/{checklists,audits,scratch,cards,decisions,insights,correspondence/referee2,analyses/_template}
   ```

3b. **Scaffold the harness (copy from the GTD template — this is what makes it a harness, not just folders):**
   ```bash
   GTD=~/Documents/gtd
   cp $GTD/checklists/*.md                 [project-name]/checklists/
   cp -r $GTD/analyses/_template/*         [project-name]/analyses/_template/   # incl. stages/<NN>/{ideas,todo,findings,exhibits}.md canister skeleton + ACTIVE_STAGE.example
   cp $GTD/dashboard_server.py             [project-name]/
   cp $GTD/scripts/r/_ledger.R $GTD/scripts/r/_manifest.R       [project-name]/code/R/   2>/dev/null || true
   cp $GTD/scripts/python/{_manifest.py,make_sample_flow.py,pdf_deck_to_html.py} [project-name]/code/python/ 2>/dev/null || true
   cp $GTD/scripts/run_official_pipeline.py [project-name]/scripts/ 2>/dev/null || true
   cp $GTD/decks/html/README.md            [project-name]/decks/html/
   cp -r $GTD/quotes $GTD/reorient         [project-name]/ 2>/dev/null || true
   ```
   The point: a new project is **born with the harness** — the canister skeleton, the checklist, the dashboard, the ledger/manifest helpers — not a bare folder tree. The researcher fills content; the architecture is already there.

4. **Copy CLAUDE.md** from `~/Documents/gtd/CLAUDE.md` (the canonical harness CLAUDE.md, NOT a bare template — it carries the rules of law: keeper-of-the-rules, Checklist Stages Are Canisters, Plain Language, Zero Error, STATE.md discipline):
   - Replace `[Your Name]` with `Scott`
   - Update the project-overview / research-question sections for the new project; leave every rules-of-law section verbatim.
   - Create `STATE.md` at the root from the structure in the GTD template.

5. **Generate README.md** with:
   - Project title
   - Visual directory tree in a fenced code block (monospace)
   - Explanation of each folder's purpose
   - Note that CLAUDE.md is copied from a permanent template and edited per-project
   - Note that README.md is for project-specific documentation
   - Note that progress_logs/ maintains continuity across Claude sessions
   - Placeholder sections: Overview, Collaborators, Status, Key Files

   The README must include this tree block:

   ````markdown
   ```
   [project-name]/
   ├── CLAUDE.md              # Research rules & estimation philosophy (permanent)
   ├── README.md              # This file — project-specific notes
   ├── code/
   │   ├── R/                 # R scripts
   │   ├── python/            # Python scripts
   │   └── stata/             # Stata do-files
   ├── data/
   │   ├── raw/               # Original source data (never modify these)
   │   └── clean/             # Cleaned and merged datasets
   ├── output/
   │   ├── tables/            # Generated tables (LaTeX, CSV)
   │   └── figures/           # Generated figures (PDF, PNG)
   ├── documents/             # Outside papers and PDFs (split with /split-pdf)
   ├── decks/                 # Beamer presentations (rhetoric of decks philosophy)
   ├── notes/                 # Scratch notes, ideas, miscellaneous
   └── progress_logs/         # Session logs for continuity across Claude conversations
   ```
   ````

6. **Create initial progress log** at `progress_logs/YYYY-MM-DD_setup.md`:
   - Record the creation date
   - List next steps as a checklist

7. **Report success** — show structure with `ls`, remind user to update CLAUDE.md.
