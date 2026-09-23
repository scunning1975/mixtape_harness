#!/usr/bin/env python3
"""
dashboard_server.py — Live research dashboard. Reads filesystem on every request.
No build step, no stale JSON. Always current.

Run: python3 dashboard_server.py
Open: http://localhost:8080/
"""

import http.server
import socketserver
import os
import random
import re
import time
import json as json_top
import subprocess
import html as html_mod
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse, parse_qs

ROOT = Path(os.getcwd())
PORT = int(os.environ.get("PORT", 8080))

# =============================================================================
# FROZEN STRUCTURE
# =============================================================================

PIPELINE_SCRIPTS = [
    {"script": "scripts/python/00_clean_source.py", "outputs": ["data/clean/source_clean.csv"], "level": 1, "name": "Clean source"},
    {"script": "scripts/python/01_build_outcome.py", "outputs": ["data/clean/outcome_county_month.csv"], "level": 1, "name": "Build outcome panel"},
    {"script": "scripts/python/02_build_covariates.py", "outputs": ["data/derived/county_covariates_static.csv"], "level": 2, "name": "Covariates"},
    {"script": "scripts/python/03_descriptive.py", "outputs": ["output/figures/treatment_timeline.png", "output/figures/sample_map.png"], "level": 4, "name": "Stage 1 descriptive (bite)"},
    {"script": "scripts/r/30_build_gvar.R", "outputs": ["data/derived/gvar_county.csv"], "level": 5, "name": "Build cohort gvar"},
    {"script": "scripts/r/30b_build_panel_clean.R", "outputs": ["data/derived/panel_clean.csv"], "level": 5, "name": "Build clean panel (main)"},
    {"script": "scripts/r/30c_build_panel_falsif.R", "outputs": ["data/derived/panel_falsif.csv"], "level": 5, "name": "Build falsification panel"},
    {"script": "scripts/r/31_csdid_main.R", "outputs": ["output/figures/csdid_event_study_main.png", "output/tables/csdid_main_results.csv", "output/tables/csdid_main_aggregates.tex", "output/figures/rollout_panelview.png", "output/figures/outcome_by_cohort.png", "output/tables/balance_main.tex", "output/tables/cohort_rollout.tex", "output/figures/pscore_main.png"], "level": 5, "name": "CS-DiD (staggered, main)"},
    {"script": "scripts/r/32_csdid_falsif.R", "outputs": ["output/figures/csdid_event_study_falsif.png", "output/tables/csdid_falsif_results.csv", "output/tables/csdid_falsif_aggregates.tex"], "level": 5, "name": "CS-DiD (falsification)"},
]

FIGURE_SCRIPT_MAP = {
    # Stage 1 descriptive (bite) -- scripts/python/03_descriptive.py
    "treatment_timeline":            "scripts/python/03_descriptive.py",
    "sample_map":                    "scripts/python/03_descriptive.py",
    # causal layer (staggered Callaway-Sant'Anna)
    "csdid_event_study_main":        "scripts/r/31_csdid_main.R",
    "csdid_event_study_falsif":      "scripts/r/32_csdid_falsif.R",
    "rollout_panelview":             "scripts/r/31_csdid_main.R",
    "outcome_by_cohort":             "scripts/r/31_csdid_main.R",
    "pscore_main":                   "scripts/r/31_csdid_main.R",
}

COURTROOM_STAGES = [
    {"num": 1, "label": "Show Bite", "desc": "The event was real. Maps, volume, timeline.",
     "keywords": ["timeline", "geographic", "rollout", "show bite", "treatment_timeline", "sample_map"]},
    {"num": 2, "label": "The Design", "desc": "Who is treated, who is control, are they comparable? Balance, overlap, pre-trends, target parameter.",
     "keywords": ["design", "target parameter", "balance table", "propensity score", "overlap plot", "common support", "treatment group", "control group"]},
    {"num": 3, "label": "Event Studies", "desc": "Dynamic effects. Pre-treatment coefficients = 0.",
     "keywords": ["event study", "csdid_event_study", "dynamic", "callaway-sant'anna"]},
    {"num": 4, "label": "Falsification", "desc": "Placebo period must find nothing.",
     "keywords": ["falsification", "placebo", "null"]},
    {"num": 5, "label": "Main Results", "desc": "Headline ATT estimates.",
     "keywords": ["att", "main result", "aggregates"]},
    {"num": 6, "label": "Mechanisms", "desc": "Heterogeneity, channels, selection theory.",
     "keywords": ["mechanism", "heterogeneity", "lasso", "prediction", "floor", "selection"]},
]

COURTROOM_FIGURE_MAP = {
    1: ["output/figures/treatment_timeline.png",
        "output/figures/sample_map.png"],
    2: ["output/figures/pscore_main.png",
        "output/figures/rollout_panelview.png"],
    3: ["output/figures/csdid_event_study_main.png",
        "output/figures/outcome_by_cohort.png"],
    4: ["output/figures/csdid_event_study_falsif.png"],
    5: ["output/figures/csdid_event_study_main.png"],
    6: [],
}

COURTROOM_HYPOTHESES = {
    1: [],
    2: [],
    3: [],
    4: [],
    5: [],
    6: [],
}

# Canonical DiD checklist (matches checklists/did_checklist.md, 0–11 + Step 2 "Bite").
# TEMPLATE version: `expected` exhibit paths are blank — each project fills them in
# its analyses/<slug> instance. Numbers track checklists/did_checklist.md 1:1.
CHECKLIST_STEPS = [
    {"num": 0, "name": "Package preflight", "desc": "Eyeball every estimator's version (Gawande pause)", "expected": []},
    {"num": 1, "name": "Target parameter", "desc": "Define the estimand + weighting", "expected": []},
    {"num": 2, "name": "Bite (assignment mechanism)", "desc": "Document treatment, first-stage, & who gets treated → deduce selection", "expected": []},
    {"num": 3, "name": "Covariates", "desc": "X that drive Y(0) trends (/covariates), informed by the bite", "expected": []},
    {"num": 4, "name": "Balance & overlap", "desc": "Std. diff table + propensity common support", "expected": []},
    {"num": 5, "name": "Treatment rollout", "desc": "panelview of who is treated when", "expected": []},
    {"num": 6, "name": "Outcomes by cohort", "desc": "Average outcome over time by cohort (pre-trends by eye)", "expected": []},
    {"num": 7, "name": "Sample sizes", "desc": "Treated / control / dropped — every drop named", "expected": []},
    {"num": 8, "name": "Estimator (gate)", "desc": "Choose the estimator; version preflight passes before it runs", "expected": []},
    {"num": 9, "name": "Estimation + event study", "desc": "ATT(s) + dynamic figure", "expected": []},
    {"num": 10, "name": "Falsification", "desc": "Placebo (group/outcome/period), 10a-10d", "expected": []},
    {"num": 11, "name": "Debug fallback", "desc": "Version check first if estimator misbehaves", "expected": []},
]

# =============================================================================
# SCANNING FUNCTIONS
# =============================================================================

def parse_frontmatter(filepath):
    text = filepath.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    fm = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            val = val.strip()
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            elif val.lower() == "null":
                val = None
            elif val.lower() in ("true", "false"):
                val = val.lower() == "true"
            fm[key.strip()] = val
    return fm, parts[2].strip()


def scan_hypotheses():
    hyp_dir = ROOT / "hypotheses"
    if not hyp_dir.exists():
        return []
    results = []
    for f in sorted(hyp_dir.glob("H*.md")):
        fm, body = parse_frontmatter(f)
        if not fm.get("id"):
            continue
        claim, kills, evidence = "", "", []
        for section in body.split("##"):
            s = section.strip()
            if s.startswith("Claim"):
                claim = "\n".join(s.split("\n")[1:]).strip()
            elif s.startswith("Kills"):
                kills = "\n".join(s.split("\n")[1:]).strip()
            elif s.startswith("Evidence"):
                evidence = [l.strip() for l in s.split("\n")[1:] if l.strip().startswith("-")]
        results.append({
            "id": fm.get("id"), "title": fm.get("title", ""),
            "status": fm.get("status", "conjecture"), "parent": fm.get("parent"),
            "children": fm.get("children", []),
            "claim": claim, "kills_it": kills, "evidence": evidence,
            "body": body, "file": str(f.relative_to(ROOT)),
        })
    return results


def scan_insights():
    ins_dir = ROOT / "insights"
    if not ins_dir.exists():
        return []
    results = []
    for f in sorted(ins_dir.glob("2*.md")):
        fm, body = parse_frontmatter(f)
        if not fm.get("date"):
            continue
        finding = ""
        for section in body.split("##"):
            s = section.strip()
            if s.startswith("Finding"):
                finding = "\n".join(s.split("\n")[1:]).strip()
        results.append({
            "date": fm.get("date"), "title": fm.get("title", ""),
            "updates": fm.get("updates", ""), "result": fm.get("result", ""),
            "script": fm.get("script", ""), "output": fm.get("output", ""),
            "stage": fm.get("stage", None),
            "finding": finding, "file": str(f.relative_to(ROOT)),
        })
    return sorted(results, key=lambda x: x["date"], reverse=True)


def scan_decisions():
    idx = ROOT / "decisions" / "INDEX.md"
    if not idx.exists():
        return []
    results = []
    for line in idx.read_text().split("\n"):
        if line.startswith("|") and "---" not in line and "ID" not in line:
            cols = [c.strip() for c in line.split("|")[1:-1]]
            if len(cols) >= 4:
                results.append({"id": cols[0], "decision": cols[1], "date": cols[2], "rationale": cols[3]})
    return results


def scan_pipeline():
    results = []
    for entry in PIPELINE_SCRIPTS:
        sp = ROOT / entry["script"]
        sp_mtime = sp.stat().st_mtime if sp.exists() else 0
        outputs = []
        all_fresh = True
        for out in entry["outputs"]:
            op = ROOT / out
            if not op.exists():
                outputs.append({"path": out, "fresh": False, "status": "missing"})
                all_fresh = False
            elif op.stat().st_mtime >= sp_mtime:
                outputs.append({"path": out, "fresh": True, "status": "fresh"})
            else:
                outputs.append({"path": out, "fresh": False, "status": "stale"})
                all_fresh = False
        results.append({**entry, "exists": sp.exists(), "all_fresh": all_fresh, "outputs": outputs,
                        "mtime": datetime.fromtimestamp(sp_mtime).strftime("%Y-%m-%d %H:%M") if sp.exists() else None})
    return results


def scan_figures():
    fig_dir = ROOT / "output" / "figures"
    if not fig_dir.exists():
        return []
    results = []
    for f in sorted(fig_dir.glob("*.png")):
        stem = f.stem
        script = FIGURE_SCRIPT_MAP.get(stem)
        sp = ROOT / script if script and script != "ad-hoc" else None
        fresh = None
        if sp and sp.exists():
            fresh = f.stat().st_mtime >= sp.stat().st_mtime
        results.append({
            "name": stem, "path": str(f.relative_to(ROOT)),
            "mtime": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
            "script": script, "fresh": fresh, "orphaned": script is None,
        })
    return results


def scan_code_files():
    files = []
    for d in ["scripts/python", "scripts/r"]:
        p = ROOT / d
        if p.exists():
            for f in sorted(p.iterdir()):
                if f.suffix in (".py", ".R", ".r"):
                    files.append(str(f.relative_to(ROOT)))
    return files


DATA_CATALOG = [
    # Template: one entry per raw data source. Fill per project.
    # {"name": "<source>", "desc": "<what it is, coverage, size>",
    #  "paths": ["data/raw/<file>"], "source": "<provenance>",
    #  "collected": "<range>", "used_by_scripts": ["scripts/..."]},
]


def scan_data():
    """Catalog raw data sources with auto-detected usage and previews."""
    results = []
    for entry in DATA_CATALOG:
        paths = entry["paths"]
        # Check existence — support glob patterns
        existing_files = []
        total_size = 0
        for p in paths:
            if "*" in p:
                existing_files.extend(ROOT.glob(p))
            else:
                fp = ROOT / p
                if fp.exists():
                    existing_files.append(fp)
        for fp in existing_files:
            total_size += fp.stat().st_size

        # Get a preview from the first CSV
        preview = None
        for fp in existing_files:
            if fp.suffix == ".csv" and fp.stat().st_size < 500_000_000:
                try:
                    with open(fp, "r", encoding="utf-8", errors="ignore") as fh:
                        lines = []
                        for i, line in enumerate(fh):
                            if i >= 4:
                                break
                            lines.append(line.rstrip())
                        preview = lines
                except Exception:
                    pass
                break

        # Trace to figures
        figures = []
        for script in entry["used_by_scripts"]:
            for fig_stem, fig_script in FIGURE_SCRIPT_MAP.items():
                if fig_script == script:
                    fig_path = f"output/figures/{fig_stem}.png"
                    if (ROOT / fig_path).exists():
                        figures.append(fig_path)

        size_str = f"{total_size/1024/1024:.0f} MB" if total_size > 1024*1024 else f"{total_size/1024:.0f} KB"
        results.append({
            "name": entry["name"],
            "desc": entry["desc"],
            "source": entry["source"],
            "collected": entry["collected"],
            "paths": paths,
            "n_files": len(existing_files),
            "exists": len(existing_files) > 0,
            "size": size_str if existing_files else None,
            "used_by": entry["used_by_scripts"],
            "figures": figures,
            "preview": preview,
        })
    return results


def map_insight_to_stages(insight):
    """Map an insight to courtroom stages. Uses explicit stage: field if present, otherwise keywords."""
    # Check for explicit stage field in frontmatter
    if "stage" in insight and insight["stage"]:
        s = insight["stage"]
        if isinstance(s, list):
            return [int(x) for x in s]
        elif isinstance(s, str) and s.startswith("["):
            return [int(x.strip()) for x in s.strip("[]").split(",") if x.strip()]
        else:
            try:
                return [int(s)]
            except (ValueError, TypeError):
                pass
    # Fallback: keyword matching
    title_lower = insight["title"].lower()
    matched = []
    for stage in COURTROOM_STAGES:
        for kw in stage["keywords"]:
            if kw in title_lower:
                matched.append(stage["num"])
                break
    return matched if matched else []


def mini_md(text):
    if not text:
        return ""
    text = html_mod.escape(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'^# (.+)$', r'', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
    text = re.sub(r'(<li>.*?</li>(\n|$))+', lambda m: '<ul>' + m.group(0) + '</ul>', text)
    # Convert [Figure: name] to clickable lightbox links
    def _fig_link(m):
        name = m.group(1)
        return f'<a class="fig-link" onclick="event.preventDefault();showLightbox(&apos;/output/figures/{name}.png&apos;,&apos;{name}&apos;)">📊 {name}</a>'
    text = re.sub(r'\[Figure: ([^\]]+)\]', _fig_link, text)
    # Convert [Table: name] to clickable links
    def _tbl_link(m):
        name = m.group(1)
        return f'<a class="fig-link" onclick="show(&apos;tables&apos;);setTimeout(()=>document.getElementById(&apos;tbl-{name}&apos;)?.scrollIntoView({{behavior:&apos;smooth&apos;}}),100)">📋 {name}</a>'
    text = re.sub(r'\[Table: ([^\]]+)\]', _tbl_link, text)
    text = text.replace("\n\n", "</p><p>").replace("\n", "<br>")
    return f"<p>{text}</p>"


# =============================================================================
# HTML RENDERING
# =============================================================================

def scan_inbox():
    """Read inbox items (unprocessed captures)."""
    inbox_dir = ROOT / "inbox"
    if not inbox_dir.exists():
        return []
    results = []
    for f in sorted(inbox_dir.glob("*.md")):
        fm, body = parse_frontmatter(f)
        action = ""
        for line in body.split("\n"):
            if line.strip().startswith("**Action needed:**"):
                action = line.strip().replace("**Action needed:**", "").strip()
        results.append({
            "file": f.name,
            "captured": fm.get("captured", ""),
            "from": fm.get("from", ""),
            "body": body.split("\n")[0] if body else "",
            "action": action,
        })
    return results


def scan_someday():
    """Read someday/maybe items."""
    sd_dir = ROOT / "someday"
    if not sd_dir.exists():
        return []
    results = []
    for f in sorted(sd_dir.glob("*.md")):
        fm, body = parse_frontmatter(f)
        results.append({
            "file": f.name,
            "captured": fm.get("captured", ""),
            "body": body.split("\n")[0] if body else "",
        })
    return results


def scan_audits():
    """Read audit records from audits/ directory."""
    audit_dir = ROOT / "audits"
    if not audit_dir.exists():
        return []
    results = []
    for f in sorted(audit_dir.glob("2*.md"), reverse=True):
        fm, body = parse_frontmatter(f)
        if not fm.get("date"):
            continue
        summary = ""
        for section in body.split("##"):
            s = section.strip()
            if s.startswith("Summary"):
                summary = "\n".join(s.split("\n")[1:]).strip()
        results.append({
            "date": fm.get("date"), "topic": fm.get("topic", ""),
            "conclusion": fm.get("conclusion", ""),
            "actions": fm.get("actions", ""),
            "narrative_updated": fm.get("narrative_updated", False),
            "summary": summary, "file": str(f.relative_to(ROOT)),
        })
    return results[:10]


def render_status(hypotheses, insights, pipeline):
    counts = {}
    for h in hypotheses:
        s = h["status"]
        counts[s] = counts.get(s, 0) + 1
    stale = sum(1 for p in pipeline if not p["all_fresh"])
    latest = insights[0] if insights else None
    audits = scan_audits()
    inbox = scan_inbox()
    someday = scan_someday()

    # Next actions
    next_actions_html = ""
    na_file = ROOT / "NEXT_ACTIONS.md"
    if na_file.exists():
        na_content = na_file.read_text().strip()
        lines = [l.strip() for l in na_content.split("\n") if l.strip() and not l.startswith("#")]
        if lines:
            items = "".join(f'<li>{html_mod.escape(l.lstrip("0123456789. "))}</li>' for l in lines)
            next_actions_html = f'<div class="card"><h3>Next Actions</h3><ol class="next-actions">{items}</ol></div>'

    # Inbox section
    inbox_html = ""
    if inbox:
        inbox_html = f'<div class="card"><h3>Inbox ({len(inbox)} items)</h3><p style="color:var(--muted);font-size:0.7rem;margin-bottom:0.5rem;">Unprocessed. Triage during <code>/gtd audit</code>.</p>'
        for item in inbox:
            inbox_html += f'<div class="inbox-item"><div class="inbox-header"><span class="inbox-from">{html_mod.escape(item["from"])}</span><span class="date">{item["captured"]}</span></div><div class="inbox-body">{html_mod.escape(item["body"])}</div>'
            if item["action"]:
                inbox_html += f'<div class="inbox-action">{html_mod.escape(item["action"])}</div>'
            inbox_html += '</div>'
        inbox_html += '</div>'
    else:
        inbox_html = '<div class="card"><h3>Inbox</h3><p style="color:var(--green);font-size:0.8rem;">Empty. All items triaged.</p></div>'

    # Someday section
    someday_html = ""
    if someday:
        someday_html = f'<div class="card"><h3>Someday / Maybe ({len(someday)})</h3>'
        for item in someday:
            someday_html += f'<div class="someday-item">{html_mod.escape(item["body"])}</div>'
        someday_html += '</div>'

    audits_html = ""
    if audits:
        audits_html = '<div class="card"><h3>Recent Audits</h3>'
        for a in audits[:5]:
            audits_html += f"""<div class="audit-card" onclick="this.querySelector('.audit-body').classList.toggle('open')">
              <div class="audit-header"><span class="audit-topic">{html_mod.escape(a['topic'])}</span><span class="date">{a['date']}</span></div>
              <div class="audit-conclusion">{html_mod.escape(a['conclusion'])}</div>
              <div class="audit-body"><p>{html_mod.escape(a['summary'][:300])}</p>{('<span class="badge confirmed">narrative updated</span>' if a['narrative_updated'] else '')}</div>
            </div>"""
        audits_html += '</div>'
    else:
        audits_html = '<div class="card"><h3>Recent Audits</h3><p class="empty">No audits yet. Run <code>/gtd audit [topic]</code> to start.</p></div>'

    return f"""
    <div class="status-grid">
      <div class="stat"><div class="stat-val">{len(hypotheses)}</div><div class="stat-lbl">Hypotheses</div></div>
      <div class="stat"><div class="stat-val green">{counts.get('confirmed',0)}</div><div class="stat-lbl">Confirmed</div></div>
      <div class="stat"><div class="stat-val yellow">{counts.get('testing',0)}</div><div class="stat-lbl">Testing</div></div>
      <div class="stat"><div class="stat-val red">{counts.get('complicated',0)}</div><div class="stat-lbl">Complicated</div></div>
      <div class="stat"><div class="stat-val">{len(pipeline)-stale}/{len(pipeline)}</div><div class="stat-lbl">Pipeline Fresh</div></div>
      <div class="stat"><div class="stat-val">{len(insights)}</div><div class="stat-lbl">Insights</div></div>
    </div>
    {'<div class="card"><h3>Latest Insight</h3><div class="insight-date">'+latest["date"]+'</div><strong>'+html_mod.escape(latest["title"])+'</strong> <span class="badge '+latest["result"]+'">'+latest["result"]+'</span><p class="finding">'+html_mod.escape(latest["finding"][:200])+'</p></div>' if latest else ''}
    {next_actions_html}
    {inbox_html}
    {audits_html}
    {someday_html}
    """


def render_courtroom(insights, figures):
    staged = {s["num"]: [] for s in COURTROOM_STAGES}
    for ins in insights:
        for snum in map_insight_to_stages(ins):
            staged[snum].append(ins)

    # Use direct figure map + supplement from insights
    stage_figures = {s["num"]: list(COURTROOM_FIGURE_MAP.get(s["num"], [])) for s in COURTROOM_STAGES}
    for ins in insights:
        output = ins.get("output", "")
        if output and output.endswith(".png") and "figures" in output:
            for snum in map_insight_to_stages(ins):
                if output not in stage_figures[snum]:
                    stage_figures[snum].append(output)

    # Determine which hypotheses have complicated evidence in Stage 3 (falsification)
    falsification_compromised = set()
    for e in staged.get(3, []):
        if e["result"] == "complicated" and e.get("updates"):
            falsification_compromised.add(e["updates"])

    # Build hypothesis status lookup
    hyp_statuses = {}
    for ins in insights:
        hid = ins.get("updates", "")
        if hid:
            hyp_statuses[hid] = ins.get("result", "testing")
    # Also check hypothesis files
    hyp_dir = ROOT / "hypotheses"
    if hyp_dir.exists():
        for hf in hyp_dir.glob("*.md"):
            fm, _ = parse_frontmatter(hf)
            if fm.get("id"):
                hyp_statuses[fm["id"]] = fm.get("status", "testing")

    html = ""
    for stage in COURTROOM_STAGES:
        evidence = staged[stage["num"]]
        status = "done" if evidence else "todo"
        for e in evidence:
            if e["result"] == "complicated":
                status = "partial"
                break

        # Render evidence items, flagging contested ones in Stage 4+
        evidence_html = ""
        if evidence:
            for e in evidence:
                contested = ""
                if stage["num"] >= 4 and e.get("updates") in falsification_compromised and e["result"] != "complicated":
                    contested = ' <span class="badge-contested">contested by falsification</span>'
                evidence_html += f'<div class="court-evidence"><span class="badge {e["result"]}">{e["result"]}</span> {html_mod.escape(e["title"])}{contested} <span class="date">({e["date"]})</span></div>'
        else:
            evidence_html = '<div class="court-empty">No evidence filed yet</div>'

        # Hypothesis badges for this stage
        hyp_html = ""
        stage_hyps = COURTROOM_HYPOTHESES.get(stage["num"], [])
        if stage_hyps:
            hyp_html = '<div class="court-hyps">'
            for hid, hlabel in stage_hyps:
                hstatus = hyp_statuses.get(hid, "testing")
                hyp_html += f'<span class="court-hyp-badge {hstatus}" title="{hid}: {hlabel}">{hid} <span class="badge {hstatus}">{hstatus}</span></span>'
            hyp_html += '</div>'

        # Figure thumbnails for this stage — lightbox on click (courtroom-scoped, arrow-key navigable)
        figs_for_stage = stage_figures.get(stage["num"], [])
        figs_html = ""
        if figs_for_stage:
            figs_html = '<div class="court-figures">'
            for fig_path in figs_for_stage:
                if not (ROOT / fig_path).exists():
                    continue
                fig_name = Path(fig_path).stem
                figs_html += f'<img class="court-thumb" data-court-src="/{fig_path}" data-court-name="{fig_name}" src="/{fig_path}" title="{fig_name}" onclick="event.stopPropagation();showCourtroomLightbox(this)">'
            figs_html += '</div>'

        html += f"""
        <div class="court-stage">
          <div class="court-num {status}">{stage['num']}</div>
          <div class="court-content">
            <div class="court-label">{stage['label']}</div>
            <div class="court-desc">{stage['desc']}</div>
            {hyp_html}
            {evidence_html}
            {figs_html}
          </div>
        </div>"""
    return html


def render_checklist():
    html = ""
    for step in CHECKLIST_STEPS:
        if not step["expected"]:
            status = "pending"
        elif all((ROOT / e).exists() for e in step["expected"]):
            status = "done"
        elif any((ROOT / e).exists() for e in step["expected"]):
            status = "partial"
        else:
            status = "missing"
        html += f"""
        <div class="check-step">
          <div class="check-num {status}">{step['num']}</div>
          <div class="check-content">
            <div class="check-name">{step['name']}</div>
            <div class="check-desc">{step['desc']}</div>
            {''.join('<div class="check-file '+('exists' if (ROOT/e).exists() else 'missing')+'">'+e+'</div>' for e in step["expected"])}
          </div>
        </div>"""
    return html


# =============================================================================
# Per-analysis checklist scan + render — the harness's first-class surface.
# Reads every analyses/<slug>/checklist.md, parses frontmatter (with PyYAML so
# nested package blocks work), counts step deliverables and checkbox state,
# and emits (a) a grid (rows = analyses, cols = steps 0-10 + Sign-off),
# (b) flippable package cards from the union of every analysis's packages.
# =============================================================================

ANALYSIS_STEPS = [
    {"num": "0",  "label": "Pkg",       "title": "Package preflight"},
    {"num": "1",  "label": "Target",    "title": "Pre-registration / target parameter"},
    {"num": "2",  "label": "Bite",      "title": "Bite — treatment + assignment mechanism (deduce selection)"},
    {"num": "3",  "label": "X",         "title": "Covariates + EPV check"},
    {"num": "4",  "label": "Balance",   "title": "Balance and overlap"},
    {"num": "5",  "label": "Rollout",   "title": "Treatment visualization"},
    {"num": "6",  "label": "Outcome",   "title": "Outcome over time"},
    {"num": "7",  "label": "N",         "title": "Sample sizes"},
    {"num": "8",  "label": "Estimator", "title": "Estimator (gate)"},
    {"num": "9",  "label": "Event",     "title": "Estimation + event study"},
    {"num": "10", "label": "Falsify",   "title": "Falsification (10a-10d)"},
    {"num": "11", "label": "Debug",     "title": "Estimator-misbehaves fallback"},
    {"num": "S",  "label": "Sign",      "title": "Sign-off (manifest.yaml)"},
]


def _parse_yaml_frontmatter(filepath):
    """Like parse_frontmatter but uses PyYAML to handle nested structures."""
    try:
        import yaml as _yaml
    except ImportError:
        return {}, filepath.read_text(encoding="utf-8", errors="ignore")
    text = filepath.read_text(encoding="utf-8", errors="ignore")
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    try:
        fm = _yaml.safe_load(parts[1]) or {}
    except Exception:
        fm = {}
    return fm, parts[2]


def _extract_section(body, heading_prefix):
    """Return the body of the section starting with heading_prefix, ending at
    the next ## heading or EOF. None if heading_prefix is not present."""
    if heading_prefix not in body:
        return None
    start = body.index(heading_prefix)
    rest = body[start:]
    next_match = re.search(r"\n## ", rest[len(heading_prefix):])
    if next_match:
        return rest[: len(heading_prefix) + next_match.start()]
    return rest


def _grade_step(body, step_num):
    """Return 'done' | 'partial' | 'missing' | 'pending' for a step section.
    Heuristic: count checkboxes ticked, count deliverable paths existing."""
    if step_num == "S":
        section = _extract_section(body, "## Sign-off")
    else:
        section = _extract_section(body, f"## {step_num}.")
    if section is None:
        return "pending"

    boxes_checked = section.count("- [x]") + section.count("- [X]")
    boxes_total = boxes_checked + section.count("- [ ]")

    paths = []
    for token in re.findall(r"`([a-zA-Z0-9_./<>\-]+\.(?:png|pdf|tex|csv|md|yaml|R|py))`", section):
        if "<" in token or ">" in token:
            continue  # placeholder
        paths.append(token)
    paths_total = len(paths)
    paths_exist = sum(1 for p in paths if (ROOT / p).exists())

    if boxes_total == 0 and paths_total == 0:
        return "pending"
    box_done = (boxes_total > 0 and boxes_checked == boxes_total)
    path_done = (paths_total > 0 and paths_exist == paths_total)
    if (boxes_total > 0 and box_done) and (paths_total == 0 or path_done):
        return "done"
    if (paths_total > 0 and path_done) and boxes_total == 0:
        return "done"
    if boxes_checked > 0 or paths_exist > 0:
        return "partial"
    return "missing"


def _stage_folder(slug_dir, step_num):
    """The stage-canister folder for a step, matched by numeric prefix ('5'->'05_*', '10'->'10_*', 'D'->'D_*')."""
    stages_dir = slug_dir / "stages"
    if not stages_dir.exists():
        return None
    prefix = step_num.zfill(2) if step_num.isdigit() else step_num
    for d in stages_dir.iterdir():
        if d.is_dir() and (d.name == prefix or d.name.startswith(prefix + "_")):
            return d
    return None


def _active_stage_folder(slug_dir):
    """The one folder name ACTIVE_STAGE points at (the 'You Are Here' room), or '' if none."""
    f = slug_dir / "ACTIVE_STAGE"
    return f.read_text().strip() if f.exists() else ""


def scan_analyses():
    """Read every analyses/<slug>/checklist.md and return one dict per slug."""
    out = []
    a_dir = ROOT / "analyses"
    if not a_dir.exists():
        return out
    for sub in sorted(a_dir.iterdir()):
        if not sub.is_dir() or sub.name.startswith("_") or sub.name.startswith("."):
            continue
        chk = sub / "checklist.md"
        if not chk.exists():
            continue
        fm, body = _parse_yaml_frontmatter(chk)
        active = _active_stage_folder(sub)
        # THREE-COLOR "You Are Here" model: a stage cell is OPEN or SHUT, plus one marker for where you are —
        # like a mall map. The box-grade muddle (partial/missing/pending) collapses:
        #   GREEN 'done'   = stage carries a LOCKED file (shut / signed off)
        #   AMBER 'active' = this is the ACTIVE_STAGE ("You Are Here") — the ONE room you're in
        #   RED   'open'   = everything else (not locked, not the active room)
        # Only ONE amber can exist (ACTIVE_STAGE names exactly one folder). To move on: LOCK the room you're
        # leaving + point ACTIVE_STAGE at the next → the amber dot moves, the one behind turns green. The rule
        # 'a stage's color IS its lock state' governs every stage, including the final Sign-off stage.
        steps = {}
        for s in ANALYSIS_STEPS:
            folder = _stage_folder(sub, s["num"])
            if folder is None:
                steps[s["num"]] = _grade_step(body, s["num"])   # no canister → fall back to grade
                continue
            if folder.name == active:
                steps[s["num"]] = "active"      # You Are Here (amber)
            elif (folder / "LOCKED").exists():
                steps[s["num"]] = "done"        # shut (green)
            else:
                steps[s["num"]] = "open"        # open (red)
        try:
            mtime = datetime.fromtimestamp(chk.stat().st_mtime).strftime("%Y-%m-%d")
        except Exception:
            mtime = ""
        manifest_exists = (sub / "manifest.yaml").exists()
        out.append({
            "slug": sub.name,
            "path": str(chk.relative_to(ROOT)),
            "fm": fm if isinstance(fm, dict) else {},
            "steps": steps,
            "packages": (fm.get("packages") if isinstance(fm, dict) else None) or [],
            "manifest_exists": manifest_exists,
            "mtime": mtime,
        })
    return out


def _query_installed_pkg_version(pkg_name):
    """Best-effort live query of installed R package version. Cached per process."""
    cache = getattr(_query_installed_pkg_version, "_cache", None)
    if cache is None:
        cache = {}
        _query_installed_pkg_version._cache = cache
    if pkg_name in cache:
        return cache[pkg_name]
    try:
        import subprocess
        result = subprocess.run(
            ["Rscript", "-e", f"cat(as.character(packageVersion('{pkg_name}')))"],
            capture_output=True, text=True, timeout=8,
        )
        cache[pkg_name] = result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        cache[pkg_name] = None
    return cache[pkg_name]


def _compare_versions(installed, required):
    """Compare installed vs required (e.g. '>= 2.3.1'). Returns 'green'|'red'|'unknown'."""
    if not installed or not required:
        return "unknown"
    m = re.match(r"\s*(>=|>|=|==|<=|<)\s*(.+)\s*", str(required))
    if not m:
        return "unknown"
    op, ver = m.group(1), m.group(2).strip()
    def _tup(v):
        return tuple(int(x) for x in re.findall(r"\d+", v))
    try:
        inst_t = _tup(installed)
        req_t  = _tup(ver)
    except Exception:
        return "unknown"
    if op == ">=":  return "green" if inst_t >= req_t else "red"
    if op == ">":   return "green" if inst_t >  req_t else "red"
    if op in ("=", "=="): return "green" if inst_t == req_t else "red"
    if op == "<=":  return "green" if inst_t <= req_t else "red"
    if op == "<":   return "green" if inst_t <  req_t else "red"
    return "unknown"


def render_package_cards(analyses):
    """Aggregate `packages:` entries across analyses into deduped flippable cards."""
    by_key = {}
    for a in analyses:
        for pkg in a["packages"]:
            if not isinstance(pkg, dict):
                continue
            name = pkg.get("name") or ""
            req  = pkg.get("required_version") or ""
            key  = f"{name}|{req}"
            if key not in by_key:
                by_key[key] = {**pkg, "used_by": []}
            by_key[key]["used_by"].append(a["slug"])

    if not by_key:
        return ('<div class="empty-loud">No package cards yet. Each analysis\'s '
                '<code>packages:</code> frontmatter block becomes a card here.</div>')

    cards = []
    for key in sorted(by_key.keys()):
        pkg = by_key[key]
        name = pkg.get("name") or "?"
        req  = pkg.get("required_version") or "—"
        decl_installed = pkg.get("installed_version") or ""
        live_installed = _query_installed_pkg_version(name) or ""
        status = _compare_versions(live_installed or decl_installed, req)
        url = pkg.get("url") or ""
        desc = pkg.get("description") or ""
        behavior = pkg.get("behavior_note") or ""
        install_source = pkg.get("install_source") or ""
        install_date = pkg.get("install_date") or ""
        known_bugs = pkg.get("known_bugs") or []

        drift_html = ""
        if decl_installed and live_installed and decl_installed != live_installed:
            drift_html = (f'<div class="pkg-drift">⚠ Frontmatter says <code>{html_mod.escape(decl_installed)}</code>; '
                          f'live query returned <code>{html_mod.escape(live_installed)}</code>.</div>')

        used_by_html = " ".join(f'<span class="pkg-uses">{html_mod.escape(s)}</span>' for s in pkg["used_by"])

        bugs_html = ""
        if known_bugs:
            items = []
            for kb in known_bugs:
                if isinstance(kb, dict):
                    items.append(f'<li><code>{html_mod.escape(str(kb.get("version","")))}</code>: {html_mod.escape(str(kb.get("note","")))}</li>')
            if items:
                bugs_html = f'<div class="pkg-bugs"><div class="pkg-section-hdr">Known bugs</div><ul>{"".join(items)}</ul></div>'

        cards.append(f"""
        <div class="fig-flip-container pkg-card-container" onclick="this.classList.toggle('flipped')">
          <div class="fig-flip-inner">
            <div class="fig-front pkg-card pkg-{status}">
              <div class="pkg-name">{html_mod.escape(name)}</div>
              <div class="pkg-status pkg-status-{status}">{status.upper()}</div>
              <div class="pkg-row"><span class="pkg-label">Installed:</span> <code>{html_mod.escape(live_installed or decl_installed or "?")}</code></div>
              <div class="pkg-row"><span class="pkg-label">Required:</span> <code>{html_mod.escape(req)}</code></div>
              <div class="pkg-row"><span class="pkg-label">Source:</span> {html_mod.escape(install_source) or "—"}</div>
              <div class="pkg-row"><span class="pkg-label">Installed on:</span> {html_mod.escape(install_date) or "—"}</div>
              {drift_html}
            </div>
            <div class="fig-back pkg-card pkg-{status}">
              <div class="pkg-name">{html_mod.escape(name)}</div>
              <div class="pkg-row">{html_mod.escape(desc)}</div>
              {f'<div class="pkg-row"><a href="{html_mod.escape(url)}" target="_blank" onclick="event.stopPropagation()">{html_mod.escape(url)}</a></div>' if url else ''}
              <div class="pkg-section-hdr">Behavior of this version</div>
              <div class="pkg-row">{html_mod.escape(behavior) or "<em>not documented</em>"}</div>
              {bugs_html}
              <div class="pkg-section-hdr">Used by analyses</div>
              <div class="pkg-row">{used_by_html or "—"}</div>
            </div>
          </div>
        </div>""")
    return f'<div class="pkg-grid">{"".join(cards)}</div>'


def render_checklist_per_analysis():
    """Top-level Checklist tab: per-analysis grid + package cards."""
    analyses = scan_analyses()
    if not analyses:
        # FELT BOARD: even with no analysis yet, render the beautiful grid as a
        # pinned template row — all 12 step columns, empty cells.
        cols = "".join(f'<th title="{html_mod.escape(s["title"])}"><div class="step-num">{s["num"]}</div><div class="step-label">{s["label"]}</div></th>'
                       for s in ANALYSIS_STEPS)
        cells = "".join(f'<td class="cell-pending" title="Step {s["num"]} — {html_mod.escape(s["title"])}: not yet attempted">○</td>'
                        for s in ANALYSIS_STEPS)
        grid_html = f'''
        <div class="checklist-section">
          <div class="checklist-section-hdr">The checklist (pinned)</div>
          <p class="checklist-help">The canonical DiD checklist — the felt board of what every analysis must do. No analysis has been instantiated yet; the row below is the empty template. The AI invokes <code>/checklist</code> to create <code>analyses/&lt;slug&gt;/checklist.md</code> and walk Steps 0–11.
          <span class="legend"><span class="cell-done">●</span> done (locked) · <span class="cell-active">●</span> You Are Here (active) · <span class="cell-open">●</span> open</span></p>
          <table class="analysis-grid">
            <thead><tr><th>Slug</th>{cols}</tr></thead>
            <tbody><tr class="analysis-row">
                <td class="slug-cell" style="opacity:0.6;font-style:italic;">(template)</td>{cells}
            </tr></tbody>
          </table>
        </div>'''
        return f'<div class="checklist-tab">{grid_html}</div>'

    cols = "".join(f'<th title="{html_mod.escape(s["title"])}"><div class="step-num">{s["num"]}</div><div class="step-label">{s["label"]}</div></th>'
                   for s in ANALYSIS_STEPS)
    rows_html = []
    for a in analyses:
        cells = []
        for s in ANALYSIS_STEPS:
            status = a["steps"].get(s["num"], "pending")
            cells.append(f'<td class="cell-{status}" title="Step {s["num"]} — {html_mod.escape(s["title"])}: {status}">●</td>')
        # Estimator, Status, AND Done/Manifest columns removed: ONE consistent rule — a stage's color IS its
        # lock state — governs everything, including the last stage. Estimator lives in Stage 7 (go there);
        # Status is already told by any red (open) cell (don't say it twice); the final Sign-off STAGE cell is
        # the flip-the-switch (lock it → green/done), so a separate Done/Manifest column duplicated it.
        rows_html.append(
            f'<tr class="analysis-row">'
            f'<td class="slug-cell"><a href="/{a["path"]}" target="_blank" onclick="event.stopPropagation()">{html_mod.escape(a["slug"])}</a></td>'
            f'{"".join(cells)}'
            f'</tr>'
        )

    grid_html = f'''
        <div class="checklist-section">
          <div class="checklist-section-hdr">Per-analysis grid</div>
          <p class="checklist-help">One row per <code>analyses/&lt;slug&gt;/checklist.md</code>. Each cell shows step status (deliverable paths verified to exist on disk; checkboxes counted from the markdown).
          <span class="legend"><span class="cell-done">●</span> done (locked) · <span class="cell-active">●</span> You Are Here (active) · <span class="cell-open">●</span> open</span></p>
          <table class="analysis-grid">
            <thead>
              <tr>
                <th>Slug</th>
                {cols}
              </tr>
            </thead>
            <tbody>
              {"".join(rows_html)}
            </tbody>
          </table>
        </div>
    '''

    pkg_html = f'''
        <div class="checklist-section">
          <div class="checklist-section-hdr">Package cards (Step 0)</div>
          <p class="checklist-help">One card per package declared in any analysis's <code>packages:</code> frontmatter. <strong>Front:</strong> installed vs required, install source and date. <strong>Back:</strong> URL, description, behavior note, known bugs, dependent analyses.<br>The cards are a reading aid — Step 0 is a Gawande pause, not an automation gate.</p>
          {render_package_cards(analyses)}
        </div>
    '''

    return f'<div class="checklist-tab">{grid_html}{pkg_html}</div>'


def scan_stale_code():
    """Find scripts not in the pipeline DAG."""
    pipeline_paths = set(p["script"] for p in PIPELINE_SCRIPTS)
    stale = []
    for d in ["scripts/python", "scripts/r"]:
        p = ROOT / d
        if not p.exists():
            continue
        for f in sorted(p.iterdir()):
            if f.suffix not in (".py", ".R", ".r"):
                continue
            rel = str(f.relative_to(ROOT))
            if rel not in pipeline_paths:
                stat = f.stat()
                # Read first docstring/comment for description
                desc = ""
                try:
                    lines = f.read_text(encoding="utf-8", errors="ignore").split("\n")
                    for line in lines[1:20]:
                        l = line.strip().lstrip("#").lstrip("*").lstrip("\"").lstrip("'").strip()
                        if l and not l.startswith("!") and not l.startswith("import") and not l.startswith("library"):
                            desc = l[:120]
                            break
                except Exception:
                    pass
                stale.append({
                    "path": rel,
                    "name": f.name,
                    "created": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"),
                    "size": f"{stat.st_size/1024:.0f} KB",
                    "desc": desc,
                })
    return stale


def _render_state_md_to_html(md_text):
    """Minimal markdown → HTML renderer scoped to STATE.md's actual conventions.
    Handles: # / ## / ### headings, bullet lists, numbered lists, **bold**,
    *italic* / _italic_, `code`, --- horizontal rules, blank-line paragraphs.
    Not a general-purpose markdown engine; intentionally narrow."""
    import re

    def inline(s):
        s = html_mod.escape(s)
        s = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", s)
        s = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", s)
        s = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", lambda m: f"<em>{m.group(1)}</em>", s)
        s = re.sub(r"(?<!\w)_([^_]+)_(?!\w)", lambda m: f"<em>{m.group(1)}</em>", s)
        return s

    lines = md_text.split("\n")
    out = []
    i = 0
    in_ul = False
    in_ol = False

    def close_lists():
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            close_lists()
            i += 1
            continue
        if line.strip() == "---":
            close_lists()
            out.append('<hr class="state-hr">')
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.+)$", line)
        if m:
            close_lists()
            level = len(m.group(1)) + 1  # h1 -> h2 (we already have a tab <h2>)
            level = min(level, 6)
            out.append(f'<h{level} class="state-h{level}">{inline(m.group(2))}</h{level}>')
            i += 1
            continue
        m = re.match(r"^(\s*)([-*])\s+(.+)$", line)
        if m:
            if not in_ul:
                close_lists()
                out.append('<ul class="state-ul">')
                in_ul = True
            out.append(f"<li>{inline(m.group(3))}</li>")
            i += 1
            continue
        m = re.match(r"^(\s*)(\d+)\.\s+(.+)$", line)
        if m:
            if not in_ol:
                close_lists()
                out.append('<ol class="state-ol">')
                in_ol = True
            out.append(f"<li>{inline(m.group(3))}</li>")
            i += 1
            continue
        # Plain paragraph: gather contiguous non-blank lines
        para = [line]
        j = i + 1
        while j < len(lines) and lines[j].strip() and not re.match(r"^(#{1,4}\s|[-*]\s|\d+\.\s|---)", lines[j].strip()):
            para.append(lines[j].rstrip())
            j += 1
        close_lists()
        out.append(f'<p class="state-p">{inline(" ".join(para))}</p>')
        i = j
    close_lists()
    return "\n".join(out)


def _render_state_inline():
    """Read STATE.md and render it as HTML inside the Arrival ritual card.
    Returns ('', '') if STATE.md does not exist."""
    state_path = ROOT / "STATE.md"
    if not state_path.exists():
        return ('<div class="state-missing">STATE.md does not exist. Create it before opening the project — see CLAUDE.md §STATE.md.</div>',
                '<span class="state-fresh-chip state-missing-chip">missing</span>')
    raw = state_path.read_text(encoding="utf-8")
    body_html = _render_state_md_to_html(raw)
    # Compute freshness from the file mtime — durable across edits that
    # forget to bump the "Last updated:" line.
    age_s = time.time() - state_path.stat().st_mtime
    if age_s < 60 * 60 * 6:
        chip_class, chip_label = "state-fresh-fresh", "fresh"
    elif age_s < 60 * 60 * 24:
        chip_class, chip_label = "state-fresh-aging", "aging"
    else:
        days = int(age_s // (60 * 60 * 24))
        chip_class, chip_label = "state-fresh-stale", f"{days}d stale"
    chip = f'<span class="state-fresh-chip {chip_class}">{chip_label}</span>'
    return (body_html, chip)


def _extract_state_objective():
    """Pull the first non-bold paragraph under '## Current objective' in STATE.md.
    Returns (text, age_chip_class) or (None, None) if not found."""
    state_path = ROOT / "STATE.md"
    if not state_path.exists():
        return None, None
    raw = state_path.read_text(encoding="utf-8")
    m = re.search(r"##\s*Current objective\s*\n+(.+?)(?=\n##\s|\Z)", raw, re.DOTALL)
    if not m:
        return None, None
    block = m.group(1).strip()
    # Take the first paragraph; strip leading **bold prefix** if present.
    first_para = block.split("\n\n")[0].strip()
    # Inline-render bold/italic/code so it reads like prose
    rendered = html_mod.escape(first_para)
    rendered = re.sub(r"`([^`]+)`", lambda m: f"<code>{m.group(1)}</code>", rendered)
    rendered = re.sub(r"\*\*([^*]+)\*\*", lambda m: f"<strong>{m.group(1)}</strong>", rendered)
    rendered = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", lambda m: f"<em>{m.group(1)}</em>", rendered)
    return rendered, None


def _most_recent_audit_or_referee():
    """Find the newest dated file in audits/ or correspondence/referee2/.
    Returns dict with path, name, mtime, age_str, body_preview, or None."""
    candidates = []
    for sub in ("audits", "correspondence/referee2"):
        d = ROOT / sub
        if not d.exists():
            continue
        for fp in d.glob("*.md"):
            if fp.name.startswith("_") or fp.name.upper() == "README.MD":
                continue
            candidates.append(fp)
    if not candidates:
        return None
    newest = max(candidates, key=lambda p: p.stat().st_mtime)
    raw = newest.read_text(encoding="utf-8")

    # Try to extract a verdict / one-line summary. Patterns vary by file:
    # - referee2 reports often have "Verdict:" or "**Verdict:**"
    # - audits have a leading H1 then a summary paragraph
    verdict = None
    for pat in (r"\*\*Verdict:\*\*\s*([^\n]+)", r"Verdict:\s*([^\n]+)",
                r"##\s*Verdict\s*\n+([^\n]+)", r"^####?\s+([^\n]+)$"):
        m = re.search(pat, raw, re.MULTILINE)
        if m:
            verdict = m.group(1).strip()
            break
    # Fall back: first H1 or H2
    if not verdict:
        m = re.search(r"^#{1,2}\s+(.+)$", raw, re.MULTILINE)
        if m:
            verdict = m.group(1).strip()
    # Strip surrounding ** and trailing punctuation/whitespace; the verdict
    # often arrives wrapped in markdown bold from the original report.
    if verdict:
        verdict = verdict.strip()
        # Remove leading/trailing ** pairs
        while verdict.startswith("**") and verdict.endswith("**"):
            verdict = verdict[2:-2].strip()
        # If it has interior **emphasis**, keep the words but drop the asterisks
        verdict = re.sub(r"\*\*([^*]+)\*\*", r"\1", verdict)
        verdict = verdict.strip(" *_")

    age_s = time.time() - newest.stat().st_mtime
    if age_s < 60 * 60 * 24:
        age_str = "today"
    elif age_s < 60 * 60 * 48:
        age_str = "yesterday"
    else:
        age_str = f"{int(age_s // (60 * 60 * 24))} days ago"

    # Strip leading frontmatter for the body preview
    body = raw
    if body.startswith("---"):
        parts = body.split("---", 2)
        if len(parts) >= 3:
            body = parts[2].strip()

    return {
        "rel_path": str(newest.relative_to(ROOT)),
        "name": newest.name,
        "verdict": verdict,
        "age_str": age_str,
        "body_html": _render_state_md_to_html(body),
        "date": datetime.fromtimestamp(newest.stat().st_mtime).strftime("%Y-%m-%d"),
    }


def _ritual_health_counts(figures):
    """Compute the three Departure-side counters from already-scanned dashboard data.
    Returns dict with stale_figures, drift_events, audits_today."""
    stale = sum(1 for f in figures if not f.get("fresh", True))
    drift = sum(1 for f in figures if f.get("orphaned"))
    today_str = datetime.now().strftime("%Y-%m-%d")
    audits_today = 0
    for sub in ("audits", "correspondence/referee2"):
        d = ROOT / sub
        if not d.exists():
            continue
        for fp in d.glob("*.md"):
            if datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d") == today_str:
                audits_today += 1
    return {"stale_figures": stale, "drift_events": drift, "audits_today": audits_today}


def render_rituals(figures=None):
    """Closing/opening rituals — the Taco Bell discipline.

    Two side-by-side cards: Arrival (when you sit down), Departure (when you
    leave). Each is a numbered checklist of gestures that protect against
    session amnesia. Boxes persist in localStorage keyed by today's date so
    each calendar day starts fresh; click 'Reset today' to clear the current
    day's checks if you started checking the wrong list.

    The directives are intentionally concrete and verifiable. The "why"-line
    under each is shown by default — the slow-reading discipline is the point.
    """
    arrival = [
        ("Read STATE.md.",
         "Section 2 (current objective) and section 5 (next). If section 2 doesn't describe what you're about to do today, stop and update it before touching anything else."),
        ("Read the most recent file in audits/ or correspondence/referee2/.",
         "What thread did the last session leave open? What did the last referee2 verdict say to do next?"),
        ("Open the dashboard. Glance at the Narrative banner.",
         "The reorient banner names last session and next move. If it disagrees with STATE.md, STATE.md wins — flag the discrepancy out loud."),
        ("Decide today's one objective. Say it out loud.",
         "One sentence. If you can't state it cleanly, you don't yet know what you're doing — and you'll spend the day in motion without progress."),
        ("Update STATE.md §2 with that objective.",
         "Now the file is honest about today. Future-you (and Claude) read this on entry — don't make them guess."),
    ]

    departure = [
        ("Update STATE.md.",
         "Section 3 (just completed): what landed today. Section 4 (in progress): what's mid-flight, including half-done edits. Section 5 (next): the immediate 1–3 steps. The file must be readable in under a minute by someone who walks in cold tomorrow."),
        ("Verify the dashboard isn't telling lies.",
         "Open the Figures and Checklist tabs. Anything yellow (stale) or red (drift)? Either fix it now, or write the discrepancy into STATE.md §7 (open questions / blockers) so it's visible tomorrow."),
        ("Commit any work-in-progress to a checkpoint.",
         "Even ugly code, even half-finished edits. A terminal closing in mid-flight without a checkpoint is the most expensive kind of amnesia. Use a wip/ branch or a stash if needed."),
        ("Write one line in audits/ if today produced a verdict.",
         "Not every day. But if you closed an audit, finished an analysis, or made a decision that binds tomorrow, file it dated. The dated history is what /amnesia reads from in card 6 of the reorient deck."),
        ("Close the loop on any unanswered Claude questions.",
         "Scan the chat for AskUserQuestion prompts you skipped or tool calls left pending. Either answer now or note in STATE.md §7 that they're deferred — don't let them rot."),
    ]

    def render_list(title, subtitle, lede, items, kind, inline_panel=""):
        rows = []
        for i, (directive, why) in enumerate(items, start=1):
            rows.append(f'''
              <li class="ritual-item">
                <input type="checkbox" class="ritual-check" data-kind="{kind}" data-idx="{i}" id="ritual-{kind}-{i}">
                <label for="ritual-{kind}-{i}" class="ritual-label">
                  <span class="ritual-num">{i}</span>
                  <span class="ritual-body">
                    <span class="ritual-directive">{directive}</span>
                    <span class="ritual-why">{why}</span>
                  </span>
                </label>
              </li>''')
        return f'''
        <section class="ritual-card ritual-{kind}">
          <header class="ritual-header">
            <span class="ritual-eyebrow">{subtitle}</span>
            <h3 class="ritual-title">{title}</h3>
            <p class="ritual-lede">{lede}</p>
          </header>
          {inline_panel}
          <ol class="ritual-list">{"".join(rows)}</ol>
          <footer class="ritual-footer">
            <span class="ritual-progress" id="ritual-progress-{kind}">0 of {len(items)}</span>
            <button class="ritual-reset" onclick="resetRitual('{kind}')">Reset today</button>
          </footer>
        </section>'''

    state_body, state_chip = _render_state_inline()
    state_panel = f'''
      <details class="state-panel" open>
        <summary class="state-summary">
          <span class="state-summary-label">STATE.md</span>
          {state_chip}
          <span class="state-summary-hint">click to collapse</span>
        </summary>
        <div class="state-body">{state_body}</div>
      </details>'''

    # Today's-objective callout — reads STATE.md §2 and renders it large above
    # the checklist. The whole point of Arrival #4 ("decide today's one objective")
    # is to set intent before action; surface it where you can't miss it.
    obj_text, _ = _extract_state_objective()
    today_str = datetime.now().strftime("%A, %B %-d, %Y")
    if obj_text:
        objective_callout = f'''
      <aside class="ritual-objective">
        <div class="ritual-objective-eyebrow">Today &middot; {today_str}</div>
        <div class="ritual-objective-text">{obj_text}</div>
        <div class="ritual-objective-source">From <code>STATE.md</code> &sect;2 &mdash; if this no longer describes today, update STATE.md before checking any boxes.</div>
      </aside>'''
    else:
        objective_callout = ''

    # Most-recent-audit panel — pulls the newest file from audits/ or
    # correspondence/referee2/ and renders its verdict + body inline. Eliminates
    # the click that Arrival #2 ("read the most recent file in audits/") implies.
    audit = _most_recent_audit_or_referee()
    if audit:
        verdict_html = f'<div class="audit-verdict">{html_mod.escape(audit["verdict"])}</div>' if audit["verdict"] else ''
        audit_panel = f'''
      <details class="audit-panel">
        <summary class="audit-summary">
          <span class="audit-summary-label">Most recent audit</span>
          <span class="audit-summary-meta">{audit["date"]} &middot; {audit["age_str"]} &middot; <code>{html_mod.escape(audit["rel_path"])}</code></span>
          <span class="state-summary-hint">click to expand</span>
        </summary>
        {verdict_html}
        <div class="audit-body">{audit["body_html"]}</div>
      </details>'''
    else:
        audit_panel = ''
    arrival_inline = state_panel + audit_panel

    # Departure-side health counters — pulled from the already-scanned figures
    # so this is a request-time pure function. Tells you whether you can leave
    # with a clean conscience without opening other tabs.
    departure_inline = ''
    if figures is not None:
        h = _ritual_health_counts(figures)
        departure_inline = f'''
      <div class="ritual-health">
        <div class="ritual-health-chip {('chip-warn' if h['stale_figures'] else 'chip-ok')}">
          <div class="chip-num">{h['stale_figures']}</div>
          <div class="chip-label">stale figures</div>
        </div>
        <div class="ritual-health-chip {('chip-bad' if h['drift_events'] else 'chip-ok')}">
          <div class="chip-num">{h['drift_events']}</div>
          <div class="chip-label">drift events</div>
        </div>
        <div class="ritual-health-chip chip-ok">
          <div class="chip-num">{h['audits_today']}</div>
          <div class="chip-label">audit{'s' if h['audits_today'] != 1 else ''} today</div>
        </div>
      </div>'''

    arrival_html = render_list(
        "Arrival",
        "When you sit down",
        "Five gestures before you touch anything.",
        arrival,
        "arrival",
        inline_panel=objective_callout + arrival_inline,
    )
    departure_html = render_list(
        "Departure",
        "Before you walk away",
        "Five gestures so future-you can pick up cold.",
        departure,
        "departure",
        inline_panel=departure_inline,
    )

    return f'''
    <div class="ritual-banner">
      <strong>The discipline:</strong> session amnesia is the recurring failure mode.
      These two checklists exist so that you, returning tomorrow, find a project that
      tells the truth about itself — and so that Claude, reading <code>STATE.md</code> on
      entry, is reading something honest. Boxes auto-reset at midnight.
    </div>
    <div class="ritual-grid">
      {arrival_html}
      {departure_html}
    </div>
    <div class="ritual-footnote">
      <em>Origin:</em> Scott, 2026-06-10 — “sort of like a checklist you'd expect someone to follow
      every time they close up a store, like Taco Bell.” The closing list keeps STATE.md honest;
      the opening list ensures you read it before acting.
    </div>'''


def render_pipeline(pipeline):
    levels = {1: "Cleaning", 2: "Derived", 4: "Figures", 5: "Estimation"}
    html = ""
    for lvl in sorted(set(p["level"] for p in pipeline)):
        html += f'<div class="pipe-level"><div class="pipe-level-hdr">Level {lvl}: {levels.get(lvl,"")}</div>'
        for p in pipeline:
            if p["level"] != lvl:
                continue
            status = "fresh" if p["all_fresh"] else "stale"
            html += f'<div class="pipe-item"><span class="pipe-script">{p["script"]}</span><span class="badge {status}">{status}</span></div>'
        html += '</div>'

    # Stale code section
    stale = scan_stale_code()
    if stale:
        html += f'<div class="stale-section"><h3>Stale Code <span style="color:var(--muted);font-weight:normal;font-size:0.75rem;">({len(stale)} scripts outside pipeline)</span></h3>'
        html += '<p style="color:var(--muted);font-size:0.72rem;margin-bottom:0.8rem;">Not in the pipeline DAG. Must be promoted via <code>/gtd audit</code> to appear in courtroom or checklist.</p>'
        for s in stale:
            html += f"""<div class="stale-item">
              <div class="stale-header"><span class="pipe-script">{s['name']}</span><span class="stale-date">{s['created']}</span></div>
              <div class="stale-path">{s['path']}</div>
              <div class="stale-desc">{html_mod.escape(s['desc'])}</div>
            </div>"""
        html += '</div>'

    return html


def render_hypotheses(hypotheses):
    # Pre-scan insights to map hypothesis → supporting evidence
    insights = scan_insights()
    hyp_evidence = {}
    for ins in insights:
        hid = ins.get("updates", "")
        if hid:
            hyp_evidence.setdefault(hid, []).append(ins)

    def render_hyp_node(h, is_child=False):
        child_cls = " child" if is_child else ""
        evidence = hyp_evidence.get(h["id"], [])
        evidence_html = ""
        if evidence:
            evidence_html = '<div class="hyp-evidence">'
            for e in evidence:
                fig_html = ""
                output = e.get("output", "")
                if output and output.endswith(".png") and (ROOT / output).exists():
                    fig_name = Path(output).stem
                    fig_html = f'<img class="hyp-thumb" src="/{output}" title="{fig_name}" onclick="event.stopPropagation();showLightbox(\'/{output}\',\'{fig_name}\')">'
                evidence_html += f'<div class="hyp-ev-item"><span class="badge {e["result"]}">{e["result"]}</span> {html_mod.escape(e["title"])} <span class="date">({e["date"]})</span>{fig_html}</div>'
            evidence_html += '</div>'

        return f"""
        <div class="hyp-node{child_cls} {h['status']}">
          <div class="hyp-header"><span class="hyp-id">{h['id']}</span> {html_mod.escape(h['title'])} <span class="badge {h['status']}">{h['status']}</span></div>
          <div class="hyp-claim">{html_mod.escape(h['claim'][:300])}</div>
          {evidence_html}
        </div>"""

    html = ""
    parents = [h for h in hypotheses if not h["parent"]]
    for p in parents:
        html += render_hyp_node(p)
        children = [h for h in hypotheses if h["parent"] == p["id"]]
        for c in children:
            html += render_hyp_node(c, is_child=True)
    return html


def render_insights(insights):
    html = '<table class="ins-table"><tr><th>Date</th><th>Finding</th><th>Hypothesis</th><th>Status</th></tr>'
    for ins in insights:
        html += f'<tr><td>{ins["date"]}</td><td>{html_mod.escape(ins["title"])}</td><td>{ins["updates"]}</td><td><span class="badge {ins["result"]}">{ins["result"]}</span></td></tr>'
    html += '</table>'
    return html


def render_deliverable_pdf(slug, title, candidates):
    """Render ONE manuscript deliverable view. Embeds+links the PDF if it exists at any candidate path;
    otherwise shows 'not yet written'. Drop a PDF at the first candidate path and it renders here live."""
    found = next((c for c in candidates if (ROOT / c).exists()), None)
    if found:
        status = f'<span style="color:var(--accent);font-weight:600;">● drafted</span> — <a href="/{found}" target="_blank">open PDF in new tab</a>'
        body = f'<iframe src="/{found}" style="width:100%;height:70vh;border:1px solid var(--border);border-radius:8px;margin-top:0.6rem;"></iframe>'
    else:
        status = '<span style="color:var(--muted);">○ not yet written</span>'
        body = (f'<p style="color:var(--muted);font-size:0.8rem;margin-top:0.6rem;">Drop the PDF at '
                f'<code>{candidates[0]}</code> and it renders here.</p>')
    return (f'<div style="background:var(--surface);border:1px solid var(--border);border-radius:10px;'
            f'padding:1rem 1.2rem;">'
            f'<div style="font-size:1.05rem;font-weight:600;color:var(--text);">{title}</div>'
            f'<div style="font-size:0.85rem;margin:0.3rem 0;">{status}</div>{body}</div>')


def list_analysis_stages():
    """Every analyses/<slug>/stages/<NN_name> folder, for the pin-to-stage menu.
    Returns [{slug, stage, label}] where label is a readable 'slug · NN_name'."""
    out = []
    a_dir = ROOT / "analyses"
    if not a_dir.exists():
        return out
    for slug_dir in sorted(a_dir.iterdir()):
        if slug_dir.name.startswith("_"):   # skip _template (not a real analysis)
            continue
        stages_dir = slug_dir / "stages"
        if not (slug_dir.is_dir() and stages_dir.exists()):
            continue
        for st in sorted(stages_dir.iterdir()):
            if st.is_dir():
                out.append({"slug": slug_dir.name, "stage": st.name,
                            "label": f"{slug_dir.name} · {st.name}"})
    return out


def figure_pinned_stages():
    """Scan every analyses/<slug>/stages/<NN>/exhibits.md and return {figure_stem: [labels]} — which stages
    each figure is currently pinned to. Lets the Figures UI show a STANDING 'pinned to X' badge that
    survives navigation, instead of only the transient just-clicked confirmation."""
    out = {}
    a_dir = ROOT / "analyses"
    if not a_dir.exists():
        return out
    for slug_dir in sorted(a_dir.iterdir()):
        if slug_dir.name.startswith("_"):
            continue
        stages_dir = slug_dir / "stages"
        if not (slug_dir.is_dir() and stages_dir.exists()):
            continue
        for st in sorted(stages_dir.iterdir()):
            ex = st / "exhibits.md"
            if not (st.is_dir() and ex.exists()):
                continue
            try:
                txt = ex.read_text()
            except Exception:
                continue
            label = f"{slug_dir.name} · {st.name}"
            for m in re.finditer(r'([\w./-]*(?:output/figures|figures)/[\w.-]+\.png)', txt):
                stem = Path(m.group(1)).stem
                out.setdefault(stem, [])
                if label not in out[stem]:
                    out[stem].append(label)
    return out


def _script_is_wired(script_path):
    """True if `script_path` (a repo-relative path like code/foo.R) is named in code/run_pipeline.sh.
    Used to badge a pin as wired/unwired (canon-closure gate). Never guesses — a substring match
    against the runner text, same as reading it by eye."""
    if not script_path:
        return False
    runner = ROOT / "code" / "run_pipeline.sh"
    if not runner.exists():
        return False
    try:
        txt = runner.read_text()
    except Exception:
        return False
    base = os.path.basename(script_path)
    return script_path in txt or base in txt


def scan_decisions_deck():
    """The project's decisions REVIEW deck, if it has one: a self-contained HTML
    deck at decisions/deck/index.html (a folder) or decisions/deck.html (a file).

    This is deliberately separate from scan_html_decks() (the decks/html/ gallery).
    A decisions deck is the daily-review front door for decisions/INDEX.md — it
    belongs ON the Decisions tab, above the binding-decisions table. Returns None
    when the project has no such deck, so the Decisions tab degrades to exactly
    what it was before."""
    for cand in (ROOT / "decisions" / "deck" / "index.html",
                 ROOT / "decisions" / "deck.html"):
        if cand.is_file():
            title = ""
            try:
                m = re.search(r"<title>(.*?)</title>",
                              cand.read_text(errors="ignore")[:2000], re.I | re.S)
                if m:
                    title = m.group(1).strip()
            except OSError:
                pass
            return {"path": "/" + str(cand.relative_to(ROOT)),
                    "mtime": int(cand.stat().st_mtime),
                    "title": title or "Decisions deck"}
    return None


def render_decisions_deck():
    """Embed the decisions deck at the top of the Decisions tab: click to enlarge
    in-page, F for true OS fullscreen, arrow keys inside the deck for nav.

    Own element ids (dec-deck-*) and own JS names, NOT the Decks tab's #deck-stage
    /#deck-frame — both views live in the same document, so shared ids would make
    getElementById hit whichever came first and one of the two would break."""
    deck = scan_decisions_deck()
    if not deck:
        return ""
    src = html_mod.escape(f'{deck["path"]}?v={deck["mtime"]}')
    js = ("<script>"
          "function decBig(){document.getElementById('dec-deck-stage').classList.toggle('deck-big');}"
          "function decFs(){var s=document.getElementById('dec-deck-stage');"
          "if(s.requestFullscreen){s.requestFullscreen();}"
          "else if(s.webkitRequestFullscreen){s.webkitRequestFullscreen();}}"
          "function _decKey(e){if(e.key!=='f'&&e.key!=='F')return;"
          "if(e.metaKey||e.ctrlKey||e.altKey)return;"
          "var t=(e.target&&e.target.tagName)||'';if(t==='INPUT'||t==='TEXTAREA')return;"
          "var v=document.getElementById('v-decisions');"
          "if(!v||v.offsetParent===null)return;"
          "e.preventDefault();decFs();}"
          "document.addEventListener('keydown',_decKey);"
          "function bindDecKeys(){try{var f=document.getElementById('dec-deck-frame');"
          "var d=f.contentDocument||f.contentWindow.document;"
          "d.addEventListener('keydown',_decKey);"
          "d.addEventListener('click',function(e){var t=e.target;"
          "if(t&&(t.tagName==='BUTTON'||(t.closest&&t.closest('button,a'))))return;"
          "decBig();});}catch(err){}}"
          "</script>")
    return (
        f'{js}'
        f'<div style="margin-bottom:1.4rem;">'
        f'<div style="display:flex;align-items:baseline;gap:0.6rem;flex-wrap:wrap;margin-bottom:0.5rem;">'
        f'<button onclick="decBig()" '
        f'style="padding:0.4rem 0.9rem;border:1px solid var(--border);background:var(--surface2);'
        f'color:var(--text);border-radius:6px;font-size:0.78rem;cursor:pointer;">'
        f'&#9974; Big (click deck)</button>'
        f'<button onclick="decFs()" title="Or press F while this tab is open" '
        f'style="padding:0.4rem 0.9rem;border:1px solid var(--accent);background:var(--accent);'
        f'color:#fff;border-radius:6px;font-size:0.78rem;cursor:pointer;">'
        f'&#9974; Fullscreen <kbd style="opacity:.8;">F</kbd></button>'
        f'<a href="{src}" target="_blank" '
        f'style="font-size:0.72rem;color:var(--accent);text-decoration:none;">'
        f'&#8599; open in its own tab</a>'
        f'<span style="font-size:0.66rem;color:var(--muted);">'
        f'&#8592;&#8594; to move through slides</span>'
        f'</div>'
        f'<div id="dec-deck-stage" onclick="decBig()" style="position:relative;cursor:zoom-in;">'
        f'<iframe id="dec-deck-frame" src="{src}" allowfullscreen onload="bindDecKeys()" '
        f'onclick="event.stopPropagation()" '
        f'style="display:block;width:100%;height:calc(100vh - 16rem);border:1px solid var(--border);'
        f'border-radius:6px;background:var(--surface);"></iframe>'
        f'</div>'
        f'<div style="font-size:0.66rem;color:var(--muted);margin-top:0.4rem;line-height:1.4;">'
        f'The decisions review deck, built from <code>decisions/INDEX.md</code>. '
        f'A decisions-review artifact &mdash; it carries no analysis numbers.</div>'
        f'</div>')


def render_decisions(decisions):
    html = render_decisions_deck()
    html += '<table class="dec-table"><tr><th>ID</th><th>Decision</th><th>Date</th><th>Rationale</th></tr>'
    for d in decisions:
        html += f'<tr><td><strong>{d["id"]}</strong></td><td>{html_mod.escape(d["decision"])}</td><td>{d["date"]}</td><td>{html_mod.escape(d["rationale"])}</td></tr>'
    html += '</table>'
    return html


def render_figures(figures, insights=None):
    insights = insights or []
    pinned_map = figure_pinned_stages()   # {figure_stem: [stage labels]} for the standing pin chips
    # Build figure→stage mapping from insights
    fig_to_stages = {}
    for ins in insights:
        output = ins.get("output", "")
        if output and "figures" in output:
            fig_name = Path(output).stem
            for snum in map_insight_to_stages(ins):
                if fig_name not in fig_to_stages:
                    fig_to_stages[fig_name] = []
                if snum not in fig_to_stages[fig_name]:
                    fig_to_stages[fig_name].append(snum)

    # Group by tier
    manifest = read_manifest()
    pipe_figs = [f for f in figures if manifest.get(f['script'], 'review') == 'approved' and f['script']]
    review_figs = [f for f in figures if manifest.get(f['script'], 'review') == 'review' or not f['script']]
    sandbox_figs = [f for f in figures if manifest.get(f['script'], 'review') == 'sandbox' and f['script']]

    # Left panel: list grouped by tier
    list_html = '<div class="fig-list-hdr pipe">Pipeline</div>'
    for f in pipe_figs:
        list_html += f'<div class="fig-list-item" onclick="document.getElementById(\'fig-{f["name"]}\').scrollIntoView({{behavior:\'smooth\',block:\'center\'}})">{f["name"]}</div>'
    if review_figs:
        list_html += '<div class="fig-list-hdr review">For Review</div>'
        for f in review_figs:
            list_html += f'<div class="fig-list-item" onclick="document.getElementById(\'fig-{f["name"]}\').scrollIntoView({{behavior:\'smooth\',block:\'center\'}})">{f["name"]}</div>'
    if sandbox_figs:
        list_html += '<div class="fig-list-hdr sandbox">Sandbox</div>'
        for f in sandbox_figs:
            list_html += f'<div class="fig-list-item" onclick="document.getElementById(\'fig-{f["name"]}\').scrollIntoView({{behavior:\'smooth\',block:\'center\'}})">{f["name"]}</div>'

    # Right panel: figure cards
    cards_html = '<div class="fig-grid">'
    for f in figures:
        if f["orphaned"]:
            border = "orphaned"
        elif f["fresh"]:
            border = "fresh"
        elif f["fresh"] is False:
            border = "stale"
        else:
            border = ""
        script_display = f['script'] or 'orphaned'
        line_num = find_line_for_output(f['script'], f['name']) if f['script'] and f['script'] != 'ad-hoc' else None
        line_label = f" (line {line_num})" if line_num else ""
        tier = get_script_tier(f['script']) if f['script'] else "review"
        # Check FIGURE_CAPTIONS.json first, then fall back to auto-extraction from code
        captions_file = ROOT / "FIGURE_CAPTIONS.json"
        manual_captions = {}
        if captions_file.exists():
            import json as json_mod
            manual_captions = json_mod.loads(captions_file.read_text())
        caption = manual_captions.get(f['name']) or (extract_figure_caption(f['script'], f['name']) if f['script'] and f['script'] != 'ad-hoc' else None)
        caption_html = f'<div class="fig-caption">{html_mod.escape(caption)}</div>' if caption else ''
        # Pin-to-stage control (append the figure's path to a checklist stage's exhibits.md via /api/pin-figure).
        _fig_name_esc = html_mod.escape(f["name"])
        _script_attr = html_mod.escape(f.get("script") or "")
        _pinned_here = pinned_map.get(f["name"], [])
        _pinned_html = ""
        if _pinned_here:
            _chips = "".join(f'<span class="pin-chip">&#128204; {html_mod.escape(p)}</span>' for p in _pinned_here)
            _pinned_html = f'<div class="pin-current">{_chips}</div>'
        pin_footer = (
            f'<div class="ds-card-foot" onclick="event.stopPropagation()">{_pinned_html}'
            f'<button class="pin-btn" onclick="openPinMenu(this,&apos;{_fig_name_esc}&apos;,&apos;{html_mod.escape(f["path"])}&apos;,&apos;{_script_attr}&apos;)">&#128204; Pin to stage &#9662;</button>'
            f'<span class="pin-status"></span></div>')
        cards_html += f"""
        <div class="fig-flip-container" id="fig-{f['name']}" style="max-width:620px;margin-bottom:1.5rem;" onclick="this.classList.toggle('flipped')">
          <div class="fig-flip-inner">
            <div class="fig-front fig-card {border}">
              <img src="/{f['path']}" loading="lazy" data-cycle-src="/{f['path']}" data-cycle-name="{f['name']}" data-cycle-kind="figure" data-cycle-group="figures-tab" ondblclick="event.stopPropagation();showLightboxFromGroup(this, '[data-cycle-group=&quot;figures-tab&quot;]')">
              <div class="fig-name">{f['name']} <span class="tier-dot tier-{tier}"></span>{'<span class="fig-no-desc">?</span>' if not caption else ''}<span class="fig-expand" data-cycle-src="/{f['path']}" data-cycle-name="{f['name']}" data-cycle-kind="figure" data-cycle-group="figures-tab" onclick="event.stopPropagation();showLightboxFromGroup(this, '[data-cycle-group=&quot;figures-tab&quot;].fig-expand')">&#x26F6;</span></div>
              <div class="fig-meta">{f['mtime']} &middot; {script_display}</div>
            </div>
            <div class="fig-back fig-card {border}">
              <div class="fig-back-header">{f['name']}</div>
              {caption_html if caption else '<div class="fig-desc-needed">Description needed — audit this figure</div>'}
              <div class="fig-back-script">{script_display}</div>
              <div class="fig-back-action" onclick="event.stopPropagation();loadCode('{script_display}',{line_num or 'null'})">View source{line_label} &rarr;</div>
              {'<div class="fig-back-stage">Courtroom: ' + ", ".join(f"Stage {s}" for s in fig_to_stages.get(f["name"], [])) + '</div>' if f["name"] in fig_to_stages else ''}
              <div class="fig-back-meta">
                <div>Modified: {f['mtime']}</div>
                <div>Path: {f['path']}</div>
              </div>
              <div class="tier-buttons" onclick="event.stopPropagation()">
                <button class="tier-btn {'tier-active' if tier=='approved' else ''}" onclick="setTier('{script_display}','approved',this)">Pipeline</button>
                <button class="tier-btn {'tier-active' if tier=='review' else ''}" onclick="setTier('{script_display}','review',this)">For Review</button>
                <button class="tier-btn {'tier-active' if tier=='sandbox' else ''}" onclick="setTier('{script_display}','sandbox',this)">Sandbox</button>
              </div>
              {pin_footer}
            </div>
          </div>
        </div>"""
    cards_html += '</div>'
    return f'<div class="fig-split"><div class="fig-list">{list_html}</div><div class="fig-main">{cards_html}</div></div>'


def _fmt_size(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024.0:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024.0
    return f"{n:.1f} PB"


def render_data(data_entries):
    # LEAN single-project: list the real immutable raw datasets under data/raw/.
    raw_dir = ROOT / "data" / "raw"
    notes = {}
    files = sorted(raw_dir.glob("*")) if raw_dir.exists() else []
    files = [f for f in files if f.is_file() and not f.name.startswith(".")]
    html = f'<p style="color:var(--muted);font-size:0.8rem;margin-bottom:1rem;">{len(files)} raw dataset(s) in <code>data/raw/</code> — immutable source files. Every derived number traces back through code to these.</p>'
    if not files:
        html += '<div style="color:var(--muted);font-size:0.85rem;padding:1.2rem;border:1px dashed var(--border);border-radius:8px;">No files found under <code>data/raw/</code>.</div>'
    for f in files:
        try:
            size = _fmt_size(f.stat().st_size)
        except OSError:
            size = "?"
        note = notes.get(f.name, "Raw immutable source dataset.")
        html += f"""
        <div class="data-card">
          <div class="data-header">
            <span class="data-name">{html_mod.escape(f.name)}</span>
            <span class="badge fresh">{size}</span>
          </div>
          <div class="data-desc">{html_mod.escape(note)}</div>
          <div class="data-meta"><strong>Path:</strong> <code>data/raw/{html_mod.escape(f.name)}</code></div>
        </div>"""
    return html


def render_data_catalog(data_entries):
    html = f'<p style="color:var(--muted);font-size:0.8rem;margin-bottom:1rem;">{len(data_entries)} source datasets cataloged.</p>'
    for d in data_entries:
        exists_cls = "fresh" if d["exists"] else "missing"
        exists_lbl = f'{d["n_files"]} files &middot; {d["size"]}' if d["exists"] else "NOT FOUND"
        scripts_html = " ".join(f'<span class="data-script">{s.split("/")[-1]}</span>' for s in d["used_by"]) if d["used_by"] else '<span style="color:var(--muted);font-size:0.7rem;">not yet in pipeline</span>'
        figs_html = ""
        if d.get("figures"):
            figs_html = '<div class="data-figs">Produces: ' + " ".join(f'<span class="data-fig">{Path(f).stem}</span>' for f in d["figures"]) + '</div>'
        preview_html = ""
        if d.get("preview"):
            preview_lines = "\n".join(html_mod.escape(l[:120]) for l in d["preview"])
            preview_html = f'<pre class="data-preview">{preview_lines}</pre>'
        html += f"""
        <div class="data-card">
          <div class="data-header">
            <span class="data-name">{html_mod.escape(d['name'])}</span>
            <span class="badge {exists_cls}">{exists_lbl}</span>
          </div>
          <div class="data-desc">{html_mod.escape(d['desc'])}</div>
          <div class="data-meta"><strong>Source:</strong> {html_mod.escape(d['source'])} &middot; <strong>Collected:</strong> {d['collected']}</div>
          <div class="data-used">Consumed by: {scripts_html}</div>
          {figs_html}
          {preview_html}
        </div>"""
    return html


def render_code(code_files):
    file_list = "".join(f'<div class="code-item" onclick="loadCode(\'{f}\')">{f.split("/")[-1]}</div>' for f in code_files)
    return f"""
    <div class="code-split">
      <div class="code-list">{file_list}</div>
      <div class="code-view"><div id="code-path"></div><pre id="code-body">Click a file to view</pre></div>
    </div>"""


def render_code_unified(pipeline, code_files):
    """Unified code view: Pipeline (green) + Stale (yellow) in left panel."""
    pipeline_paths = set(p["script"] for p in PIPELINE_SCRIPTS)
    stale_scripts = [f for f in code_files if f not in pipeline_paths]

    # Pipeline section
    pipe_items = ""
    for p in pipeline:
        status_cls = "fresh" if p["all_fresh"] else "stale"
        pipe_items += f'<div class="code-item pipe-{status_cls}" onclick="loadCode(\'{p["script"]}\')">{p["script"].split("/")[-1]} <span class="code-badge {status_cls}"></span></div>'

    # Stale section
    stale_items = ""
    for f in stale_scripts:
        stale_items += f'<div class="code-item stale-code" onclick="loadCode(\'{f}\')">{f.split("/")[-1]}</div>'

    return f"""
    <div class="code-split">
      <div class="code-list">
        <div class="code-section-hdr pipeline-hdr">Pipeline</div>
        {pipe_items}
        <div class="code-section-hdr stale-hdr">Stale</div>
        {stale_items}
      </div>
      <div class="code-view"><div id="code-path"></div><pre id="code-body">Click a file to view</pre></div>
    </div>"""


def parse_latex_table(text):
    """Attempt to render a LaTeX tabular as HTML. Returns HTML or None if unparseable."""
    if "\\begin{tabular" not in text:
        return None
    try:
        # Extract between \begin{tabular} and \end{tabular}
        start = text.index("\\begin{tabular")
        end = text.index("\\end{tabular}") + len("\\end{tabular}")
        tabular = text[start:end]
        # Parse rows
        rows = []
        for line in tabular.split("\n"):
            line = line.strip()
            if not line or line.startswith("\\begin") or line.startswith("\\end") or line.startswith("\\toprule") or line.startswith("\\bottomrule") or line.startswith("\\midrule") or line.startswith("\\hline"):
                continue
            if "&" in line:
                cells = [c.strip().rstrip("\\\\").strip() for c in line.split("&")]
                cells = [c.replace("\\textbf{", "").replace("}", "").replace("\\", "") for c in cells]
                rows.append(cells)
        if not rows:
            return None
        html = '<table class="rendered-table"><thead><tr>'
        for c in rows[0]:
            html += f'<th>{html_mod.escape(c)}</th>'
        html += '</tr></thead><tbody>'
        for row in rows[1:]:
            html += '<tr>' + "".join(f'<td>{html_mod.escape(c)}</td>' for c in row) + '</tr>'
        html += '</tbody></table>'
        return html
    except Exception:
        return None


def parse_csv_table(text):
    """Render CSV content as HTML table."""
    lines = text.strip().split("\n")
    if not lines:
        return None
    rows = [line.split(",") for line in lines[:50]]
    html = '<table class="rendered-table"><thead><tr>'
    for c in rows[0]:
        html += f'<th>{html_mod.escape(c.strip())}</th>'
    html += '</tr></thead><tbody>'
    for row in rows[1:]:
        html += '<tr>' + "".join(f'<td>{html_mod.escape(c.strip())}</td>' for c in row) + '</tr>'
    html += '</tbody></table>'
    return html


def find_line_for_output(script_path, output_name):
    """Find the line number in a script where an output file is referenced."""
    sp = ROOT / script_path
    if not sp.exists():
        return None
    try:
        for i, line in enumerate(sp.read_text(encoding="utf-8", errors="ignore").split("\n"), 1):
            if output_name in line:
                return i
    except Exception:
        pass
    return None


def extract_figure_caption(script_path, output_name):
    """Extract a caption for a figure by finding title/comment near the savefig call."""
    sp = ROOT / script_path
    if not sp.exists():
        return None
    try:
        lines = sp.read_text(encoding="utf-8", errors="ignore").split("\n")
        save_line = None
        for i, line in enumerate(lines):
            if output_name in line and ("save" in line.lower() or "ggsave" in line.lower() or "export" in line.lower() or "png" in line.lower()):
                save_line = i
                break
        if save_line is None:
            return None
        # Look backward up to 15 lines for a title or section comment
        context = lines[max(0, save_line - 15):save_line + 1]
        # Try to find ax.set_title, title(, or a section comment
        for cl in reversed(context):
            # Python: ax.set_title('...')
            if "set_title(" in cl or "title(" in cl:
                import re
                m = re.search(r"['\"]([^'\"]{8,})['\"]", cl)
                if m:
                    return m.group(1).replace("\\n", " — ")
            # R: title("...")
            if "title(" in cl.lower() and '"' in cl:
                import re
                m = re.search(r'"([^"]{8,})"', cl)
                if m:
                    return m.group(1)
            # Section comment: # === FIGURE 3: ... ===
            stripped = cl.strip()
            if stripped.startswith("#") and len(stripped) > 10 and not stripped.startswith("#!"):
                comment = stripped.lstrip("# =").rstrip("= ").strip()
                if len(comment) > 8:
                    return comment
    except Exception:
        pass
    return None


def render_tables():
    """Scan output/tables/ for .tex and .csv files. Render as flippable cards with left-panel list."""
    tables_dir = ROOT / "output" / "tables"
    if not tables_dir.exists():
        return '<p class="empty">No output/tables/ directory.</p>'
    files = sorted(tables_dir.glob("*"))
    files = [f for f in files if f.suffix in (".tex", ".csv")]
    if not files:
        return '<p class="empty">No tables found.</p>'

    # Left panel list
    manifest = read_manifest()
    _verdicts, _run_stamp = official_verdicts()
    list_html = ""
    for f in files:
        rel_path = str(f.relative_to(ROOT))
        source_script = None
        for entry in PIPELINE_SCRIPTS:
            if rel_path in entry["outputs"]:
                source_script = entry["script"]
                break
        tier = manifest.get(source_script, "review") if source_script else "review"
        dot_cls = f"tier-{tier}"
        _vb = verdict_badge(rel_path, _verdicts, _run_stamp)
        list_html += f'<div class="fig-list-item" onclick="document.getElementById(\'tbl-{f.stem}\').scrollIntoView({{behavior:\'smooth\',block:\'center\'}})">{f.name} <span class="tier-dot {dot_cls}"></span>{("<div>" + _vb + "</div>") if _vb else ""}</div>'

    html = '<div class="table-grid">'
    for f in files:
        try:
            content = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        rendered = None
        if f.suffix == ".tex":
            rendered = parse_latex_table(content)
        elif f.suffix == ".csv":
            rendered = parse_csv_table(content)

        # Find source script — check pipeline first, then grep all scripts
        rel_path = str(f.relative_to(ROOT))
        source_script = None
        source_line = None
        for entry in PIPELINE_SCRIPTS:
            if rel_path in entry["outputs"]:
                source_script = entry["script"]
                source_line = find_line_for_output(entry["script"], f.name)
                break
        if not source_script:
            for script_dir in ["scripts/python", "scripts/r"]:
                sd = ROOT / script_dir
                if not sd.exists():
                    continue
                for sf in sd.iterdir():
                    if sf.suffix in (".py", ".R", ".r"):
                        ln = find_line_for_output(str(sf.relative_to(ROOT)), f.name)
                        if ln:
                            source_script = str(sf.relative_to(ROOT))
                            source_line = ln
                            break
                if source_script:
                    break

        front_content = rendered if rendered else f'<pre class="table-raw">{html_mod.escape(content[:1500])}</pre>'
        script_display = source_script or "unknown"
        line_ref = f"#L{source_line}" if source_line else ""
        table_caption = extract_figure_caption(source_script, f.name) if source_script else None
        table_caption_html = f'<div class="fig-caption">{html_mod.escape(table_caption)}</div>' if table_caption else ''

        html += f"""
        <div class="fig-flip-container" id="tbl-{f.stem}" onclick="this.classList.toggle('flipped')">
          <div class="fig-flip-inner">
            <div class="fig-front table-card">
              <div class="table-title">{f.name}</div>
              {front_content}
            </div>
            <div class="fig-back table-card">
              <div class="fig-back-header">{f.name}</div>
              {table_caption_html}
              <div class="fig-back-script">{script_display}</div>
              {f'<div class="fig-back-action" onclick="event.stopPropagation();loadCode(&apos;{script_display}&apos;)">View source (line {source_line}) &rarr;</div>' if source_script else '<div class="fig-back-action" style="color:var(--muted)">No pipeline script mapped</div>'}
              <div class="fig-back-meta">
                <div>Path: {rel_path}</div>
                <div>Size: {f.stat().st_size/1024:.0f} KB</div>
              </div>
              {f'<div class="tier-buttons" onclick="event.stopPropagation()"><button class="tier-btn {chr(39)+"tier-active"+chr(39) if get_script_tier(source_script)=="approved" else ""}" onclick="setTier(&apos;{source_script}&apos;,&apos;approved&apos;,this)">Pipeline</button><button class="tier-btn {chr(39)+"tier-active"+chr(39) if get_script_tier(source_script)=="review" else ""}" onclick="setTier(&apos;{source_script}&apos;,&apos;review&apos;,this)">For Review</button><button class="tier-btn {chr(39)+"tier-active"+chr(39) if get_script_tier(source_script)=="sandbox" else ""}" onclick="setTier(&apos;{source_script}&apos;,&apos;sandbox&apos;,this)">Sandbox</button></div>' if source_script else ''}
            </div>
          </div>
        </div>"""
    html += '</div>'
    return f'<div class="fig-split"><div class="fig-list">{list_html}</div><div class="fig-main">{html}</div></div>'


def annotate_hypothesis_ids(html_text, hypotheses):
    """Inject inline status badges next to hypothesis IDs (H01, H01a, etc.) in rendered HTML. Complicated/testing badges are clickable to expand the reason."""
    # Build a map of id → (status, reason)
    info_map = {}
    for h in hypotheses:
        reason = ""
        if h["status"] in ("complicated", "testing", "conjecture"):
            # Pull the first line of the kills_it or claim as context
            reason = h.get("kills_it", "") or h.get("claim", "")
            reason = reason.split("\n")[0][:150]
        info_map[h["id"]] = (h["status"], reason)

    for hid, (status, reason) in sorted(info_map.items(), key=lambda x: len(x[0]), reverse=True):
        if status in ("complicated", "testing") and reason:
            badge = f'<span class="narr-badge {status}" onclick="this.nextElementSibling.classList.toggle(\'open\')">{status}</span><span class="narr-reason">{html_mod.escape(reason)}</span>'
        else:
            badge = f'<span class="narr-badge {status}">{status}</span>'
        html_text = html_text.replace(f'{hid}', f'{hid} {badge}', 1)
    return html_text


def check_narrative_drift(content, hypotheses):
    """Check if narrative.md references hypotheses that are not confirmed. Returns warnings."""
    status_map = {h["id"]: h["status"] for h in hypotheses}
    warnings = []
    for hid, status in status_map.items():
        if hid in content and status in ("complicated", "rejected", "testing"):
            warnings.append(f'<a class="drift-link" onclick="show(\'hypotheses\');setTimeout(()=>document.querySelector(\'.hyp-id\')&&document.querySelectorAll(\'.hyp-node\').forEach(n=>{{if(n.textContent.includes(\'{hid}\'))n.scrollIntoView({{behavior:\'smooth\'}})}}),100)">{hid}</a> is referenced but status is <span class="badge {status}">{status}</span>')
    return warnings


def render_narrative(hypotheses, insights):
    nf = ROOT / "narrative.md"
    # If narrative.md has real content (more than the placeholder), use it
    if nf.exists():
        content = nf.read_text().strip()
        if len(content) > 100 and not content.startswith("# Narrative\n\nThe narrative will be assembled"):
            # Check for drift
            drift_warnings = check_narrative_drift(content, hypotheses)
            warning_html = ""
            if drift_warnings:
                items = "".join(f'<li>{w}</li>' for w in drift_warnings)
                warning_html = f'<div class="narr-warning"><strong>Drift detected:</strong> narrative references unconfirmed material.<ul>{items}</ul></div>'

            # Split into sections for left-panel navigation
            lines = content.split("\n")
            sections = []
            current_title = ""
            current_body = []
            for line in lines:
                if line.startswith("## "):
                    if current_title:
                        sections.append((current_title, "\n".join(current_body)))
                    current_title = line[3:].strip()
                    current_body = []
                elif line.startswith("# "):
                    continue
                else:
                    current_body.append(line)
            if current_title:
                sections.append((current_title, "\n".join(current_body)))

            # Left panel: draggable section titles
            list_html = ""
            for i, (title, _) in enumerate(sections):
                slug = f"narr-sec-{i}"
                list_html += f'<div class="fig-list-item" onclick="document.getElementById(\'{slug}\').scrollIntoView({{behavior:\'smooth\',block:\'start\'}})">{title}</div>'

            # Right panel: rendered sections
            body_html = ""
            for i, (title, body) in enumerate(sections):
                slug = f"narr-sec-{i}"
                rendered_body = mini_md(body)
                rendered_body = annotate_hypothesis_ids(rendered_body, hypotheses)
                body_html += f'<div id="{slug}" class="narr-section-block"><h2>{html_mod.escape(title)}</h2>{rendered_body}</div>'

            return f'{warning_html}<div class="fig-split" style="height:calc(100vh - 200px)"><div class="fig-list">{list_html}</div><div class="fig-main"><div class="narrative-prose">{body_html}</div></div></div>'

    # Auto-assemble from confirmed/complicated material — present tense, current state only
    sections = []

    # What do we currently believe?
    confirmed = [h for h in hypotheses if h["status"] == "confirmed"]
    complicated = [h for h in hypotheses if h["status"] == "complicated"]
    testing = [h for h in hypotheses if h["status"] == "testing"]

    if confirmed:
        items = "".join(f'<li><strong>{h["id"]}:</strong> {html_mod.escape(h["claim"][:150])}</li>' for h in confirmed)
        sections.append(f'<div class="narr-section"><h3>What We Know</h3><ul>{items}</ul></div>')

    if complicated:
        items = "".join(f'<li><strong>{h["id"]}:</strong> {html_mod.escape(h["claim"][:150])}</li>' for h in complicated)
        sections.append(f'<div class="narr-section"><h3>What Is Complicated</h3><ul>{items}</ul></div>')

    if testing:
        items = "".join(f'<li><strong>{h["id"]}:</strong> {html_mod.escape(h["claim"][:150])}</li>' for h in testing)
        sections.append(f'<div class="narr-section"><h3>What We Are Testing</h3><ul>{items}</ul></div>')

    # Latest confirmed insights as supporting evidence
    confirmed_insights = [i for i in insights if i["result"] == "confirmed"][:5]
    if confirmed_insights:
        items = "".join(f'<li><span class="date">{i["date"]}</span> {html_mod.escape(i["title"])}</li>' for i in confirmed_insights)
        sections.append(f'<div class="narr-section"><h3>Supporting Evidence</h3><ul>{items}</ul></div>')

    if not sections:
        return '<p class="empty">No confirmed material yet. The narrative emerges as courtroom stages are completed.</p>'

    return '<div class="narrative-auto">' + "".join(sections) + '<p style="color:var(--muted);font-size:0.7rem;margin-top:1.5rem;">Auto-assembled from confirmed material. Write narrative.md to replace with authored prose.</p></div>'


def render_voices():
    """Render voice profiles from voices/ directory."""
    voices_dir = ROOT / "voices"
    voices = []
    for name in ["weitzman", "pollak"]:
        profile = voices_dir / name / "VOICE_PROFILE.md"
        if profile.exists():
            fm, body = parse_frontmatter(profile)
            # Extract key moves (first few bullet points)
            moves = []
            for line in body.split("\n"):
                if line.strip().startswith("- **"):
                    move = line.strip()[2:].split("**")
                    if len(move) >= 2:
                        moves.append({"name": move[1], "desc": move[2].lstrip(". ").strip() if len(move) > 2 else ""})
                    if len(moves) >= 4:
                        break
            voices.append({"name": name.capitalize(), "moves": moves, "file": str(profile.relative_to(ROOT))})

    html = ""
    for v in voices:
        moves_html = "".join(f'<li><strong>{m["name"]}</strong> {html_mod.escape(m["desc"][:100])}</li>' for m in v["moves"])
        html += f"""
        <div class="voice-card">
          <div class="voice-name">{v['name']}</div>
          <ul class="voice-moves">{moves_html}</ul>
          <div class="voice-file">{v['file']}</div>
        </div>"""

    # Blend
    html += """
    <div class="voice-card">
      <div class="voice-name">Blend</div>
      <ul class="voice-moves">
        <li><strong>Pollak's skeleton, Weitzman's muscle.</strong> Open with directness, close with widening implication.</li>
        <li><strong>Enumeration + escalation.</strong> Taxonomy for structure, understatement for tone.</li>
        <li><strong>Like an architect who has seen the flood coming</strong> and is calmly specifying the levee.</li>
      </ul>
    </div>"""
    return html


def render_skills():
    """Scan ~/.claude/skills/ for installed skills and render them."""
    skills_dir = Path.home() / ".claude" / "skills"
    if not skills_dir.exists():
        return '<p class="empty">No skills directory found.</p>'
    skills = []
    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        skill_file = d / "SKILL.md"
        if not skill_file.exists():
            continue
        fm, body = parse_frontmatter(skill_file)
        name = fm.get("name", d.name)
        desc = fm.get("description", "")
        # Extract argument hint if present
        hint = fm.get("argument-hint", "")
        if isinstance(hint, list):
            hint = " ".join(hint)
        skills.append({"name": name, "desc": desc, "hint": hint})

    # GTD commands with fuller explanations
    gtd_commands = [
        ("/gtd conjecture", "State a belief", "You say what you think is true. Claude interrogates it with 6 questions (estimand, population, variation, mechanism, falsification, sub-claims) one at a time. Result: a filed hypothesis with a 'kills it' condition."),
        ("/gtd insight", "File a finding", "Record an empirical result with exact numbers. Must link to a hypothesis and a pipeline script. This is how evidence enters the system."),
        ("/gtd decide", "Bind a choice", "Commit to a design decision (estimator, sample, treatment date). Once committed, all scripts must respect it. Enforces consistency."),
        ("/gtd audit [topic]", "Interrogate anything", "5 steps: What is it? → Is it correct? → Does it belong? → What's next? → Update narrative? One question at a time. Produces an audit record."),
        ("/gtd courtroom", "Walk the proof", "Go through the 5 stages (show bite → event study → falsification → main results → mechanisms). Present exhibits, confirm or flag. Populates the narrative."),
        ("/gtd pipeline", "Check freshness", "Which outputs are stale? Which figures are orphaned? Forces the pipeline to be current."),
        ("/gtd status", "Orient quickly", "Hypothesis counts, pipeline health, latest insight, next actions. The 10-second briefing."),
    ]

    html = ""
    for cmd, short, full in gtd_commands:
        html += f'<div class="skill-card"><div class="skill-name">{cmd} <span class="skill-hint">— {short}</span></div><div class="skill-desc">{full}</div></div>'
    return html


def render_manuscript():
    mf = ROOT / "manuscript_outline.md"
    if mf.exists():
        return mini_md(mf.read_text())
    return '<p class="empty">No manuscript_outline.md found.</p>'


def render_stages():
    """The canister hallway. Each checklist stage is a room holding four files:
    ideas / todo / findings / exhibits, colour-coded (violet/amber/green/teal).
    Landing = a grid of doors with a peek; click a door to ENTER the room.
    Reads analyses/<slug>/stages/<NN>/ at request time. ACTIVE_STAGE glows."""
    import html as _h, re as _re
    # canister palette — consistent everywhere
    C = {"ideas": "#8b5cf6", "todo": "#D97706", "findings": "#059669", "exhibits": "#0E7490"}
    base = ROOT / "analyses"
    analyses = sorted([d for d in base.glob("*/stages") if d.is_dir()]) if base.exists() else []
    if not analyses:
        return ('<p class="empty">No stage canisters yet. They live at '
                '<code>analyses/&lt;slug&gt;/stages/&lt;NN_name&gt;/</code> with four files each: '
                'ideas.md · todo.md · findings.md · exhibits.md.</p>')

    out = []
    for stages_dir in analyses:
        slug = stages_dir.parent.name
        active = ""
        amf = stages_dir.parent / "ACTIVE_STAGE"
        if amf.exists():
            active = amf.read_text().strip()
        rooms = sorted([d for d in stages_dir.iterdir() if d.is_dir()])

        def _count_boxes(p):
            if not p.exists():
                return 0, False
            t = p.read_text()
            return t.count("- [ ]"), ("- [x]" in t or "- [X]" in t)

        def _count_bullets(p):
            if not p.exists():
                return 0
            return sum(1 for l in p.read_text().splitlines()
                       if l.strip().startswith(("- ", "* ")) and "[ ]" not in l and "[x]" not in l)

        def _has_content(p):
            # findings/exhibits "done" = file exists with real prose beyond the header
            if not p.exists():
                return False
            body = _re.sub(r"^---.*?---", "", p.read_text(), flags=_re.S)
            body = _re.sub(r"^#.*$", "", body, flags=_re.M)
            return len(body.strip()) > 120

        out.append(f'<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;'
                   f'color:var(--muted);margin:0.4rem 0 0.8rem;">{_h.escape(slug)} · '
                   f'{"room " + _h.escape(active) + " is active" if active else "no active room"}</div>')

        # ---- the hallway: door grid ----
        doors = ""
        for room in rooms:
            nm = room.name                       # e.g. 02_assignment
            num = nm.split("_")[0]
            title = nm.split("_", 1)[1].replace("_", " ").title() if "_" in nm else nm
            is_active = (nm == active)
            n_ideas = _count_bullets(room / "ideas.md")
            n_todo, _ = _count_boxes(room / "todo.md")
            has_find = _has_content(room / "findings.md")
            ex = room / "exhibits.md"
            n_exhib = sum(1 for l in (ex.read_text().splitlines() if ex.exists() else [])
                          if l.strip().startswith("- ")) if ex.exists() else 0
            glow = (f"box-shadow:0 0 0 2px {C['todo']},0 6px 22px rgba(217,118,6,.25);"
                    if is_active else "box-shadow:0 2px 8px rgba(0,0,0,.06);")
            badge = (f'<span style="color:{C["todo"]};font-weight:700;">◀ active</span>' if is_active
                     else ('<span style="color:var(--green);">✓ findings</span>' if has_find
                           else '<span style="color:var(--muted);">·</span>'))
            doors += (
                f'<div onclick="enterRoom(\'{slug}\',\'{nm}\')" '
                f'style="cursor:pointer;border:1px solid var(--border);border-radius:10px;'
                f'background:var(--surface);padding:0.8rem 0.9rem;{glow}transition:.15s;">'
                f'<div style="font-size:0.7rem;color:var(--muted);">stage {_h.escape(num)}</div>'
                f'<div style="font-weight:700;font-size:0.95rem;margin:0.15rem 0 0.4rem;">{_h.escape(title)}</div>'
                f'<div style="font-size:0.72rem;margin-bottom:0.35rem;">{badge}</div>'
                f'<div style="display:flex;gap:0.5rem;font-size:0.7rem;">'
                f'<span style="color:{C["ideas"]};">💜 {n_ideas}</span>'
                f'<span style="color:{C["todo"]};">▣ {n_todo}</span>'
                f'<span style="color:{C["findings"]};">{"✓" if has_find else "·"}</span>'
                f'<span style="color:{C["exhibits"]};">▦ {n_exhib}</span></div>'
                f'</div>')
        out.append(f'<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));'
                   f'gap:0.8rem;margin-bottom:1.5rem;">{doors}</div>')

        # ---- the rooms (hidden until a door is clicked) ----
        for room in rooms:
            nm = room.name
            title = nm.split("_", 1)[1].replace("_", " ").title() if "_" in nm else nm
            panels = ""
            for key, label, icon in [("ideas", "Ideas", "💜"), ("todo", "To-Do", "🟠"),
                                     ("findings", "Findings", "🟢"), ("exhibits", "Exhibits", "🟦")]:
                f = room / f"{key}.md"
                body = mini_md(f.read_text()) if f.exists() else '<p style="color:var(--muted);">empty</p>'
                panels += (
                    f'<div style="border-top:4px solid {C[key]};border-radius:8px;background:var(--surface);'
                    f'border:1px solid var(--border);border-top:4px solid {C[key]};padding:1rem 1.1rem;overflow:auto;">'
                    f'<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;'
                    f'font-weight:700;color:{C[key]};margin-bottom:0.6rem;">{icon} {label}</div>'
                    f'<div style="font-size:0.82rem;line-height:1.5;">{body}</div></div>')
            out.append(
                f'<div class="stage-room" id="room-{slug}-{nm}" style="display:none;">'
                f'<button onclick="exitRoom()" style="margin-bottom:0.9rem;padding:0.4rem 0.9rem;'
                f'border:1px solid var(--border);background:var(--surface);color:var(--text);'
                f'border-radius:6px;cursor:pointer;font-size:0.8rem;">← back to hallway</button>'
                f'<h3 style="margin-bottom:0.8rem;">Room {_h.escape(nm)}</h3>'
                f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;">{panels}</div></div>')

    js = ('<script>'
          'function enterRoom(s,n){document.querySelectorAll(".stage-room").forEach(function(r){r.style.display="none";});'
          'document.getElementById("stages-hall").style.display="none";'
          'var el=document.getElementById("room-"+s+"-"+n); if(el) el.style.display="block";}'
          'function exitRoom(){document.querySelectorAll(".stage-room").forEach(function(r){r.style.display="none";});'
          'document.getElementById("stages-hall").style.display="block";}'
          '</script>')
    # wrap the hallway (doors + slug headers) so we can hide/show it
    hall = "".join(x for x in out if 'class="stage-room"' not in x)
    rooms_html = "".join(x for x in out if 'class="stage-room"' in x)
    return f'{js}<div id="stages-hall">{hall}</div>{rooms_html}'


def render_todo():
    """Render TODO.md (the canonical open-work list). Reads at request time so it
    never drifts — same philosophy as the Reorient deck reading STATE.md."""
    tf = ROOT / "TODO.md"
    if not tf.exists():
        return '<p class="empty">No TODO.md found. Create it at the project root.</p>'
    text = tf.read_text()
    open_n = text.count("- [ ]")
    prog_n = text.count("- [~]")
    done_n = text.count("- [x]")
    chips = (f'<div class="todo-chips">'
             f'<span class="todo-chip chip-open">{open_n} open</span>'
             f'<span class="todo-chip chip-prog">{prog_n} in progress</span>'
             f'<span class="todo-chip chip-done">{done_n} done</span></div>')
    return chips + '<div class="todo-body">' + mini_md(text) + '</div>'


# =============================================================================
# PAGE ASSEMBLY
# =============================================================================

CSS = """
/* Dark theme (default) */
:root, :root[data-theme="dark"] {
  --bg:#0f1115; --surface:#1a1d23; --surface2:#22262e; --surface3:#2a2f38; --border:#333940;
  --text:#e8ecf0; --muted:#8892a0; --accent:#8b5cf6; --green:#34d399; --yellow:#fbbf24; --red:#f87171;
  --green-dim:rgba(52,211,153,0.12); --yellow-dim:rgba(251,191,36,0.12); --red-dim:rgba(248,113,113,0.12);
}
/* Light theme */
:root[data-theme="light"] {
  --bg:#fafafa; --surface:#ffffff; --surface2:#f3f4f6; --surface3:#e5e7eb; --border:#d1d5db;
  --text:#111827; --muted:#6b7280; --accent:#6d28d9; --green:#059669; --yellow:#b45309; --red:#dc2626;
  --green-dim:rgba(5,150,105,0.10); --yellow-dim:rgba(180,83,9,0.10); --red-dim:rgba(220,38,38,0.10);
}
@media (prefers-color-scheme: light) {
  :root:not([data-theme]) {
    --bg:#fafafa; --surface:#ffffff; --surface2:#f3f4f6; --surface3:#e5e7eb; --border:#d1d5db;
    --text:#111827; --muted:#6b7280; --accent:#6d28d9; --green:#059669; --yellow:#b45309; --red:#dc2626;
    --green-dim:rgba(5,150,105,0.10); --yellow-dim:rgba(180,83,9,0.10); --red-dim:rgba(220,38,38,0.10);
  }
}
.theme-toggle { display:flex; align-items:center; gap:0.4rem; padding:0.3rem 0.8rem; margin:0.4rem 0.8rem 0.4rem; font-size:0.65rem; background:var(--surface2); color:var(--muted); border:1px solid var(--border); border-radius:4px; cursor:pointer; width:calc(100% - 1.6rem); justify-content:center; }
.theme-toggle:hover { color:var(--text); border-color:var(--accent); }
.theme-toggle .theme-icon { font-size:0.8rem; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Inter',-apple-system,sans-serif; background:var(--bg); color:var(--text); display:flex; min-height:100vh; font-size:14px; line-height:1.6; }
nav { width:200px; background:var(--surface); border-right:1px solid var(--border); padding:1rem 0; flex-shrink:0; position:sticky; top:0; height:100vh; overflow-y:auto; }
nav .title { padding:0.8rem 1rem 0.3rem; font-weight:700; font-size:1rem; color:var(--accent); }
.project-switcher { display:flex; flex-wrap:wrap; gap:0.3rem; padding:0 0.8rem 0.8rem; border-bottom:1px solid var(--border); margin-bottom:0.5rem; }
.project-btn { font-size:0.6rem; padding:0.2rem 0.5rem; border-radius:4px; background:var(--surface2); color:var(--muted); cursor:pointer; border:1px solid var(--border); text-decoration:none; }
.project-btn.active { background:var(--accent); color:#fff; border-color:var(--accent); font-weight:600; }
.project-btn:hover:not(.active) { border-color:var(--accent); color:var(--text); }
.project-label { font-size:0.7rem; font-weight:600; padding:0.2rem 0.6rem; border-radius:4px; background:var(--accent); color:#fff; letter-spacing:0.03em; }
nav .group { padding:0.5rem 1rem 0.2rem; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.08em; margin-top:0.8rem; font-weight:600; }
nav .group-map { color:#c4b5fd; }
nav .group-checklist { color:#fbbf24; }
nav .group-evidence { color:#34d399; }
nav .group-machinery { color:#60a5fa; }
.cassette { display:block; width:max-content; max-width:100%; margin:2.2rem auto; font-family:ui-monospace, Menlo, monospace; line-height:1.05; color:var(--accent); font-size:clamp(0.62rem, 1.45vw, 1.25rem); white-space:pre; overflow-x:auto; text-align:left; }

/* Per-analysis checklist tab */
.checklist-tab { padding:0.2rem 0; }
.checklist-section { margin-bottom:2.2rem; }
.checklist-section-hdr { font-size:1rem; font-weight:600; color:var(--text); border-bottom:2px solid var(--accent); padding-bottom:0.4rem; margin-bottom:0.8rem; }
.checklist-help { color:var(--muted); font-size:0.75rem; margin-bottom:1rem; line-height:1.55; }
.checklist-help .legend { display:block; margin-top:0.4rem; font-size:0.7rem; }
.checklist-help .legend > span { display:inline-block; margin-right:0.5rem; }
.empty-loud { background:var(--surface); border:2px dashed var(--yellow); border-radius:8px; padding:1.5rem; color:var(--text); font-size:0.85rem; line-height:1.7; }
.empty-loud strong { color:var(--yellow); display:block; margin-bottom:0.4rem; font-size:0.95rem; }

/* Per-analysis grid */
.analysis-grid { width:100%; border-collapse:separate; border-spacing:0; font-size:0.78rem; }
.analysis-grid th { padding:0.4rem 0.4rem 0.5rem; border-bottom:1px solid var(--border); color:var(--muted); font-weight:600; font-size:0.65rem; text-align:center; vertical-align:bottom; }
.analysis-grid th:nth-child(-n+4) { text-align:left; }
.analysis-grid td { padding:0.5rem 0.4rem; border-bottom:1px solid var(--border); text-align:center; }
.analysis-grid td.slug-cell { text-align:left; font-family:'SF Mono',monospace; font-weight:600; }
.analysis-grid td.slug-cell a { color:var(--accent); text-decoration:none; }
.analysis-grid td.slug-cell a:hover { text-decoration:underline; }
.analysis-grid td.meta-cell { text-align:left; color:var(--muted); font-size:0.7rem; }
.step-num { font-size:0.7rem; font-weight:700; color:var(--text); }
.step-label { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.04em; }
/* THREE-COLOR "You Are Here" model: green=shut, red=open, amber=where you are (mall map).
   The color IS the lock state — a stage is done (locked), open, or the one you're in. */
.cell-done { color:var(--green); font-size:1.1rem; }               /* SHUT — locked / signed off */
.cell-open { color:var(--red); font-size:1.1rem; }                 /* OPEN — not locked, not active */
.cell-active { color:var(--amber, #C77A1A); font-size:1.15rem; animation:cellpulse 1.5s ease-in-out infinite; } /* YOU ARE HERE */
@keyframes cellpulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
/* legacy grade classes kept as aliases so any non-canister fallback still renders a sane color */
.cell-partial { color:var(--red); font-size:1.1rem; }
.cell-missing { color:var(--red); font-size:1.1rem; }
.cell-pending { color:var(--red); opacity:0.9; font-size:1.1rem; }
.status-in_progress { color:var(--yellow); }
.status-complete { color:var(--green); font-weight:600; }
.status-abandoned { color:var(--muted); text-decoration:line-through; }
.manifest-yes { color:var(--green); font-size:0.65rem; padding:0.1rem 0.4rem; background:var(--green-dim); border-radius:3px; }
.manifest-no { color:var(--red); font-size:0.65rem; padding:0.1rem 0.4rem; background:var(--red-dim); border-radius:3px; }

/* Package cards */
.pkg-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); gap:1rem; }
.pkg-card-container { perspective:1000px; cursor:pointer; min-height:180px; }
.pkg-card { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:1rem 1.2rem; min-height:180px; }
.pkg-card.pkg-green { border-color:var(--green); }
.pkg-card.pkg-red { border-color:var(--red); }
.pkg-card.pkg-unknown { border-color:var(--yellow); }
.pkg-name { font-family:'SF Mono',monospace; font-size:0.95rem; font-weight:700; color:var(--text); margin-bottom:0.3rem; }
.pkg-status { display:inline-block; font-size:0.6rem; padding:0.1rem 0.4rem; border-radius:3px; margin-bottom:0.5rem; font-weight:600; letter-spacing:0.04em; }
.pkg-status-green { color:var(--green); background:var(--green-dim); }
.pkg-status-red { color:var(--red); background:var(--red-dim); }
.pkg-status-unknown { color:var(--yellow); background:var(--yellow-dim); }
.pkg-row { font-size:0.72rem; color:var(--text); margin-bottom:0.25rem; line-height:1.5; }
.pkg-label { color:var(--muted); display:inline-block; min-width:80px; }
.pkg-row code { font-size:0.7rem; background:var(--surface2); padding:0.05rem 0.3rem; border-radius:3px; }
.pkg-section-hdr { font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--muted); margin-top:0.7rem; margin-bottom:0.3rem; font-weight:600; }
.pkg-drift { background:var(--yellow-dim); color:var(--yellow); font-size:0.68rem; padding:0.3rem 0.5rem; border-radius:3px; margin-top:0.4rem; }
.pkg-bugs ul { font-size:0.68rem; padding-left:1rem; line-height:1.6; }
.pkg-uses { display:inline-block; font-size:0.65rem; padding:0.1rem 0.4rem; background:var(--surface2); color:var(--muted); border-radius:3px; margin:0.1rem; font-family:'SF Mono',monospace; }
.pkg-card a { color:var(--accent); word-break:break-all; }
nav .btn { display:block; width:100%; text-align:left; padding:0.4rem 1rem; font-size:0.8rem; color:var(--muted); background:none; border:none; cursor:pointer; border-left:3px solid transparent; }
nav .btn:hover { color:var(--text); background:var(--surface2); }
nav .btn.active { color:var(--accent); border-left-color:var(--accent); background:var(--surface2); }
main { flex:1; padding:2rem; max-width:1100px; min-width:0; overflow-x:hidden; }
.view { display:none; } .view.active { display:block; }
h2 { font-size:1.2rem; margin-bottom:1rem; font-weight:600; }
.card { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem; margin-bottom:1rem; }
.status-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(130px,1fr)); gap:0.8rem; margin-bottom:1.5rem; }
.stat { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:0.8rem 1rem; text-align:center; }
.stat-val { font-size:1.4rem; font-weight:700; } .stat-lbl { font-size:0.7rem; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em; }
.stat-val.green { color:var(--green); } .stat-val.yellow { color:var(--yellow); } .stat-val.red { color:var(--red); }
.badge { display:inline-block; padding:0.15rem 0.5rem; border-radius:10px; font-size:0.65rem; font-weight:600; text-transform:uppercase; }
.badge.confirmed { background:var(--green-dim); color:var(--green); } .badge.testing { background:var(--yellow-dim); color:var(--yellow); }
.badge.complicated { background:var(--red-dim); color:var(--red); } .badge.fresh { background:var(--green-dim); color:var(--green); }
.badge.stale { background:var(--yellow-dim); color:var(--yellow); } .badge.missing { background:var(--red-dim); color:var(--red); }
.badge.done { background:var(--green-dim); color:var(--green); } .badge.partial { background:var(--yellow-dim); color:var(--yellow); }
.badge.todo { background:var(--surface2); color:var(--muted); } .badge.pending { background:var(--surface2); color:var(--muted); }
.court-stage { display:flex; gap:0.8rem; padding:0.8rem; background:var(--surface); border:1px solid var(--border); border-radius:6px; margin-bottom:0.6rem; }
.court-num { width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:700; flex-shrink:0; }
.court-num.done { background:var(--green-dim); color:var(--green); } .court-num.partial { background:var(--yellow-dim); color:var(--yellow); } .court-num.todo { background:var(--surface2); color:var(--muted); }
.court-label { font-weight:600; font-size:0.85rem; } .court-desc { font-size:0.75rem; color:var(--muted); }
.court-evidence { font-size:0.78rem; margin-top:0.3rem; padding:0.2rem 0; border-top:1px solid var(--border); }
.court-empty { font-size:0.72rem; color:var(--muted); font-style:italic; margin-top:0.3rem; }
.court-figures { display:flex; gap:0.5rem; margin-top:0.6rem; flex-wrap:wrap; }
.court-thumb { width:80px; height:55px; object-fit:cover; border-radius:4px; border:1px solid var(--border); cursor:pointer; transition:border-color 0.15s, transform 0.15s; }
.court-thumb:hover { border-color:var(--accent); transform:scale(1.05); }
.check-step { display:flex; gap:0.8rem; padding:0.7rem; background:var(--surface); border:1px solid var(--border); border-radius:6px; margin-bottom:0.5rem; align-items:center; }
.check-num { width:26px; height:26px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.7rem; font-weight:700; flex-shrink:0; }
.check-num.done { background:var(--green-dim); color:var(--green); } .check-num.partial { background:var(--yellow-dim); color:var(--yellow); }
.check-num.missing { background:var(--red-dim); color:var(--red); } .check-num.pending { background:var(--surface2); color:var(--muted); }
.check-name { font-weight:600; font-size:0.82rem; } .check-desc { font-size:0.72rem; color:var(--muted); }
.check-file { font-size:0.65rem; font-family:'SF Mono',monospace; color:var(--muted); } .check-file.exists { color:var(--green); } .check-file.missing { color:var(--red); }
.pipe-level { margin-bottom:1rem; } .pipe-level-hdr { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); padding:0.3rem 0.5rem; background:var(--surface2); border-radius:4px 4px 0 0; }
.pipe-item { display:flex; justify-content:space-between; align-items:center; padding:0.5rem 0.8rem; border:1px solid var(--border); border-top:none; font-size:0.8rem; }
.pipe-script { font-family:'SF Mono',monospace; font-size:0.75rem; }
.stale-section { margin-top:2rem; padding-top:1.5rem; border-top:1px solid var(--border); }
.stale-section h3 { font-size:0.9rem; margin-bottom:0.5rem; }
.stale-item { padding:0.6rem 0.8rem; border:1px solid var(--border); border-left:3px solid var(--yellow); border-radius:0 4px 4px 0; margin-bottom:0.5rem; background:var(--surface); }
.stale-header { display:flex; justify-content:space-between; align-items:center; }
.stale-date { font-size:0.7rem; color:var(--muted); }
.stale-path { font-size:0.65rem; color:var(--muted); font-family:'SF Mono',monospace; }
.stale-desc { font-size:0.72rem; color:var(--text); margin-top:0.2rem; }
.hyp-node { padding:0.8rem 1rem; border-left:3px solid var(--border); margin-bottom:0.5rem; background:var(--surface); border-radius:0 6px 6px 0; }
.hyp-node.confirmed { border-left-color:var(--green); } .hyp-node.testing { border-left-color:var(--yellow); } .hyp-node.complicated { border-left-color:var(--red); }
.hyp-node.child { margin-left:1.5rem; } .hyp-id { font-family:'SF Mono',monospace; color:var(--accent); font-size:0.8rem; margin-right:0.4rem; }
.hyp-header { font-size:0.85rem; } .hyp-claim { font-size:0.75rem; color:var(--muted); margin-top:0.3rem; }
table { width:100%; border-collapse:collapse; font-size:0.8rem; } th { text-align:left; padding:0.5rem; border-bottom:1px solid var(--border); color:var(--muted); font-size:0.7rem; text-transform:uppercase; }
td { padding:0.5rem; border-bottom:1px solid var(--border); }
.fig-grid { display:block; }
.fig-split { display:flex; height:calc(100vh - 150px); overflow:hidden; width:100%; }
.fig-list { width:220px; overflow-y:auto; background:var(--surface); border-right:1px solid var(--border); border-radius:6px 0 0 6px; flex-shrink:0; }
.fig-list-item { padding:0.4rem 0.8rem; font-size:0.72rem; font-family:'SF Mono',monospace; cursor:grab; color:var(--muted); border-bottom:1px solid var(--border); display:flex; align-items:center; gap:0.4rem; transition:background 0.1s; }
.fig-list-item:hover { background:var(--surface2); color:var(--text); }
.fig-list-item:active { cursor:grabbing; }
.fig-list-item.active { background:var(--surface2); color:var(--accent); border-left:3px solid var(--accent); }
.fig-list-item.drag-over-item { border-top:2px solid var(--accent); }
.fig-list-hdr { padding:0.4rem 0.8rem; font-size:0.6rem; text-transform:uppercase; letter-spacing:0.06em; font-weight:600; border-bottom:1px solid var(--border); }
.fig-list-hdr.pipe { color:var(--green); } .fig-list-hdr.review { color:var(--yellow); } .fig-list-hdr.sandbox { color:var(--muted); }
.fig-main { flex:1; overflow-y:auto; overflow-x:hidden; padding:1rem; min-width:0; }
.fig-flip-container { perspective:1000px; cursor:pointer; }
.fig-flip-inner { position:relative; transition:transform 0.5s; transform-style:preserve-3d; }
.fig-flip-container.flipped .fig-flip-inner { transform:rotateY(180deg); }
.fig-front, .fig-back { backface-visibility:hidden; }
.fig-back { position:absolute; top:0; left:0; width:100%; height:100%; transform:rotateY(180deg); overflow-y:auto; padding:1rem; }
.fig-back-header { font-weight:600; font-size:0.85rem; margin-bottom:0.3rem; }
.fig-caption { font-size:0.78rem; color:var(--text); line-height:1.5; margin-bottom:0.6rem; padding:0.5rem 0.6rem; background:rgba(139,92,246,0.06); border-left:3px solid var(--accent); border-radius:0 4px 4px 0; }
.fig-back-script { font-family:'SF Mono',monospace; font-size:0.75rem; color:var(--accent); margin-bottom:0.5rem; }
.fig-back-action { font-size:0.75rem; color:var(--green); cursor:pointer; margin-bottom:0.8rem; }
.fig-back-action:hover { text-decoration:underline; }
.fig-back-stage { font-size:0.7rem; color:var(--accent); margin-bottom:0.4rem; font-weight:500; }
.fig-back-meta { font-size:0.7rem; color:var(--muted); line-height:1.6; }
.tier-buttons { display:flex; gap:0.4rem; margin-top:0.8rem; }
.tier-btn { background:var(--surface2); border:1px solid var(--border); border-radius:4px; color:var(--muted); font-size:0.65rem; padding:0.25rem 0.5rem; cursor:pointer; transition:all 0.15s; }
.tier-btn:hover { border-color:var(--accent); color:var(--text); }
.tier-btn.tier-active { background:var(--accent); border-color:var(--accent); color:#fff; font-weight:600; }
.tier-dot { width:8px; height:8px; border-radius:50%; display:inline-block; vertical-align:middle; margin-left:0.3rem; }
.tier-dot.tier-approved { background:var(--green); }
.tier-dot.tier-review { background:var(--yellow); }
.tier-dot.tier-sandbox { background:var(--muted); }
.fig-card { background:var(--surface); border:1px solid var(--border); border-radius:6px; overflow:hidden; }
.fig-card.fresh { border-color:var(--green); } .fig-card.stale { border-color:var(--yellow); } .fig-card.orphaned { border-color:var(--muted); }
.fig-card img { display:block; width:100%; max-width:620px; max-height:70vh; object-fit:contain; }
.fig-flip-container { max-width:620px; cursor:pointer; }
.fig-name { padding:0.4rem 0.6rem; font-size:0.75rem; font-weight:600; } .fig-meta { padding:0 0.6rem 0.2rem; font-size:0.65rem; color:var(--muted); }
.fig-no-desc { background:var(--red); color:#fff; font-size:0.55rem; padding:0.1rem 0.3rem; border-radius:50%; margin-left:0.3rem; font-weight:700; }
.fig-desc-needed { font-size:0.75rem; color:var(--red); font-style:italic; margin-bottom:0.5rem; padding:0.4rem 0.6rem; background:rgba(248,113,113,0.08); border-radius:4px; }
.data-card { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:1rem; margin-bottom:0.8rem; }
.data-header { display:flex; justify-content:space-between; align-items:center; }
.data-name { font-weight:600; font-size:0.85rem; font-family:'SF Mono',monospace; }
.data-desc { font-size:0.78rem; color:var(--text); margin-top:0.4rem; line-height:1.5; }
.data-meta { font-size:0.7rem; color:var(--muted); margin-top:0.3rem; }
.data-used { font-size:0.72rem; color:var(--muted); margin-top:0.4rem; }
.data-script { background:var(--surface2); padding:0.1rem 0.4rem; border-radius:3px; font-family:'SF Mono',monospace; font-size:0.65rem; margin-right:0.3rem; }
.data-figs { font-size:0.72rem; color:var(--muted); margin-top:0.3rem; }
.data-fig { background:var(--accent);background:rgba(139,92,246,0.15); color:var(--accent); padding:0.1rem 0.4rem; border-radius:3px; font-size:0.65rem; margin-right:0.3rem; }
.data-preview { background:var(--surface2); border:1px solid var(--border); border-radius:4px; padding:0.5rem 0.7rem; margin-top:0.5rem; font-family:'SF Mono',monospace; font-size:0.65rem; line-height:1.5; overflow-x:auto; color:var(--muted); max-height:6rem; overflow-y:auto; }
.table-grid { display:grid; grid-template-columns:1fr; gap:1.5rem; }
.table-card { background:var(--surface); border:1px solid var(--border); border-radius:8px; padding:1.2rem 1.5rem; overflow-x:auto; }
.table-title { font-weight:600; font-size:0.85rem; margin-bottom:1rem; color:var(--accent); font-family:'SF Mono',monospace; letter-spacing:0.02em; }
.rendered-table { width:100%; border-collapse:separate; border-spacing:0; font-size:0.8rem; }
.rendered-table th { text-align:left; padding:0.6rem 0.8rem; border-bottom:2px solid var(--accent); color:var(--text); font-weight:600; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.04em; }
.rendered-table td { padding:0.5rem 0.8rem; border-bottom:1px solid var(--border); color:var(--text); transition:background 0.1s; }
.rendered-table tr:hover td { background:rgba(139,92,246,0.06); }
.rendered-table tr:last-child td { border-bottom:none; }
.rendered-table td:first-child { font-weight:500; }
.table-raw { font-size:0.72rem; color:var(--muted); line-height:1.6; max-height:400px; overflow-y:auto; background:var(--surface2); padding:0.8rem; border-radius:4px; }
.code-split { display:flex; height:70vh; border:1px solid var(--border); border-radius:6px; overflow:hidden; }
.code-list { width:220px; overflow-y:auto; background:var(--surface); border-right:1px solid var(--border); }
.code-item { padding:0.4rem 0.8rem; font-size:0.75rem; font-family:'SF Mono',monospace; cursor:pointer; color:var(--muted); display:flex; justify-content:space-between; align-items:center; } .code-item:hover { background:var(--surface2); color:var(--text); }
.code-section-hdr { padding:0.4rem 0.8rem; font-size:0.65rem; text-transform:uppercase; letter-spacing:0.06em; font-weight:600; }
.pipeline-hdr { color:var(--green); border-bottom:1px solid var(--border); }
.stale-hdr { color:var(--yellow); border-top:1px solid var(--border); border-bottom:1px solid var(--border); margin-top:0.5rem; }
.code-badge { width:8px; height:8px; border-radius:50%; display:inline-block; }
.code-badge.fresh { background:var(--green); } .code-badge.stale { background:var(--yellow); }
.code-item.stale-code { border-left:2px solid var(--yellow); }
.code-view { flex:1; overflow:auto; padding:1rem; background:var(--surface2); }
#code-path { font-size:0.7rem; color:var(--accent); margin-bottom:0.5rem; font-family:'SF Mono',monospace; }
#code-body { font-family:'SF Mono','Fira Code',monospace; font-size:0.72rem; line-height:1.8; white-space:pre; }
.code-line { display:inline; }
.line-num { display:inline-block; width:3.5em; text-align:right; margin-right:1em; color:var(--border); user-select:none; }
.insight-date { font-size:0.7rem; color:var(--muted); } .finding { font-size:0.8rem; color:var(--muted); margin-top:0.4rem; }
.date { font-size:0.7rem; color:var(--muted); }
.empty { color:var(--muted); font-style:italic; }
.narr-section { margin-bottom:1.5rem; } .narr-section h3 { font-size:0.95rem; margin-bottom:0.5rem; color:var(--accent); }
.narr-section ul { list-style:none; padding:0; } .narr-section li { padding:0.4rem 0; border-bottom:1px solid var(--border); font-size:0.82rem; line-height:1.5; }
.narrative-auto { max-width:700px; }
.reorient-banner { background:linear-gradient(135deg, rgba(139,92,246,0.08), rgba(96,165,250,0.08)); border:1px solid var(--border); border-radius:8px; padding:1rem 1.2rem; margin-bottom:1.5rem; font-size:0.8rem; line-height:1.6; color:var(--text); }
.reorient-banner strong { color:var(--accent); }
.todo-chips { display:flex; gap:0.6rem; margin-bottom:1.2rem; }
.todo-chip { font-size:0.72rem; font-weight:600; padding:0.25rem 0.7rem; border-radius:999px; border:1px solid var(--border); }
.todo-chip.chip-open { background:var(--yellow-dim); color:var(--yellow); }
.todo-chip.chip-prog { background:rgba(139,92,246,0.12); color:var(--accent); }
.todo-chip.chip-done { background:var(--green-dim); color:var(--green); }
.todo-body { max-width:62rem; }

/* ===== Rituals tab — Arrival / Departure checklists ===== */
.ritual-banner { background:linear-gradient(135deg, rgba(139,92,246,0.06), rgba(34,211,153,0.05)); border:1px solid var(--border); border-radius:8px; padding:1rem 1.3rem; margin-bottom:1.6rem; font-size:0.82rem; line-height:1.65; color:var(--text); }
.ritual-banner strong { color:var(--accent); font-weight:600; }
.ritual-banner code { background:var(--surface2); padding:0.05rem 0.3rem; border-radius:3px; font-size:0.85em; }
.ritual-grid { display:grid; grid-template-columns:1fr 1fr; gap:1.6rem; align-items:start; margin-bottom:2rem; }
@media (max-width: 1100px) { .ritual-grid { grid-template-columns:1fr; } }
.ritual-card { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:1.6rem 1.8rem 1.2rem; box-shadow:0 1px 3px rgba(0,0,0,0.04); position:relative; }
.ritual-arrival { border-top:3px solid var(--green); }
.ritual-departure { border-top:3px solid var(--accent); }
.ritual-header { padding-bottom:1.1rem; border-bottom:1px solid var(--border); margin-bottom:1.2rem; }
.ritual-eyebrow { display:block; font-family:'Inter',-apple-system,sans-serif; font-size:0.65rem; font-weight:500; letter-spacing:0.16em; text-transform:uppercase; color:var(--muted); margin-bottom:0.4rem; }
.ritual-title { font-family:'Cormorant Garamond',Georgia,serif; font-size:2.4rem; font-weight:500; line-height:1.05; color:var(--text); margin:0 0 0.5rem; letter-spacing:-0.005em; }
.ritual-arrival .ritual-title { color:var(--green); }
.ritual-departure .ritual-title { color:var(--accent); }
.ritual-lede { font-family:'Cormorant Garamond',Georgia,serif; font-size:1.05rem; font-style:italic; color:var(--muted); margin:0; line-height:1.4; }
.ritual-list { list-style:none; padding:0; margin:0; }
.ritual-item { display:block; margin-bottom:1.2rem; }
.ritual-item:last-child { margin-bottom:0.4rem; }
.ritual-check { position:absolute; opacity:0; pointer-events:none; }
.ritual-label { display:flex; gap:1rem; align-items:flex-start; cursor:pointer; padding:0.6rem 0.7rem 0.6rem 0.5rem; border-radius:6px; transition:background 0.15s ease, opacity 0.2s ease; }
.ritual-label:hover { background:var(--surface2); }
.ritual-num { flex:0 0 1.8rem; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.6rem; font-weight:500; line-height:1; color:var(--muted); padding-top:0.05rem; transition:color 0.15s ease; position:relative; }
.ritual-num::before { content:''; position:absolute; left:-0.4rem; top:0.2rem; width:1.05rem; height:1.05rem; border:1.5px solid var(--border); border-radius:3px; background:var(--bg); transition:all 0.18s ease; }
.ritual-check:checked + .ritual-label .ritual-num::before { background:var(--green); border-color:var(--green); }
.ritual-arrival .ritual-check:checked + .ritual-label .ritual-num::before { background:var(--green); border-color:var(--green); }
.ritual-departure .ritual-check:checked + .ritual-label .ritual-num::before { background:var(--accent); border-color:var(--accent); }
.ritual-check:checked + .ritual-label .ritual-num::after { content:'\\2713'; position:absolute; left:-0.32rem; top:0.05rem; font-family:'Inter',-apple-system,sans-serif; font-size:0.85rem; font-weight:700; color:#fff; line-height:1; }
.ritual-body { display:flex; flex-direction:column; gap:0.35rem; flex:1; }
.ritual-directive { font-family:'Cormorant Garamond',Georgia,serif; font-size:1.25rem; font-weight:500; line-height:1.35; color:var(--text); transition:color 0.18s ease; }
.ritual-why { font-family:'Inter',-apple-system,sans-serif; font-size:0.78rem; line-height:1.6; color:var(--muted); }
.ritual-check:checked + .ritual-label .ritual-directive { color:var(--muted); text-decoration:line-through; text-decoration-thickness:1px; text-decoration-color:rgba(136,146,160,0.4); }
.ritual-check:checked + .ritual-label .ritual-num { color:var(--muted); }
.ritual-check:focus-visible + .ritual-label { outline:2px solid var(--accent); outline-offset:2px; }
.ritual-footer { display:flex; justify-content:space-between; align-items:center; margin-top:1.4rem; padding-top:0.9rem; border-top:1px solid var(--border); }
.ritual-progress { font-family:'Cormorant Garamond',Georgia,serif; font-style:italic; font-size:0.95rem; color:var(--muted); }
.ritual-progress.complete { color:var(--green); font-weight:500; font-style:normal; }
.ritual-departure .ritual-progress.complete { color:var(--accent); }
.ritual-reset { font-family:'Inter',-apple-system,sans-serif; font-size:0.65rem; letter-spacing:0.1em; text-transform:uppercase; color:var(--muted); background:transparent; border:1px solid var(--border); padding:0.35rem 0.8rem; border-radius:4px; cursor:pointer; transition:all 0.15s ease; }
.ritual-reset:hover { color:var(--text); border-color:var(--accent); }
.ritual-footnote { font-size:0.7rem; color:var(--muted); line-height:1.65; padding-top:0.8rem; border-top:1px dashed var(--border); }
.ritual-footnote em { font-style:italic; color:var(--text); margin-right:0.2rem; }
/* Inline STATE.md panel inside the Arrival card. Reading should be one glance,
   not a context-switch — show the file, don't just point at it. */
.state-panel { margin:-0.4rem 0 1.4rem; border:1px solid var(--border); border-radius:8px; background:var(--surface2); overflow:hidden; }
.state-panel[open] { background:var(--bg); }
.state-summary { display:flex; align-items:center; gap:0.7rem; cursor:pointer; padding:0.7rem 1rem; font-family:'Inter',-apple-system,sans-serif; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); user-select:none; list-style:none; }
.state-summary::-webkit-details-marker { display:none; }
.state-summary::before { content:'\\25B8'; font-size:0.65rem; color:var(--muted); transition:transform 0.18s ease; transform:rotate(0deg); flex:0 0 auto; }
.state-panel[open] .state-summary::before { transform:rotate(90deg); }
.state-summary:hover { color:var(--text); }
.state-summary-label { font-weight:600; color:var(--text); letter-spacing:0.04em; }
.state-panel[open] .state-summary-label { color:var(--accent); }
.state-summary-hint { margin-left:auto; font-size:0.6rem; font-weight:400; color:var(--muted); letter-spacing:0.05em; opacity:0.7; }
.state-fresh-chip { display:inline-flex; align-items:center; padding:0.15rem 0.55rem; border-radius:10px; font-family:'Inter',-apple-system,sans-serif; font-size:0.6rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; }
.state-fresh-fresh { background:var(--green-dim); color:var(--green); border:1px solid var(--green); }
.state-fresh-aging { background:var(--yellow-dim); color:var(--yellow); border:1px solid var(--yellow); }
.state-fresh-stale { background:var(--red-dim); color:var(--red); border:1px solid var(--red); }
.state-missing-chip { background:var(--red-dim); color:var(--red); border:1px solid var(--red); }
.state-body { padding:0.4rem 1.4rem 1.4rem; max-height:48vh; overflow-y:auto; border-top:1px solid var(--border); }
.state-body::-webkit-scrollbar { width:6px; }
.state-body::-webkit-scrollbar-track { background:transparent; }
.state-body::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
.state-body .state-h2 { font-family:'Cormorant Garamond',Georgia,serif; font-size:1.45rem; font-weight:500; color:var(--accent); margin:1.2rem 0 0.5rem; line-height:1.15; }
.state-body .state-h2:first-child { margin-top:0.6rem; }
.state-body .state-h3 { font-family:'Cormorant Garamond',Georgia,serif; font-size:1.18rem; font-weight:500; color:var(--text); margin:1rem 0 0.4rem; line-height:1.2; }
.state-body .state-h4 { font-family:'Inter',-apple-system,sans-serif; font-size:0.78rem; font-weight:600; letter-spacing:0.05em; text-transform:uppercase; color:var(--muted); margin:0.9rem 0 0.4rem; }
.state-body .state-p { font-size:0.8rem; line-height:1.62; color:var(--text); margin:0.5rem 0; }
.state-body .state-ul, .state-body .state-ol { font-size:0.8rem; line-height:1.6; color:var(--text); margin:0.4rem 0 0.6rem 1.1rem; padding:0; }
.state-body .state-ul li, .state-body .state-ol li { margin:0.32rem 0; }
.state-body code { background:var(--surface2); color:var(--accent); padding:0.05rem 0.35rem; border-radius:3px; font-family:'SF Mono',monospace; font-size:0.85em; }
.state-body strong { color:var(--text); font-weight:600; }
.state-body em { color:var(--muted); font-style:italic; }
.state-body .state-hr { border:0; border-top:1px solid var(--border); margin:1rem 0; }
.state-missing { padding:1rem 1.4rem 1.4rem; font-size:0.78rem; color:var(--red); font-style:italic; }
/* Today's-objective callout — large pull from STATE.md §2 sitting at the
   very top of the Arrival card. Sets intent before any check. */
.ritual-objective { margin:-0.4rem 0 1.3rem; padding:1.1rem 1.3rem; background:linear-gradient(135deg, rgba(52,211,153,0.08), rgba(139,92,246,0.05)); border-left:3px solid var(--green); border-radius:6px; }
.ritual-objective-eyebrow { font-family:'Inter',-apple-system,sans-serif; font-size:0.62rem; font-weight:600; letter-spacing:0.14em; text-transform:uppercase; color:var(--green); margin-bottom:0.45rem; }
.ritual-objective-text { font-family:'Cormorant Garamond',Georgia,serif; font-size:1.4rem; font-weight:500; line-height:1.32; color:var(--text); }
.ritual-objective-text strong { font-weight:600; color:var(--text); }
.ritual-objective-text code { background:rgba(139,92,246,0.12); color:var(--accent); padding:0.05rem 0.35rem; border-radius:3px; font-family:'SF Mono',monospace; font-size:0.75em; vertical-align:0.05em; }
.ritual-objective-source { margin-top:0.7rem; font-size:0.68rem; color:var(--muted); line-height:1.55; font-style:italic; }
.ritual-objective-source code { font-style:normal; }
/* Most-recent-audit panel — collapsible, sits below STATE.md panel */
.audit-panel { margin:0.8rem 0 1.4rem; border:1px solid var(--border); border-radius:8px; background:var(--surface2); overflow:hidden; }
.audit-panel[open] { background:var(--bg); }
.audit-summary { display:flex; align-items:center; gap:0.7rem; cursor:pointer; padding:0.7rem 1rem; font-family:'Inter',-apple-system,sans-serif; font-size:0.7rem; letter-spacing:0.05em; color:var(--muted); user-select:none; list-style:none; flex-wrap:wrap; }
.audit-summary::-webkit-details-marker { display:none; }
.audit-summary::before { content:'\\25B8'; font-size:0.65rem; color:var(--muted); transition:transform 0.18s ease; flex:0 0 auto; }
.audit-panel[open] .audit-summary::before { transform:rotate(90deg); }
.audit-summary:hover { color:var(--text); }
.audit-summary-label { font-weight:600; color:var(--text); letter-spacing:0.04em; text-transform:uppercase; font-size:0.62rem; }
.audit-summary-meta { font-size:0.68rem; color:var(--muted); }
.audit-summary-meta code { background:transparent; color:var(--muted); padding:0; font-family:'SF Mono',monospace; }
.audit-verdict { padding:0.85rem 1.4rem; font-family:'Cormorant Garamond',Georgia,serif; font-size:1.15rem; font-weight:500; line-height:1.4; color:var(--accent); border-top:1px solid var(--border); background:var(--surface); }
.audit-body { padding:0.4rem 1.4rem 1.4rem; max-height:42vh; overflow-y:auto; border-top:1px solid var(--border); }
.audit-body::-webkit-scrollbar { width:6px; }
.audit-body::-webkit-scrollbar-thumb { background:var(--border); border-radius:3px; }
.audit-body .state-h2, .audit-body .state-h3 { font-family:'Cormorant Garamond',Georgia,serif; color:var(--accent); margin:1rem 0 0.4rem; }
.audit-body .state-h2 { font-size:1.25rem; font-weight:500; }
.audit-body .state-h3 { font-size:1.05rem; font-weight:500; color:var(--text); }
.audit-body .state-h4 { font-family:'Inter',-apple-system,sans-serif; font-size:0.72rem; font-weight:600; letter-spacing:0.04em; text-transform:uppercase; color:var(--muted); margin:0.7rem 0 0.3rem; }
.audit-body .state-p { font-size:0.78rem; line-height:1.6; color:var(--text); margin:0.4rem 0; }
.audit-body .state-ul, .audit-body .state-ol { font-size:0.78rem; line-height:1.55; margin:0.4rem 0 0.6rem 1.1rem; padding:0; }
.audit-body code { background:var(--surface2); color:var(--accent); padding:0.05rem 0.35rem; border-radius:3px; font-family:'SF Mono',monospace; font-size:0.85em; }
.audit-body strong { color:var(--text); font-weight:600; }
.audit-body em { color:var(--muted); font-style:italic; }
.audit-body .state-hr { border:0; border-top:1px solid var(--border); margin:0.9rem 0; }
/* Departure-side health counters — three chips: stale figures, drift events, audits today */
.ritual-health { display:grid; grid-template-columns:1fr 1fr 1fr; gap:0.7rem; margin:-0.3rem 0 1.3rem; }
.ritual-health-chip { padding:0.85rem 0.7rem; border-radius:8px; text-align:center; border:1px solid var(--border); background:var(--surface2); }
.ritual-health-chip.chip-ok { border-color:var(--green); background:var(--green-dim); }
.ritual-health-chip.chip-warn { border-color:var(--yellow); background:var(--yellow-dim); }
.ritual-health-chip.chip-bad { border-color:var(--red); background:var(--red-dim); }
.ritual-health-chip .chip-num { font-family:'Cormorant Garamond',Georgia,serif; font-size:1.9rem; font-weight:500; line-height:1; margin-bottom:0.2rem; color:var(--text); }
.ritual-health-chip.chip-ok .chip-num { color:var(--green); }
.ritual-health-chip.chip-warn .chip-num { color:var(--yellow); }
.ritual-health-chip.chip-bad .chip-num { color:var(--red); }
.ritual-health-chip .chip-label { font-family:'Inter',-apple-system,sans-serif; font-size:0.6rem; font-weight:500; letter-spacing:0.08em; text-transform:uppercase; color:var(--muted); }
.narr-warning { background:rgba(248,113,113,0.1); border:1px solid var(--red); border-radius:6px; padding:0.8rem 1rem; margin-bottom:1.5rem; font-size:0.8rem; }
.narr-warning strong { color:var(--red); }
.narr-warning ul { margin-top:0.4rem; padding-left:1rem; }
.narr-warning li { font-size:0.75rem; margin:0.2rem 0; }
.narr-badge { display:inline-block; padding:0.1rem 0.4rem; border-radius:8px; font-size:0.6rem; font-weight:600; text-transform:uppercase; vertical-align:middle; margin-left:0.2rem; }
.narr-badge.confirmed { background:var(--green-dim); color:var(--green); }
.narr-badge.testing { background:var(--yellow-dim); color:var(--yellow); }
.narr-badge.complicated { background:var(--red-dim); color:var(--red); cursor:pointer; }
.narr-badge.testing { cursor:pointer; }
.narr-badge.conjecture { background:var(--surface2); color:var(--muted); }
.narr-reason { display:none; font-size:0.72rem; color:var(--red); font-style:italic; background:var(--surface2); padding:0.3rem 0.6rem; border-radius:4px; margin-left:0.3rem; }
.narr-reason.open { display:inline; }
.badge-contested { background:rgba(248,113,113,0.15); color:var(--red); font-size:0.6rem; padding:0.1rem 0.4rem; border-radius:8px; font-weight:500; margin-left:0.3rem; }
.narrative-prose { max-width:700px; font-size:0.85rem; line-height:1.8; }
.narrative-prose h2 { font-size:1rem; margin-top:2.5rem; margin-bottom:0.8rem; color:var(--accent); padding-top:1.5rem; border-top:1px solid var(--border); }
.narrative-prose h2:first-child { margin-top:0; padding-top:0; border-top:none; }
.narrative-prose h3 { font-size:0.9rem; margin-top:1.5rem; margin-bottom:0.5rem; color:var(--text); }
.narrative-prose p { margin-bottom:1rem; }
.narrative-prose strong { color:var(--text); }
.narr-section-block { margin-bottom:2rem; padding-bottom:1.5rem; border-bottom:1px solid var(--border); }
.narr-section-block:last-child { border-bottom:none; }
.fig-link { color:var(--accent); cursor:pointer; font-size:0.78rem; text-decoration:none; border-bottom:1px dotted var(--accent); }
.fig-link:hover { color:var(--green); border-bottom-color:var(--green); }
.next-actions { padding-left:1.2rem; } .next-actions li { font-size:0.82rem; padding:0.3rem 0; line-height:1.5; }
.inbox-item { padding:0.6rem; border-left:3px solid var(--accent); background:var(--surface2); border-radius:0 4px 4px 0; margin-bottom:0.5rem; }
.inbox-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.2rem; }
.inbox-from { font-size:0.72rem; font-weight:600; color:var(--accent); }
.inbox-body { font-size:0.78rem; color:var(--text); }
.inbox-action { font-size:0.72rem; color:var(--green); margin-top:0.3rem; font-style:italic; }
.someday-item { font-size:0.75rem; color:var(--muted); padding:0.4rem 0; border-bottom:1px solid var(--border); }
.audit-card { padding:0.7rem; border:1px solid var(--border); border-radius:6px; margin-bottom:0.6rem; cursor:pointer; transition:background 0.1s; }
.audit-card:hover { background:var(--surface2); }
.audit-header { display:flex; justify-content:space-between; align-items:center; }
.audit-topic { font-weight:600; font-size:0.82rem; }
.audit-conclusion { font-size:0.75rem; color:var(--muted); margin-top:0.2rem; }
.audit-body { display:none; margin-top:0.5rem; padding-top:0.5rem; border-top:1px solid var(--border); font-size:0.75rem; color:var(--text); line-height:1.5; }
.audit-body.open { display:block; }
.voice-card { background:var(--surface); border:1px solid var(--border); border-radius:6px; padding:1rem; margin-bottom:1rem; }
.voice-name { font-size:1rem; font-weight:700; color:var(--accent); margin-bottom:0.5rem; }
.voice-moves { list-style:none; padding:0; } .voice-moves li { font-size:0.8rem; padding:0.3rem 0; border-bottom:1px solid var(--border); line-height:1.5; }
.voice-moves li:last-child { border-bottom:none; }
.voice-file { font-size:0.65rem; color:var(--muted); font-family:'SF Mono',monospace; margin-top:0.5rem; }
.skill-section-hdr { font-size:0.7rem; text-transform:uppercase; letter-spacing:0.06em; color:var(--accent); font-weight:600; margin-bottom:0.5rem; }
.skill-card { padding:0.7rem 1rem; border:1px solid var(--border); border-radius:6px; margin-bottom:0.5rem; background:var(--surface); }
.skill-name { font-family:'SF Mono',monospace; font-size:0.85rem; font-weight:600; color:var(--accent); }
.skill-hint { font-weight:normal; color:var(--muted); font-size:0.7rem; }
.skill-desc { font-size:0.75rem; color:var(--text); margin-top:0.2rem; line-height:1.4; }
/* Lightbox */
#lightbox-overlay { display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:9999; align-items:center; justify-content:center; }
.lb-backdrop { position:absolute; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); }
.lb-content { position:relative; z-index:1; max-width:90vw; max-height:90vh; text-align:center; }
.lb-flip-container { perspective:1200px; cursor:pointer; display:inline-block; }
.lb-flip-inner { position:relative; transition:transform 0.5s; transform-style:preserve-3d; }
.lb-flip-container.flipped .lb-flip-inner { transform:rotateY(180deg); }
.lb-front, .lb-back { backface-visibility:hidden; }
.lb-back { position:absolute; top:0; left:0; width:100%; height:100%; transform:rotateY(180deg); background:var(--surface); border-radius:8px; padding:1.5rem; overflow-y:auto; text-align:left; max-height:82vh; }
.lb-back-title { font-size:1rem; font-weight:600; margin-bottom:0.8rem; color:var(--text); }
.lb-back-body { font-size:0.8rem; color:var(--text); }
.lb-back-body .fig-back-header { font-size:0.95rem; font-weight:600; margin-bottom:0.5rem; }
.lb-back-body .fig-caption { margin:0.5rem 0; line-height:1.5; }
.lb-back-body .fig-back-script { font-family:'SF Mono',monospace; font-size:0.75rem; color:var(--muted); margin:0.3rem 0; }
.lb-back-body .fig-back-meta { font-size:0.7rem; color:var(--muted); margin-top:0.5rem; }
.lb-back-body .tier-buttons { margin-top:0.8rem; }
.lb-img { max-width:90vw; max-height:78vh; border-radius:8px; box-shadow:0 8px 32px rgba(0,0,0,0.6); }
.lb-title { color:#fff; font-size:0.85rem; margin-top:0.7rem; font-weight:500; }
.lb-hint { color:rgba(255,255,255,0.4); font-size:0.65rem; margin-top:0.3rem; }
/* Courtroom hypothesis badges */
.court-hyps { margin:0.3rem 0 0.5rem; display:flex; flex-wrap:wrap; gap:0.4rem; }
.court-hyp-badge { font-size:0.68rem; padding:0.15rem 0.5rem; border-radius:4px; background:var(--surface); border:1px solid var(--border); display:inline-flex; align-items:center; gap:0.3rem; font-family:'SF Mono',monospace; }
.court-hyp-badge .badge { font-size:0.6rem; padding:0.05rem 0.3rem; }
/* Drift warning links */
.drift-link { color:var(--accent); cursor:pointer; text-decoration:underline; font-family:'SF Mono',monospace; font-weight:600; }
.drift-link:hover { color:#fff; }
/* Hypothesis evidence section */
.hyp-evidence { margin:0.4rem 0 0.2rem 1rem; border-left:2px solid var(--border); padding-left:0.6rem; }
.hyp-ev-item { font-size:0.72rem; margin-bottom:0.3rem; display:flex; align-items:center; gap:0.4rem; flex-wrap:wrap; }
.hyp-ev-item .date { color:var(--muted); font-size:0.65rem; }
.hyp-thumb { width:48px; height:32px; object-fit:cover; border-radius:3px; cursor:pointer; border:1px solid var(--border); margin-left:0.3rem; }
.hyp-thumb:hover { border-color:var(--accent); transform:scale(1.1); }
/* Figure expand button */
.fig-expand { float:right; font-size:0.75rem; color:var(--muted); cursor:pointer; padding:0 0.3rem; }
.fig-expand:hover { color:var(--accent); }
/* ---- Dataset flip cards + fullscreen modal (Scott, 2026-06-19) ---- */
.ds-grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:0.9rem; }
.ds-card { background:var(--surface); border:1px solid var(--border); border-radius:10px; padding:0.9rem 1rem; cursor:pointer; transition:transform .12s, border-color .12s, box-shadow .12s; display:flex; flex-direction:column; min-height:128px; }
.ds-card:hover { transform:translateY(-3px); border-color:var(--accent); box-shadow:0 8px 24px rgba(0,0,0,.18); }
.ds-card-top { display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem; }
.ds-tag { width:10px; height:10px; border-radius:50%; display:inline-block; }
.ds-tag-v { background:var(--green); } .ds-tag-w { background:var(--yellow); } .ds-tag-n { background:var(--muted); }
.ds-status { font-size:0.6rem; padding:0.1rem 0.45rem; border-radius:10px; font-weight:600; }
.ds-status.ds-fresh { background:var(--green-dim); color:var(--green); } .ds-status.ds-missing { background:var(--surface2); color:var(--muted); }
.ds-card-name { font-weight:700; font-size:0.92rem; line-height:1.2; color:var(--text); }
.ds-card-role { font-size:0.66rem; color:var(--accent); margin-top:0.25rem; text-transform:uppercase; letter-spacing:0.04em; font-weight:600; }
.ds-card-src { font-size:0.68rem; color:var(--muted); margin-top:0.4rem; line-height:1.35; flex:1; }
.ds-card-hint { font-size:0.6rem; color:var(--muted); margin-top:0.5rem; opacity:0.7; }
/* pin-to-stage control (Scott, 2026-07-28) */
.ds-card-foot { position:relative; margin-top:0.4rem; display:flex; flex-direction:column; gap:0.2rem; }
.pin-btn { font-size:0.62rem; padding:0.2rem 0.5rem; border:1px solid var(--border,#d0d7de); border-radius:6px; background:var(--surface,#f6f8fa); color:var(--ink,#333); cursor:pointer; align-self:flex-start; }
.pin-btn:hover { background:#1f6feb; color:#fff; border-color:#1f6feb; }
.pin-status { font-size:0.6rem; line-height:1.3; }
.pin-ok { color:#1a7f37; } .pin-warn { color:#9a6700; }
.pin-current { display:flex; flex-wrap:wrap; gap:0.2rem; margin-bottom:0.25rem; }
.pin-chip { font-size:0.58rem; padding:0.12rem 0.4rem; border-radius:10px; background:#1a7f3718; border:1px solid #1a7f3755; color:#1a7f37; white-space:nowrap; }
.pin-menu { position:absolute; top:100%; left:0; z-index:50; margin-top:2px; max-height:240px; overflow:auto; background:var(--surface,#fff); border:1px solid var(--border,#d0d7de); border-radius:8px; box-shadow:0 6px 20px rgba(0,0,0,.18); min-width:230px; }
/* on the fullscreen modal front bar, open the menu UPWARD so it doesn't fall off-screen */
.fig-front-pin .pin-menu { top:auto; bottom:100%; margin-top:0; margin-bottom:4px; }
.pin-menu-item { padding:0.35rem 0.6rem; font-size:0.66rem; cursor:pointer; white-space:nowrap; }
.pin-menu-item:hover { background:#1f6feb; color:#fff; }
.pin-menu-empty { padding:0.4rem 0.6rem; font-size:0.66rem; color:var(--muted); }
.ds-overlay { display:none; position:fixed; inset:0; z-index:200; background:rgba(8,12,16,.72); backdrop-filter:blur(3px); align-items:center; justify-content:center; padding:2.5vh 2.5vw; }
.ds-overlay.open { display:flex; }
.ds-modal { position:relative; width:min(1100px,95vw); height:min(86vh,820px); }
.ds-x { position:absolute; top:-14px; right:-14px; z-index:10; width:40px; height:40px; border-radius:50%; border:1px solid var(--border); background:var(--surface); color:var(--text); font-size:18px; cursor:pointer; box-shadow:0 4px 16px rgba(0,0,0,.4); }
.ds-x:hover { background:var(--accent); color:#fff; border-color:var(--accent); }
.ds-flip { width:100%; height:100%; perspective:2200px; }
.ds-flip.clickflip { cursor:pointer; }  /* whole open card flips on click (except real controls) */
.ds-inner { position:relative; width:100%; height:100%; transition:transform .55s; transform-style:preserve-3d; }
.ds-flip.flipped .ds-inner { transform:rotateY(180deg); }
.ds-front, .ds-back { position:absolute; inset:0; backface-visibility:hidden; -webkit-backface-visibility:hidden; background:var(--surface); border:1px solid var(--border); border-radius:14px; padding:2rem 2.4rem; overflow-y:auto; box-shadow:0 24px 70px rgba(0,0,0,.5); }
.ds-back { transform:rotateY(180deg); }
.ds-role { font-size:0.72rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.08em; font-weight:700; margin-bottom:0.4rem; }
.ds-title { font-size:1.5rem; font-weight:800; color:var(--text); margin-bottom:1.2rem; line-height:1.15; }
.ds-grid2 { display:grid; grid-template-columns:max-content 1fr; gap:0.6rem 1.4rem; align-items:start; }
.ds-k { font-size:0.74rem; font-weight:700; color:var(--muted); text-transform:uppercase; letter-spacing:0.04em; padding-top:0.1rem; }
.ds-v { font-size:0.9rem; color:var(--text); line-height:1.55; }
.ds-v code { background:var(--surface2); padding:0.08rem 0.4rem; border-radius:4px; font-size:0.82em; }
.ds-ok { color:var(--green); font-weight:600; } .ds-no { color:var(--red,#C0492F); font-weight:600; }
.ds-preview { background:var(--surface2); border:1px solid var(--border); border-radius:6px; padding:0.7rem 0.9rem; margin-top:1.3rem; font-family:'SF Mono',monospace; font-size:0.72rem; line-height:1.6; overflow-x:auto; color:var(--muted); max-height:9rem; }
.ds-desc { font-size:1.12rem; line-height:1.7; color:var(--text); max-width:62ch; }
.ds-usefor { margin-top:1.4rem; }
.ds-rolechip { display:inline-block; font-size:0.7rem; font-weight:700; padding:0.2rem 0.7rem; border-radius:12px; color:#fff; }
.ds-rolechip.ds-tag-v { background:var(--green); } .ds-rolechip.ds-tag-w { background:#a9781f; } .ds-rolechip.ds-tag-n { background:var(--muted); }
.ds-flipbtn { margin-top:1.8rem; background:var(--accent); border:none; border-radius:8px; color:#fff; font-size:0.85rem; font-weight:600; padding:0.6rem 1.1rem; cursor:pointer; }
.ds-flipbtn:hover { filter:brightness(1.1); }
/* Figure cards: compact grid + fullscreen flip modal (mirrors .ds-card / .ds-overlay) */
.fig-card-thumb { width:100%; height:118px; background:var(--surface2); border-radius:7px; overflow:hidden; display:flex; align-items:center; justify-content:center; margin-bottom:0.55rem; }
.fig-card-thumb img { width:100%; height:100%; object-fit:cover; object-position:top center; display:block; }
.fig-tier-chip { font-size:0.6rem; font-weight:700; padding:0.12rem 0.5rem; border-radius:10px; text-transform:uppercase; letter-spacing:0.04em; color:#fff; }
.fig-tier-approved { background:var(--green); } .fig-tier-review { background:#a9781f; } .fig-tier-sandbox { background:var(--muted); }
.fig-modal { width:min(1200px,96vw); height:min(90vh,900px); }
.fig-front-modal, .fig-back-modal { display:flex; flex-direction:column; }
.fig-modal-img { flex:1; min-height:0; display:flex; align-items:center; justify-content:center; background:var(--surface2); border-radius:10px; padding:1rem; }
.fig-modal-img img { max-width:100%; max-height:100%; object-fit:contain; display:block; }
.fig-modal-bar { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-top:1.2rem; }
.fig-modal-name { font-weight:700; font-size:1rem; color:var(--text); }
.fig-modal-eyebrow { font-size:0.72rem; color:var(--accent); text-transform:uppercase; letter-spacing:0.05em; font-weight:700; margin-bottom:0.4rem; }
.fig-modal-caption { font-size:1.08rem; line-height:1.7; color:var(--text); max-width:70ch; }
.fig-modal-nodesc { color:var(--red,#C0492F); font-style:italic; }
.fig-modal-stage { margin-top:1.1rem; font-size:0.78rem; color:var(--accent); font-weight:600; }
.fig-modal-src { margin-top:0.9rem; font-size:0.78rem; color:var(--muted); }
.fig-modal-src code { background:var(--surface2); padding:0.08rem 0.4rem; border-radius:4px; }
.fig-modal-viewsrc { color:var(--green); cursor:pointer; } .fig-modal-viewsrc:hover { text-decoration:underline; }
.fig-back-modal .tier-buttons { margin-top:1.3rem; }
/* Folding figure sections (Labor event open; Data centers folded) */
.fig-group { margin-bottom:1.1rem; border:1px solid var(--border); border-radius:10px; background:var(--surface); overflow:hidden; }
.fig-group-sum { cursor:pointer; padding:0.7rem 1rem; font-size:1.02rem; font-weight:700; color:var(--text); list-style:none; user-select:none; }
.fig-group-sum::-webkit-details-marker { display:none; }
.fig-group-sum::before { content:'\\25B8'; display:inline-block; margin-right:0.5rem; color:var(--accent); transition:transform .15s; }
.fig-group[open] .fig-group-sum::before { transform:rotate(90deg); }
.fig-group-sum:hover { background:var(--surface2); }
.fig-group-n { font-size:0.72rem; font-weight:600; color:var(--muted); background:var(--surface2); border-radius:10px; padding:0.1rem 0.5rem; margin-left:0.4rem; }
.fig-group .ds-grid { padding:0.4rem 1rem 1rem; }
/* Prev/Next nav arrows on the fullscreen modal */
.fig-nav { position:fixed; top:50%; transform:translateY(-50%); z-index:210; width:54px; height:54px; border-radius:50%;
  border:1px solid var(--border); background:var(--surface); color:var(--text); font-size:30px; line-height:1; cursor:pointer;
  box-shadow:0 4px 16px rgba(0,0,0,.4); display:flex; align-items:center; justify-content:center; }
.fig-overlay-pad { }
.fig-nav:hover { background:var(--accent); color:#fff; border-color:var(--accent); }
.fig-prev { left:2.5vw; } .fig-next { right:2.5vw; }
#fig-overlay:not(.open) .fig-nav { display:none; }
.fig-modal-counter { font-size:0.75rem; color:var(--muted); margin-left:0.6rem; font-family:'SF Mono',monospace; }
"""

JS = """
// Theme: auto / light / dark. Auto follows the OS; the choice persists.
function _themeMode() {
  const saved = localStorage.getItem('gtd-theme');
  return (saved === 'dark' || saved === 'light' || saved === 'auto') ? saved : 'auto';
}
function _resolvedTheme() {
  const mode = _themeMode();
  if (mode !== 'auto') return mode;
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}
function _applyTheme() {
  document.documentElement.setAttribute('data-theme', _resolvedTheme());
  const mode = _themeMode();
  const icon = document.getElementById('theme-icon');
  const label = document.getElementById('theme-label');
  const icons = { auto: '&#9681;', light: '&#9728;', dark: '&#9790;' };
  const labels = { auto: 'Auto', light: 'Light', dark: 'Dark' };
  if (icon)  icon.innerHTML = icons[mode];
  if (label) label.textContent = labels[mode];
}
function _syncThemeButton() { _applyTheme(); }
function toggleTheme() {
  const order = ['auto', 'light', 'dark'];
  const next = order[(order.indexOf(_themeMode()) + 1) % 3];
  localStorage.setItem('gtd-theme', next);
  _applyTheme();
}
_applyTheme();
document.addEventListener('DOMContentLoaded', _syncThemeButton);
window.matchMedia('(prefers-color-scheme: light)').addEventListener('change', _syncThemeButton);

function show(id) {
  var view = document.getElementById('v-'+id);
  var tab = document.querySelector('[data-tab="'+id+'"]');
  if (!view || !tab) return;   // tab was retired — ignore stale links rather than throw
  document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
  document.querySelectorAll('nav .btn').forEach(b => b.classList.remove('active'));
  view.classList.add('active');
  tab.classList.add('active');
  if (id === 'diffs') loadDiffs();
}

// ---- Home "Today" to-do: click a box to cross the item off. State persists in localStorage
// keyed by the TODAY.md date + item index, so reloads keep the checks — but when /sleep writes
// a NEW TODAY.md (new date), the keys change and every item comes back fresh & uncrossed. ----
function _applyTodo(li, done) {
  const box = li.querySelector('.today-box');
  const txt = li.querySelector('.today-text');
  if (done) {
    box.innerHTML = '\\u2611';                       // checked box
    txt.style.textDecoration = 'line-through';
    txt.style.opacity = '0.5';
  } else {
    box.innerHTML = '\\u2610';                       // open box
    txt.style.textDecoration = 'none';
    txt.style.opacity = '1';
  }
}
function toggleTodo(li) {
  const key = li.dataset.key;
  const done = !(localStorage.getItem(key) === '1');
  try { done ? localStorage.setItem(key, '1') : localStorage.removeItem(key); } catch(e) {}
  _applyTodo(li, done);
}
function restoreTodos() {
  document.querySelectorAll('.today-item').forEach(li => {
    let done = false;
    try { done = localStorage.getItem(li.dataset.key) === '1'; } catch(e) {}
    if (done) _applyTodo(li, true);
  });
}
document.addEventListener('DOMContentLoaded', restoreTodos);

// ===== Rituals tab — Arrival / Departure checklists =====
// Boxes persist in localStorage keyed by today's date. Each new calendar day
// shows fresh boxes; previous days remain stored (recoverable) but the UI is
// clean. The "Reset today" button forces today's boxes back to empty.
function _todayKey() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return y + '-' + m + '-' + day;
}
function _ritualKey(kind) { return 'gtd-ritual-' + kind + '-' + _todayKey(); }
function _ritualBoxes(kind) {
  return Array.from(document.querySelectorAll('.ritual-check[data-kind="' + kind + '"]'));
}
function _saveRitual(kind) {
  const state = _ritualBoxes(kind).map(b => b.checked);
  try { localStorage.setItem(_ritualKey(kind), JSON.stringify(state)); } catch (e) {}
}
function _loadRitual(kind) {
  let state = null;
  try { state = JSON.parse(localStorage.getItem(_ritualKey(kind))); } catch (e) {}
  const boxes = _ritualBoxes(kind);
  if (Array.isArray(state) && state.length === boxes.length) {
    boxes.forEach((b, i) => { b.checked = !!state[i]; });
  } else {
    boxes.forEach(b => { b.checked = false; });
  }
  _updateRitualProgress(kind);
}
function _updateRitualProgress(kind) {
  const boxes = _ritualBoxes(kind);
  const done = boxes.filter(b => b.checked).length;
  const el = document.getElementById('ritual-progress-' + kind);
  if (el) {
    el.textContent = done + ' of ' + boxes.length;
    if (done === boxes.length && boxes.length > 0) {
      el.classList.add('complete');
      el.textContent = '✓ ' + done + ' of ' + boxes.length + ' — complete';
    } else {
      el.classList.remove('complete');
    }
  }
}
function resetRitual(kind) {
  _ritualBoxes(kind).forEach(b => { b.checked = false; });
  _saveRitual(kind);
  _updateRitualProgress(kind);
}
function _initRituals() {
  ['arrival', 'departure'].forEach(kind => {
    _loadRitual(kind);
    _ritualBoxes(kind).forEach(b => {
      b.addEventListener('change', () => {
        _saveRitual(kind);
        _updateRitualProgress(kind);
      });
    });
  });
  // Watch for date rollover (e.g., a tab left open across midnight).
  let lastDay = _todayKey();
  setInterval(() => {
    const now = _todayKey();
    if (now !== lastDay) {
      lastDay = now;
      ['arrival', 'departure'].forEach(_loadRitual);
    }
  }, 60 * 1000);
}
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', _initRituals);
} else {
  _initRituals();
}
async function loadCode(path, line) {
  document.getElementById('code-path').textContent = path + (line ? ' (line '+line+')' : '');
  try {
    const r = await fetch('/api/code?path='+encodeURIComponent(path));
    if (!r.ok) throw new Error('HTTP '+r.status);
    const text = await r.text();
    // Render with line numbers
    const lines = text.split('\\n');
    const html = lines.map((l, i) => {
      const num = i + 1;
      const highlight = (line && num === parseInt(line)) ? ' style="background:rgba(139,92,246,0.15);display:block;"' : '';
      return '<span class="code-line"' + highlight + ' id="codeline-'+num+'"><span class="line-num">'+(num)+'</span>'+l.replace(/</g,'&lt;')+'</span>';
    }).join('\\n');
    document.getElementById('code-body').innerHTML = html;
    show('code');
    if (line) {
      setTimeout(() => {
        const el = document.getElementById('codeline-'+line);
        if (el) el.scrollIntoView({behavior:'smooth', block:'center'});
      }, 100);
    }
  } catch(e) {
    document.getElementById('code-body').textContent = 'Error: '+e.message;
    show('code');
  }
}
// Drag and drop in the left-hand list (reorders figures/tables)
let dragItem = null;
function initDrag() {
  document.querySelectorAll('.fig-list .fig-list-item').forEach(el => {
    el.setAttribute('draggable', 'true');
    el.addEventListener('dragstart', e => {
      dragItem = el;
      el.style.opacity = '0.4';
      e.dataTransfer.effectAllowed = 'move';
    });
    el.addEventListener('dragend', e => {
      el.style.opacity = '1';
      dragItem = null;
      document.querySelectorAll('.drag-over-item').forEach(d => d.classList.remove('drag-over-item'));
      saveListOrder(el.closest('.fig-list'));
    });
    el.addEventListener('dragover', e => {
      e.preventDefault();
      e.dataTransfer.dropEffect = 'move';
      el.classList.add('drag-over-item');
    });
    el.addEventListener('dragleave', e => { el.classList.remove('drag-over-item'); });
    el.addEventListener('drop', e => {
      e.preventDefault();
      el.classList.remove('drag-over-item');
      if (dragItem && dragItem !== el) {
        const list = el.parentElement;
        const items = [...list.querySelectorAll('.fig-list-item')];
        const fromIdx = items.indexOf(dragItem);
        const toIdx = items.indexOf(el);
        if (fromIdx < toIdx) { list.insertBefore(dragItem, el.nextSibling); }
        else { list.insertBefore(dragItem, el); }
        // Also reorder the cards in the main panel
        reorderCards(list);
      }
    });
  });
}
function reorderCards(list) {
  const items = [...list.querySelectorAll('.fig-list-item')];
  const grid = list.closest('.fig-split').querySelector('.fig-grid');
  if (!grid) return;
  items.forEach(item => {
    const targetId = item.getAttribute('onclick')?.match(/getElementById\('([^']+)'\)/)?.[1];
    if (targetId) {
      const card = document.getElementById(targetId);
      if (card) grid.appendChild(card);
    }
  });
}
async function saveListOrder(list) {
  const items = [...list.querySelectorAll('.fig-list-item')];
  const ids = items.map(el => {
    const m = el.getAttribute('onclick')?.match(/getElementById\('([^']+)'\)/);
    return m ? m[1] : null;
  }).filter(Boolean);
  const viewId = list.closest('.view')?.id || 'unknown';
  await fetch('/api/order', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({[viewId]: ids})});
}
window.addEventListener('load', () => {
  initDrag();
  // Scroll spy: highlight left list item when figure is visible
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        const id = e.target.id;
        e.target.closest('.fig-split')?.querySelectorAll('.fig-list-item').forEach(item => {
          const match = item.getAttribute('onclick')?.includes(id);
          item.classList.toggle('active', match);
        });
      }
    });
  }, {threshold:0.5});
  document.querySelectorAll('.fig-flip-container[id]').forEach(el => observer.observe(el));
});
async function setTier(script, tier, btn) {
  try {
    const r = await fetch('/api/tier', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({script, tier})});
    if (r.ok) {
      btn.parentElement.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('tier-active'));
      btn.classList.add('tier-active');
    }
  } catch(e) { console.error(e); }
}
// Generic group-cycling lightbox. Works for courtroom thumbs, figures tab,
// and tables tab — any group with cycle-eligible thumbs. Arrow keys walk
// the cycle whenever a group context is set.
//
// `groupSelector` is a CSS selector that yields the list of cycle-eligible
// thumbs in DOM order. Each thumb must carry data-cycle-src, data-cycle-name,
// and (optionally) data-cycle-kind="figure"|"table".
function showLightboxFromGroup(thumbEl, groupSelector) {
  const allThumbs = Array.from(document.querySelectorAll(groupSelector));
  let idx = allThumbs.indexOf(thumbEl);
  if (idx < 0) idx = 0;
  window._lbCycle = { thumbs: allThumbs, idx, selector: groupSelector };
  const t = allThumbs[idx];
  const kind = t.dataset.cycleKind || 'figure';
  showLightbox(t.dataset.cycleSrc, t.dataset.cycleName, /*hasCycle=*/true, kind);
}
// Legacy entry point — courtroom thumbs still call this.
function showCourtroomLightbox(thumbEl) {
  // Migrate courtroom thumbs onto the generic cycler at call time.
  const courtThumbs = Array.from(document.querySelectorAll('.court-thumb[data-court-src]'));
  courtThumbs.forEach(c => {
    c.dataset.cycleSrc = c.dataset.courtSrc;
    c.dataset.cycleName = c.dataset.courtName;
    c.dataset.cycleKind = 'figure';
  });
  showLightboxFromGroup(thumbEl, '.court-thumb[data-cycle-src]');
}
function _lbCycleStep(delta) {
  const ctx = window._lbCycle;
  if (!ctx) return;
  const n = ctx.thumbs.length;
  if (!n) return;
  ctx.idx = (ctx.idx + delta + n) % n;
  const t = ctx.thumbs[ctx.idx];
  const kind = t.dataset.cycleKind || 'figure';
  showLightbox(t.dataset.cycleSrc, t.dataset.cycleName, /*hasCycle=*/true, kind);
}
// Back-compat shim: old call sites pass _courtroomLbStep directly.
function _courtroomLbStep(delta) { _lbCycleStep(delta); }
function showLightbox(src, title, hasCycle, kind) {
  if (!hasCycle) window._lbCycle = null;
  kind = kind || 'figure';
  let lb = document.getElementById('lightbox-overlay');
  if (!lb) {
    lb = document.createElement('div');
    lb.id = 'lightbox-overlay';
    lb.innerHTML = `<div class="lb-backdrop"></div>
      <div class="lb-content">
        <div class="lb-flip-container">
          <div class="lb-flip-inner">
            <div class="lb-front"><img class="lb-img"><div class="lb-title"></div><div class="lb-hint">click card to flip · ← → to cycle (courtroom)</div></div>
            <div class="lb-back"><div class="lb-back-title"></div><div class="lb-back-body"></div></div>
          </div>
        </div>
      </div>`;
    document.body.appendChild(lb);
    lb.querySelector('.lb-backdrop').onclick = () => { lb.style.display='none'; window._lbCycle = null; };
    lb.querySelector('.lb-flip-container').onclick = (e) => {
      if (e.target.closest('.lb-back-action')) return;
      lb.querySelector('.lb-flip-container').classList.toggle('flipped');
    };
    document.addEventListener('keydown', (e) => {
      if (lb.style.display !== 'flex') return;
      if (e.key === 'Escape') { lb.style.display='none'; lb.querySelector('.lb-flip-container').classList.remove('flipped'); window._lbCycle = null; return; }
      if (window._lbCycle) {
        if (e.key === 'ArrowLeft')  { e.preventDefault(); _lbCycleStep(-1); }
        if (e.key === 'ArrowRight') { e.preventDefault(); _lbCycleStep(1); }
      }
    });
  }
  lb.querySelector('.lb-flip-container').classList.remove('flipped');
  lb.querySelector('.lb-img').src = src;
  const displayTitle = title.replace(/_/g, ' ');
  lb.querySelector('.lb-title').textContent = displayTitle;
  lb.querySelector('.lb-back-title').textContent = displayTitle;
  // Build back content from figure metadata if available
  const figEl = document.getElementById('fig-' + title);
  let backHtml = '';
  if (figEl) {
    const backEl = figEl.querySelector('.fig-back');
    if (backEl) { backHtml = backEl.innerHTML; }
  }
  if (!backHtml) {
    backHtml = '<div style="color:var(--muted);padding:1rem;">Source: ' + src + '</div>';
  }
  lb.querySelector('.lb-back-body').innerHTML = backHtml;
  lb.style.display = 'flex';
}

// ---- Pin a figure to a checklist stage (Scott, 2026-07-28) ----
// Builds a dropdown from window.PIN_STAGES, POSTs to /api/pin-figure, and updates the card's status
// line live (no page reload). Warn-but-allow: if the figure's script isn't wired into run_pipeline.sh,
// the confirmation shows an UNWIRED warning but the pin still succeeds.
function closePinMenus(){ document.querySelectorAll('.pin-menu').forEach(m=>m.remove()); }
function openPinMenu(btn, name, path, script){
  closePinMenus();
  const stages = window.PIN_STAGES || [];
  const menu = document.createElement('div'); menu.className='pin-menu';
  if(!stages.length){ menu.innerHTML='<div class="pin-menu-empty">No analysis stages found.</div>'; }
  else {
    stages.forEach(s=>{
      const it=document.createElement('div'); it.className='pin-menu-item'; it.textContent=s.label;
      it.onclick=(e)=>{ e.stopPropagation(); closePinMenus(); doPin(btn, s.slug, s.stage, name, path, script); };
      menu.appendChild(it);
    });
  }
  btn.parentElement.appendChild(menu);
  setTimeout(()=>document.addEventListener('click', closePinMenus, {once:true}), 0);
}
async function doPin(btn, slug, stage, name, path, script){
  const status = btn.parentElement.querySelector('.pin-status');
  status.textContent='pinning…';
  try {
    const r = await fetch('/api/pin-figure', {method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({slug, stage, name, path, script})});
    const d = await r.json();
    if(d.ok){
      const where = slug+' · '+stage;
      if(d.already){ status.innerHTML='<span class="pin-ok">already in '+where+'</span>'; }
      else if(d.wired){ status.innerHTML='<span class="pin-ok">&#10003; pinned to '+where+'</span>'; }
      else { status.innerHTML='<span class="pin-warn">&#9888; pinned to '+where+' (UNWIRED — provenance not proven)</span>'; }
      // add a STANDING chip next to the button so it persists visually until reload (matches reload state)
      const foot = btn.parentElement;
      let cur = foot.querySelector('.pin-current');
      if(!cur){ cur=document.createElement('div'); cur.className='pin-current'; foot.insertBefore(cur, foot.firstChild); }
      if(![...cur.querySelectorAll('.pin-chip')].some(c=>c.textContent.includes(where))){
        const chip=document.createElement('span'); chip.className='pin-chip'; chip.textContent='📌 '+where; cur.appendChild(chip);
      }
    } else { status.textContent='pin failed'; }
  } catch(e){ status.textContent='pin failed'; console.error(e); }
}
// ---- Diffs tab: a GRID of commit cards; click one to float it open into the fullscreen
// flip modal (mirrors the figure lightbox). Front = green/red diff; back = authored/committed
// dates + review sign-off. ← / → rotate commits inside the modal. Read-only on git. ----
let DIFF_COMMITS = [], DIFF_CUR = 0, diffsLoaded = false;
async function loadDiffs() {
  if (diffsLoaded) return;
  const counter = document.getElementById('diff-counter');
  const grid = document.getElementById('diff-grid');
  if (!counter || !grid) return;
  try {
    const r = await fetch('/api/git-log');
    DIFF_COMMITS = await r.json();
    if (!DIFF_COMMITS.length) { counter.textContent = 'No commits yet.'; return; }
    diffsLoaded = true;
    counter.innerHTML = DIFF_COMMITS.length + ' commit' + (DIFF_COMMITS.length===1?'':'s') +
      ' · newest first · click a card to open the diff, then use <b>&larr; &rarr;</b> to walk commits';
    renderDiffGrid();
    refreshScale();   // paint the sticky scale readout as soon as commits are in memory
  } catch(e) { counter.textContent = 'Could not load git log.'; }
}
function renderDiffGrid() {
  const grid = document.getElementById('diff-grid');
  grid.innerHTML = DIFF_COMMITS.map(function(c, i){
    const reviewed = !!c.reviewed;
    const chip = reviewed
      ? '<span class="fig-tier-chip" style="background:var(--green);">&#10003; reviewed</span>'
      : '<span class="fig-tier-chip" style="background:#a9781f;">&#9675; debt</span>';
    // CONVENTION (Scott, 2026-07-17): commit subject = "CAPS SUMMARY: detailed part". If the text
    // BEFORE the first colon is an all-caps summary, the card TITLE shows just that (short, scannable),
    // and the detailed part becomes small subtext. If there's no caps lead (old commits), fall back to
    // showing the detail, truncated. Full raw subject always shows when the card opens.
    var raw = c.subject;
    var esc = function(t){ return t.replace(/&/g,'&amp;').replace(/</g,'&lt;'); };
    var ci = raw.indexOf(':');
    var lead = ci > -1 ? raw.slice(0, ci).trim() : '';
    var rest = ci > -1 ? raw.slice(ci + 1).trim() : raw;
    // "all-caps summary" = the lead is short and has no lowercase letters (allow digits, spaces, /&-)
    var isCaps = lead.length > 0 && lead.length <= 32 && !/[a-z]/.test(lead);
    var title, sub;
    if (isCaps) { title = lead; sub = rest; }
    else { title = rest.replace(/\\s*\\([^)]*\\)\\s*$/, '').trim(); sub = ''; }   // fallback: old behavior
    if (title.length > 60) title = title.slice(0, 58).trim() + '…';
    if (sub.length > 90) sub = sub.slice(0, 88).trim() + '…';
    return '<div class="ds-card" onclick="openDiff('+i+')">'
      + '<div class="ds-card-top">' + chip
      + '<span style="font-size:0.6rem;color:var(--muted);font-family:\\'SF Mono\\',monospace;">#'+(i+1)+'</span></div>'
      + '<div class="ds-card-name">'+esc(title)+'</div>'
      + (sub ? '<div style="font-size:0.72rem;color:var(--muted);line-height:1.3;margin-top:0.2rem;">'+esc(sub)+'</div>' : '')
      + '<div class="ds-card-src">'+c.short+' · '+c.date+'</div>'
      + '<div class="ds-card-hint">click to open diff &#x26F6;</div></div>';
  }).join('');
}
function openDiff(i) {
  if (!DIFF_COMMITS.length) return;
  DIFF_CUR = Math.max(0, Math.min(DIFF_COMMITS.length - 1, i));
  flipDiffModal(false);                 // always open on the diff (front)
  document.getElementById('diff-overlay').classList.add('open');
  showDiffModal();
}
function closeDiff() { document.getElementById('diff-overlay').classList.remove('open'); }
function stepDiffModal(dir) {
  DIFF_CUR = Math.max(0, Math.min(DIFF_COMMITS.length - 1, DIFF_CUR + dir));
  flipDiffModal(false);
  showDiffModal();
}
function flipDiffModal(toBack) {
  document.getElementById('diff-flip').classList.toggle('flipped', !!toBack);
}
// Click anywhere on the card (including the diff text) to toggle front<->back. Only two
// exceptions: real controls (buttons), and when you're actually selecting text (so
// highlighting a diff line doesn't flip the card out from under you). Scrolling a trackpad
// doesn't fire a click, so scrolling the patch is unaffected.
function diffCardClick(ev) {
  if (ev.target.closest('button, a')) return;
  const sel = window.getSelection && window.getSelection().toString();
  if (sel) return;                       // mid text-selection — don't flip
  document.getElementById('diff-flip').classList.toggle('flipped');
}
// Trackpad scroll fix (Scott, 2026-07-10): the diff patch sits inside a 3D-transformed flip card,
// and WebKit eats two-finger wheel scrolling of nested overflow:auto children there. Manually apply
// wheel deltas to the patch pane so the trackpad (and mouse wheel) scroll it. Bound once, on the doc,
// so it survives re-renders; only acts when the pointer is over #diff-patch.
if (!window._diffWheelBound) {
  window._diffWheelBound = true;
  document.addEventListener('wheel', function(e){
    const p = document.getElementById('diff-patch');
    if (!p) return;
    const ov = document.getElementById('diff-overlay');
    if (!ov || !ov.classList.contains('open')) return;
    if (!p.contains(e.target)) return;
    p.scrollTop += e.deltaY;
    e.preventDefault();
  }, { passive: false });
}
async function showDiffModal() {
  const c = DIFF_COMMITS[DIFF_CUR]; if (!c) return;
  const subj = c.subject;
  document.getElementById('diff-subject').textContent = subj;
  document.getElementById('diff-back-subject').textContent = subj;
  document.getElementById('diff-front-eyebrow').textContent =
    'Commit diff · ' + (DIFF_CUR+1) + ' / ' + DIFF_COMMITS.length;
  document.getElementById('diff-meta').textContent = c.short + ' · ' + c.date;
  document.getElementById('diff-adate').textContent = c.adate || c.date || '—';
  document.getElementById('diff-cdate').textContent = c.cdate || c.date || '—';
  document.getElementById('diff-hash').textContent = c.short;
  renderReviewState(c);
  // Load the patch for this commit (green/red).
  const patch = document.getElementById('diff-patch');
  patch.innerHTML = 'loading diff…';
  try {
    const r = await fetch('/api/git-diff?hash='+encodeURIComponent(c.hash));
    const text = await r.text();
    DIFF_LINES = text.split('\\n');   // stash raw lines so the changes-only / full toggle can re-render
    renderPatchLines();
  } catch(e) { patch.innerHTML = '<span style="color:var(--red);">Could not load diff.</span>'; }
}
// Front shows ONLY the changes (green +, red -) by default — the white/unchanged context lines are hidden;
// toggle to full context (Scott, 2026-07-20). @@ hunk headers + file headers are kept for orientation.
var DIFF_LINES = [];
var DIFF_FULL = false;   // false = changes only (default), true = full unified context
function renderPatchLines() {
  const patch = document.getElementById('diff-patch');
  if (!DIFF_LINES.length) { patch.innerHTML = '(no changes)'; return; }
  let shown = 0;
  const html = DIFF_LINES.map(l => {
    const e = l.replace(/&/g,'&amp;').replace(/</g,'&lt;');
    const isAdd = l.startsWith('+') && !l.startsWith('+++');
    const isDel = l.startsWith('-') && !l.startsWith('---');
    const isHunk = l.startsWith('@@');
    const isHdr = l.startsWith('diff ')||l.startsWith('commit ')||l.startsWith('Author')||l.startsWith('Date')||l.startsWith('+++')||l.startsWith('---')||l.startsWith('index ');
    if (isAdd) { shown++; return '<span style="background:rgba(52,211,153,0.15);color:var(--green);display:block;">'+e+'</span>'; }
    if (isDel) { shown++; return '<span style="background:rgba(248,113,113,0.15);color:var(--red);display:block;">'+e+'</span>'; }
    if (isHunk) return '<span style="color:var(--accent);display:block;">'+e+'</span>';   // keep hunk header for orientation
    if (isHdr) return '<span style="color:var(--muted);display:block;">'+e+'</span>';       // keep file/commit headers
    // an unchanged CONTEXT line: show only in full mode
    return DIFF_FULL ? '<span style="display:block;">'+e+'</span>' : '';
  }).join('');
  patch.innerHTML = html || '<span style="color:var(--muted);">(no added/removed lines)</span>';
  const t = document.getElementById('diff-fulltoggle');
  if (t) t.textContent = DIFF_FULL ? 'Changes only' : 'Show full context';
}
function toggleDiffFull(){ DIFF_FULL = !DIFF_FULL; renderPatchLines(); }
function renderReviewState(c) {
  const badge = document.getElementById('diff-badge');
  const btn = document.getElementById('diff-reviewbtn');
  if (c.reviewed) {
    badge.textContent = '\\u2713 Reviewed' + (c.reviewed_at ? ' ' + c.reviewed_at : '');
    badge.style.background = 'rgba(52,211,153,0.18)'; badge.style.color = 'var(--green)';
    btn.innerHTML = '\\u2717 Un-review'; btn.style.background = 'var(--surface2)'; btn.style.color = 'var(--text)';
  } else {
    badge.textContent = '\\u25CB Unreviewed \\u2014 verification debt';
    badge.style.background = 'rgba(251,191,36,0.18)'; badge.style.color = 'var(--yellow)';
    btn.innerHTML = '\\u2713 Mark reviewed'; btn.style.background = 'var(--green)'; btn.style.color = '#fff';
  }
}
async function toggleReview() {
  const c = DIFF_COMMITS[DIFF_CUR]; if (!c) return;
  const newState = !c.reviewed;
  try {
    await fetch('/api/git-review', {method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({hash: c.hash, reviewed: newState})});
    c.reviewed = newState;
    c.reviewed_at = newState ? 'just now' : '';
    renderReviewState(c);
    renderDiffGrid();        // reflect the chip on the grid card behind the modal
    refreshScale();          // re-weigh the scale-of-justice live
  } catch(e) {}
}
document.addEventListener('keydown', function(e){
  const v = document.getElementById('v-diffs');
  if (!v || !v.classList.contains('active')) return;
  const open = document.getElementById('diff-overlay') &&
               document.getElementById('diff-overlay').classList.contains('open');
  if (!open) return;                    // arrows only act while the modal is floating open
  if (e.key === 'ArrowRight') { stepDiffModal(1); e.preventDefault(); }
  else if (e.key === 'ArrowLeft') { stepDiffModal(-1); e.preventDefault(); }
  else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    flipDiffModal(!document.getElementById('diff-flip').classList.contains('flipped')); e.preventDefault(); }
  else if (e.key === 'Escape') { closeDiff(); e.preventDefault(); }
});

// ---- Live link: marking a diff reviewed re-weighs the scale-of-justice WITHOUT a reload ----
// Recomputes from the in-memory commit list (each carries a live `reviewed` flag), so the beam
// settles toward level the instant you accept a diff, and tips back if you un-review.
function refreshScale() {
  if (!DIFF_COMMITS || !DIFF_COMMITS.length) return;
  const total = DIFF_COMMITS.length;
  const reviewed = DIFF_COMMITS.filter(c => c.reviewed).length;
  const debt = total - reviewed;
  const beam = document.getElementById('scale-beam');
  if (beam) beam.style.transform = 'rotate(' + (debt > 0 ? 10 : 0) + 'deg)';
  const set = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  set('scale-legend-prod', total); set('scale-legend-ver', reviewed);
  const verdict = document.getElementById('scale-verdict');
  if (verdict) {
    if (debt === 0 && total > 0) {
      verdict.innerHTML = '\\u2696 Balanced \\u2014 every commit reviewed. You are caught up.';
      verdict.style.color = 'var(--green)';
    } else {
      verdict.innerHTML = debt + ' unreviewed commit' + (debt !== 1 ? 's' : '') +
        ' \\u2014 verification debt. Review them in the Diffs tab to level the scale.';
      verdict.style.color = 'var(--yellow)';
    }
  }
}
"""


# =============================================================================
# FRESHNESS / OFFICIAL-PIPELINE VERDICTS / SAMPLE FLOW / EPIGRAPH
# (ported from the GTD template, 2026-06-12 — see correspondence/referee2/
#  2026-06-12_gtd_template_sync_audit.md. All degrade gracefully when the
#  backing data — quotes, pipeline_runs, sample-flow generator — is absent.)
# =============================================================================

FRESHNESS_CLASSES = [
    ("Raw data", ["data/raw/*", "data/clean/*", "data/derived/*"], False),
    ("Tables", ["output/tables/*"], True),
    ("Figures", ["output/figures/*"], True),
    ("Flow checkpoint", ["audits/flows/sample_flow_*.json"], True),
]


def render_freshness():
    """Age chips: days since each artifact class was last produced, vs the raw
    data. RED = raw data newer than artifacts built from it (true staleness).
    YELLOW = aging (>14d) but consistent. GREEN = artifacts postdate inputs."""
    import datetime as _dt
    now = _dt.datetime.now()

    def newest(globs):
        ts = []
        for g in globs:
            ts += [p.stat().st_mtime for p in ROOT.glob(g) if p.is_file()]
        return max(ts) if ts else None

    raw_ts = newest(FRESHNESS_CLASSES[0][1])
    chips = ""
    for name, globs, downstream in FRESHNESS_CLASSES:
        ts = newest(globs)
        if ts is None:
            chips += (f'<span style="display:inline-block;margin:0 0.4rem 0.4rem 0;padding:0.25rem 0.65rem;'
                      f'border-radius:5px;font-size:0.7rem;background:var(--surface2);'
                      f'border:1px solid var(--border);color:var(--muted);">{name}: none</span>')
            continue
        age = (now - _dt.datetime.fromtimestamp(ts)).days
        date = _dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        is_stale = downstream and raw_ts is not None and ts < raw_ts - 60
        if is_stale:
            color, weight, note, bg = "var(--red)", "700", " &mdash; OLDER THAN THE DATA, re-run", "var(--red-dim)"
        elif age > 14:
            color, weight, note, bg = "var(--yellow)", "600", "", "var(--yellow-dim)"
        else:
            color, weight, note, bg = "var(--green)", "400", "", "var(--green-dim)"
        chips += (f'<span title="newest file: {date}" style="display:inline-block;margin:0 0.4rem 0.4rem 0;'
                  f'padding:0.25rem 0.65rem;border-radius:5px;font-size:0.7rem;background:{bg};'
                  f'border:1px solid {color};color:{color};font-weight:{weight};">'
                  f'{name}: {"today" if age == 0 else str(age) + "d ago"}{note}</span>')
    return f'<div style="margin-bottom:0.9rem;">{chips}</div>'


def official_verdicts():
    """Latest official pipeline run report: per-artifact verdicts + run stamp."""
    import json as _json
    runs = sorted((ROOT / "audits/pipeline_runs").glob("run_*.json")) \
        if (ROOT / "audits/pipeline_runs").exists() else []
    if not runs:
        return {}, None
    rep = _json.loads(runs[-1].read_text())
    return rep.get("verdicts", {}), rep.get("run")


def verdict_badge(path, verdicts, run_stamp):
    """Small badge stating the artifact's verdict at the last official run."""
    if not run_stamp:
        return ""
    v = verdicts.get(path, {}).get("verdict")
    if v in ("confirmed", "regenerated-identical"):
        return (f'<span style="font-size:0.6rem;color:var(--green);font-weight:600;">'
                f'&#10003; reproduced {run_stamp}</span>')
    if v == "changed":
        return (f'<span style="font-size:0.6rem;color:var(--red);font-weight:700;">'
                f'CHANGED at {run_stamp}</span>')
    if v == "untouched":
        return (f'<span style="font-size:0.6rem;color:var(--yellow);font-weight:700;">'
                f'UNTOUCHED by {run_stamp}</span>')
    if v == "missing":
        return (f'<span style="font-size:0.6rem;color:var(--red);font-weight:700;">'
                f'NOT PRODUCED by {run_stamp}</span>')
    return ""


def render_sample_flow():
    """CONSORT-style sample flow. Prefers LIVE computation (imports
    compute_flow() from code/make_sample_flow.py or
    scripts/python/make_sample_flow.py — no cached artifact, cannot be
    stale); falls back to output/sample_flow.json; else shows setup
    instructions. Front: official-pipeline box, drift alarm, freshness,
    anchor badges, narration, chart. Back: provenance (source fingerprints)."""
    import importlib.util
    import json as _json
    import traceback

    d, mode = None, None
    for cand in ["code/make_sample_flow.py", "scripts/python/make_sample_flow.py"]:
        p = ROOT / cand
        if p.exists():
            try:
                spec = importlib.util.spec_from_file_location("msf", p)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                if hasattr(mod, "compute_flow"):
                    d, mode = mod.compute_flow(ROOT), "live"
                    break
            except SystemExit:
                pass  # template stub — fall through to JSON
            except Exception:
                return ('<div style="border:2px solid var(--red);border-radius:6px;padding:1rem;">'
                        '<strong style="color:var(--red);">Sample flow failed to compute.</strong>'
                        '<pre style="font-size:0.65rem;margin-top:0.5rem;white-space:pre-wrap;">'
                        + html_mod.escape(traceback.format_exc()[-900:]) + "</pre></div>")
    if d is None:
        f = ROOT / "output" / "sample_flow.json"
        if f.exists():
            d, mode = _json.loads(f.read_text()), "json"
        else:
            return ('<p class="empty">No sample flow yet. Write a generator exposing '
                    '<code>compute_flow(root)</code> (preferred: the dashboard then computes live on '
                    'every load) or emit <code>output/sample_flow.json</code> — schema in '
                    '<code>scripts/python/make_sample_flow.py</code>.</p>')

    html = ""

    # Official pipeline box
    runs = sorted((ROOT / "audits/pipeline_runs").glob("run_*.json")) \
        if (ROOT / "audits/pipeline_runs").exists() else []
    if runs:
        rep = _json.loads(runs[-1].read_text())
        vc = {}
        for v in rep.get("verdicts", {}).values():
            vc[v["verdict"]] = vc.get(v["verdict"], 0) + 1
        ok = rep.get("all_steps_ok")
        bad = vc.get("changed", 0) + vc.get("missing", 0)
        warn = vc.get("untouched", 0)
        sc = "var(--red)" if (not ok or bad) else ("var(--yellow)" if warn else "var(--green)")
        st = ("FAILED" if not ok else f"{bad} inaccurate" if bad
              else f"clean, {warn} untouched" if warn else "fully reproduced")
        total_s = rep.get("total_seconds") or sum(x.get("seconds", 0) for x in rep.get("steps", []))
        dur = (f"{int(total_s // 60)}m {int(total_s % 60)}s" if total_s >= 60 else f"{int(total_s)}s")
        last_line = (f'Last official run: <strong>{html_mod.escape(rep["run"])}</strong> &mdash; '
                     f'<strong style="color:{sc};">{st}</strong>. It took <strong>{dur}</strong> '
                     f'start to finish &mdash; expect about that when you run it.')
    else:
        last_line = '<strong style="color:var(--red);">No official run yet.</strong>'
    html += (f'<div style="border:1px solid var(--border);background:var(--surface);border-radius:6px;'
             f'padding:0.8rem 1rem;margin-bottom:1rem;">'
             f'<div style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.06em;'
             f'color:var(--muted);margin-bottom:0.3rem;">The Official Pipeline</div>'
             f'<code style="display:block;background:var(--surface2);border:1px solid var(--border);'
             f'border-radius:4px;padding:0.45rem 0.7rem;font-size:0.78rem;margin-bottom:0.4rem;">'
             f'python3 scripts/run_official_pipeline.py</code>'
             f'<div style="font-size:0.74rem;color:var(--muted);">Re-derives every exhibit from raw '
             f'data and verdicts each one. Or say <code>/pipeline</code> in a Claude Code session.</div>'
             f'<div style="font-size:0.74rem;margin-top:0.4rem;">{last_line}</div></div>')

    if d.get("drift_vs_previous"):
        items = "".join(f"<li>{html_mod.escape(x)}</li>" for x in d["drift_vs_previous"])
        html += (f'<div style="border:2px solid var(--red);background:var(--red-dim);border-radius:6px;'
                 f'padding:0.8rem 1rem;margin-bottom:1rem;">'
                 f'<strong style="color:var(--red);">SAMPLE DRIFT &mdash; the data changed since the '
                 f'last acknowledged checkpoint</strong>'
                 f'<ul style="margin:0.4rem 0 0 1.2rem;">{items}</ul></div>')

    stale_note = ("Computed live; no cached artifact exists &mdash; this page cannot be stale."
                  if mode == "live" else
                  "Read from output/sample_flow.json &mdash; a cached artifact; prefer a "
                  "compute_flow() generator for staleness-proof rendering.")
    flip_btn = ""
    if d.get("sources"):
        flip_btn = (f'<button onclick="var f=document.getElementById(\'sf-front\'),'
                    f'b=document.getElementById(\'sf-back\');var sb=f.style.display!==\'none\';'
                    f'f.style.display=sb?\'none\':\'\';b.style.display=sb?\'\':\'none\';'
                    f'this.innerHTML=sb?\'&#8646; Flip to chart\':\'&#8646; Flip to provenance\';" '
                    f'style="flex-shrink:0;margin-left:1rem;padding:0.3rem 0.7rem;font-size:0.72rem;'
                    f'background:var(--surface2);color:var(--text);border:1px solid var(--border);'
                    f'border-radius:5px;cursor:pointer;">&#8646; Flip to provenance</button>')
    html += (f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.8rem;">'
             f'<span style="font-size:0.72rem;color:var(--muted);">Generated '
             f'<strong>{html_mod.escape(d.get("generated", ""))}</strong>. {stale_note}</span>{flip_btn}</div>')

    front = render_freshness()

    if d.get("anchor_present"):
        badges = ""
        for c in d.get("anchor_checks", []):
            ok = c.get("ok")
            color = "var(--green)" if ok else "var(--red)"
            label = "matches anchor" if ok else f'MISMATCH: expected {c.get("expected")}, observed {c.get("observed")}'
            unit = c.get("wave", c.get("group", ""))
            badges += (f'<span style="display:inline-block;margin:0 0.4rem 0.4rem 0;padding:0.15rem 0.6rem;'
                       f'border-radius:10px;font-size:0.7rem;background:{color};color:#fff;">'
                       f'{html_mod.escape(str(unit))}: {html_mod.escape(label)}</span>')
        front += f'<div style="margin-bottom:0.8rem;">{badges}</div>'
    else:
        front += ('<p style="color:var(--red);font-size:0.8rem;">No anchor reconciliation '
                  '&mdash; counts below are unpinned.</p>')

    story = "".join(f'<p style="margin:0 0 0.55rem 0;">{html_mod.escape(x)}</p>'
                    for x in d.get("narration", []))
    front += (f'<div style="font-family:Georgia,serif;font-size:0.95rem;line-height:1.55;'
              f'color:var(--text);background:var(--surface);border-left:4px solid #5B21B6;'
              f'border-radius:4px;padding:0.9rem 1.1rem;margin-bottom:1.4rem;">{story}</div>')

    groups = []
    for r in d.get("flow", []):
        g = r.get("wave", r.get("group"))
        if g not in groups:
            groups.append(g)
    cols = ""
    for g in groups:
        rows = [r for r in d["flow"] if r.get("wave", r.get("group")) == g]
        boxes = (f'<div style="font-weight:700;font-size:0.8rem;margin-bottom:0.5rem;">'
                 f'{html_mod.escape("Wave " + str(g) if isinstance(g, int) else str(g))}</div>')
        for i, r in enumerate(rows):
            if i > 0:
                drop = r.get("dropped", 0)
                reason = html_mod.escape(str(r.get("reason", ""))[:90])
                arrow = f'&darr; &minus;{drop}' if drop else "&darr;"
                note = f' <span style="color:var(--muted);">({reason})</span>' if drop and reason else ""
                boxes += (f'<div style="font-size:0.66rem;color:var(--red);padding:0.18rem 0 0.18rem 0.8rem;">'
                          f'{arrow}{note}</div>')
            by = r.get("by_arm") or r.get("by_group") or {}
            sub = " &middot; ".join(f"{html_mod.escape(str(k))} {v}" for k, v in by.items())
            boxes += (f'<div style="border:1px solid var(--border);border-radius:5px;background:var(--surface);'
                      f'padding:0.45rem 0.6rem;">'
                      f'<div style="font-size:0.68rem;color:var(--muted);text-transform:uppercase;'
                      f'letter-spacing:0.05em;">{html_mod.escape(r["stage"])}</div>'
                      f'<div style="font-size:1.25rem;font-weight:700;">{r["n"]}</div>'
                      + (f'<div style="font-size:0.66rem;color:var(--muted);">{sub}</div>' if sub else "")
                      + "</div>")
        cols += f'<div style="flex:1;min-width:170px;">{boxes}</div>'
    front += f'<div style="display:flex;gap:1rem;flex-wrap:wrap;">{cols}</div>'

    back = ""
    if d.get("sources"):
        src_rows = "".join(
            f'<tr><td style="padding:0.3rem 0.6rem;"><code>{html_mod.escape(x["path"])}</code></td>'
            f'<td style="padding:0.3rem 0.6rem;white-space:nowrap;">{html_mod.escape(x["modified"])}</td>'
            f'<td style="padding:0.3rem 0.6rem;font-family:monospace;font-size:0.62rem;">'
            f'{html_mod.escape(x["sha256"][:16])}&hellip;</td></tr>'
            for x in d["sources"])
        back = ('<div style="font-size:0.82rem;line-height:1.6;">'
                '<h3 style="font-size:0.9rem;margin-bottom:0.4rem;">Source files read for this render</h3>'
                f'<table style="border-collapse:collapse;font-size:0.72rem;background:var(--surface);'
                f'border:1px solid var(--border);border-radius:6px;">'
                f'<tr style="color:var(--muted);"><th style="padding:0.3rem 0.6rem;text-align:left;">file</th>'
                f'<th style="padding:0.3rem 0.6rem;text-align:left;">modified</th>'
                f'<th style="padding:0.3rem 0.6rem;text-align:left;">sha-256</th></tr>{src_rows}</table></div>')

    html += (f'<div id="sf-front">{front}</div>'
             f'<div id="sf-back" style="display:none;">{back}</div>')
    return html


def render_epigraph():
    """A reminder and a line of poetry, freshly drawn on every refresh.
    Reads quotes/maxims.txt and quotes/poetry.txt (one entry per line,
    "text - Attribution" separated by an em dash; # lines ignored)."""
    def pick(fname):
        f = ROOT / "quotes" / fname
        if not f.exists():
            return None
        lines = [l.strip() for l in f.read_text().splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        return random.choice(lines) if lines else None

    def split_attr(line):
        if line and "—" in line:
            text, attr = line.rsplit("—", 1)
            return text.strip(), attr.strip()
        return line, ""

    maxim, poem = pick("maxims.txt"), pick("poetry.txt")
    if not maxim and not poem:
        return ""
    parts = []
    if maxim:
        t, a = split_attr(maxim)
        parts.append(
            f'<div style="font-family:Inter,-apple-system,sans-serif;font-size:0.68rem;'
            f'letter-spacing:0.06em;text-transform:uppercase;color:var(--muted);">'
            f'{html_mod.escape(t)} <span style="text-transform:none;letter-spacing:0;">'
            f'&mdash; {html_mod.escape(a)}</span></div>')
    if poem:
        t, a = split_attr(poem)
        parts.append(
            f'<div style="font-family:Georgia,serif;font-style:italic;font-size:0.92rem;'
            f'color:var(--text);margin-top:0.3rem;">{html_mod.escape(t)} '
            f'<span style="font-style:normal;font-size:0.72rem;color:var(--muted);">'
            f'&mdash; {html_mod.escape(a)}</span></div>')
    return ('<div class="epigraph" style="text-align:center;padding:0.4rem 1rem 0.9rem;'
            'margin:0 0 1.2rem 0;border-bottom:1px solid var(--border);">'
            + "".join(parts) + "</div>")


def scan_html_decks():
    """Find self-contained HTML decks under decks/html/. Two layouts accepted:
      decks/html/<slug>/index.html   (a deck folder)
      decks/html/<slug>.html         (a single-file deck)
    Returns a list of {slug, title, path (served URL), mtime} newest first."""
    import datetime as _dt
    base = ROOT / "decks" / "html"
    decks = []
    if not base.exists():
        return decks
    seen = set()
    for p in sorted(base.iterdir()):
        if p.is_dir() and (p / "index.html").exists():
            f = p / "index.html"
            slug = p.name
        elif p.is_file() and p.suffix == ".html":
            f = p
            slug = p.stem
        else:
            continue
        if slug in seen:
            continue
        seen.add(slug)
        # Pull <title> if present, else prettify the slug.
        title = slug.replace("_", " ").replace("-", " ").title()
        try:
            head = f.read_text(errors="ignore")[:2000]
            m = re.search(r"<title>(.*?)</title>", head, re.I | re.S)
            if m and m.group(1).strip():
                title = m.group(1).strip()
        except OSError:
            pass
        # The deck collection: an optional meta.json (next to the deck or in the
        # deck folder) carries the STATED PURPOSE + canonical date, so the rail
        # reads "2026-06-12 · <purpose>" instead of a bare title. This is the
        # "oh yeah, I remember this" layer — every deck dated, with why it exists.
        purpose, date_str, status = "", None, ""
        meta_path = (p / "meta.json") if p.is_dir() else p.with_suffix(".meta.json")
        if meta_path.exists():
            try:
                import json as _json
                meta = _json.loads(meta_path.read_text())
                title = meta.get("title", title)
                purpose = meta.get("purpose", "")
                date_str = meta.get("date")
                status = meta.get("status", "")
            except (ValueError, OSError):
                pass
        decks.append({
            "slug": slug,
            "title": title,
            "purpose": purpose,
            "status": status,
            "path": "/" + str(f.relative_to(ROOT)),
            "mtime": f.stat().st_mtime,
            "date": date_str or _dt.datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"),
        })
    # Sort by the deck's stated date (meta.json) newest-first; fall back to mtime.
    decks.sort(key=lambda d: (d.get("date") or "", d["mtime"]), reverse=True)
    return decks


def render_decks():
    """HTML decks tab: a left-rail list of decks found under decks/html/, with
    the selected one embedded in an iframe. Empty-state with instructions when
    none exist yet (the tab is intentionally present even when empty)."""
    decks = scan_html_decks()
    if not decks:
        return (
            '<div style="border:1px dashed var(--border);border-radius:8px;'
            'padding:2rem;text-align:center;color:var(--muted);">'
            '<div style="font-size:1.1rem;margin-bottom:0.6rem;">No HTML decks yet.</div>'
            '<div style="font-size:0.82rem;line-height:1.6;max-width:40rem;margin:0 auto;">'
            'Drop a self-contained deck at <code>decks/html/&lt;slug&gt;/index.html</code> '
            '(a deck folder) or <code>decks/html/&lt;slug&gt;.html</code> (a single file) '
            'and it appears here automatically — newest first, embedded live. '
            'Same serving path as the Reorient deck, so use <kbd>←</kbd>/<kbd>→</kbd> '
            'navigation inside the deck if it supports it.</div></div>')

    # Left rail of deck buttons + one iframe that swaps src.
    # Append the file mtime as a cache-buster so the browser never serves a
    # stale copy of a deck that was just edited on disk.
    for d in decks:
        d["path"] = f'{d["path"]}?v={int(d["mtime"])}'
    rail = ""
    for i, d in enumerate(decks):
        active = " active" if i == 0 else ""
        rail += (
            f'<button class="deck-pick{active}" data-src="{html_mod.escape(d["path"])}" '
            f'onclick="pickDeck(this)" '
            f'style="display:block;width:100%;text-align:left;border:1px solid var(--border);'
            f'background:var(--surface);color:var(--text);border-radius:6px;padding:0.5rem 0.7rem;'
            f'margin-bottom:0.5rem;cursor:pointer;font-size:0.82rem;">'
            f'<div style="font-size:0.62rem;color:var(--accent);font-weight:700;letter-spacing:0.03em;">{d["date"]}</div>'
            f'<div style="font-weight:600;margin-top:0.1rem;">{html_mod.escape(d["title"])}</div>'
            + (f'<div style="font-size:0.7rem;color:var(--muted);margin-top:0.3rem;line-height:1.35;">{html_mod.escape(d["purpose"])}</div>'
               if d.get("purpose") else
               f'<div style="font-size:0.68rem;color:var(--muted);margin-top:0.15rem;">{html_mod.escape(d["slug"])} — add a meta.json for its stated purpose</div>')
            + '</button>')

    first = html_mod.escape(decks[0]["path"])
    js = ("<script>function pickDeck(b){"
          "document.querySelectorAll('.deck-pick').forEach(function(x){x.classList.remove('active');});"
          "b.classList.add('active');"
          "var src=b.dataset.src;"
          "document.getElementById('deck-frame').src=src;"
          "document.getElementById('deck-open').href=src;}</script>")
    return (
        f'{js}'
        f'<div style="display:flex;gap:1rem;align-items:flex-start;">'
        f'<div style="flex:0 0 16rem;max-height:calc(100vh - 9rem);overflow:auto;">'
        f'<button onclick="show(\'narrative\')" '
        f'style="display:block;width:100%;text-align:center;margin-bottom:0.6rem;padding:0.45rem 0.7rem;'
        f'border:1px solid var(--border);background:var(--surface2);color:var(--muted);border-radius:6px;'
        f'font-size:0.78rem;cursor:pointer;">&#10005; Exit decks</button>'
        f'{rail}'
        f'<a id="deck-open" href="{first}" target="_blank" '
        f'style="display:block;text-align:center;margin-top:0.4rem;padding:0.55rem 0.7rem;'
        f'background:var(--accent);color:#fff;border-radius:6px;font-size:0.82rem;font-weight:600;'
        f'text-decoration:none;">&#8599; Open full screen (best for presenting)</a>'
        f'<div style="font-size:0.66rem;color:var(--muted);margin-top:0.4rem;line-height:1.4;">'
        f'The deck scales to fit; for a talk, open it full screen in its own tab.</div></div>'
        f'<iframe id="deck-frame" src="{first}" '
        f'style="flex:1;height:calc(100vh - 9rem);border:1px solid var(--border);'
        f'border-radius:6px;background:var(--surface);"></iframe>'
        f'</div>')


def render_scale():
    """The Scale-of-Justice tab: verification debt made physical. Production pan = total
    commits; Verification pan = commits Scott has marked reviewed; the beam tilts by the
    number of UNREVIEWED commits (the debt). Level = caught up. Computed LIVE (git log +
    the review ledger) on every load, so it cannot go stale."""
    import subprocess, json as _json
    if not (ROOT / ".git").exists():
        return ('<p class="empty">No local git repository yet — nothing to weigh. The scale '
                'measures verification debt (commits made) against verification (diffs you have reviewed).</p>')
    total, reviewed = 0, 0
    try:
        raw = subprocess.run(["git", "-C", str(ROOT), "log", "--pretty=format:%H"],
                             capture_output=True, text=True, timeout=10).stdout
        hashes = [x for x in raw.splitlines() if x.strip()]
        total = len(hashes)
        led = ROOT / ".commit_reviews.json"
        rec = {}
        if led.exists():
            try: rec = _json.loads(led.read_text())
            except Exception: rec = {}
        reviewed = sum(1 for h in hashes if h in rec)
    except Exception:
        pass
    debt = total - reviewed
    balanced = (debt == 0 and total > 0)
    # TWO-STATE picture (Scott, 2026-07-09): the beam is either tilted toward production
    # (any unreviewed debt) or level (caught up) — not a proportional angle. Production is on
    # the LEFT and sinks DOWN when debt exists. Driven by a CSS transform so the Diffs tab's
    # "Mark reviewed" button can animate it back to level live (refreshScale()).
    ang = 10 if debt > 0 else 0
    verdict = ("&#9878; Balanced &mdash; every commit reviewed. You are caught up." if balanced
               else (f"{debt} unreviewed commit{'s' if debt != 1 else ''} &mdash; verification debt. "
                     f"Review them in the Diffs tab to level the scale." if total else "No commits yet."))
    vcol = "var(--green)" if balanced else "var(--yellow)"
    # Labels AND count numbers are NO LONGER inside the SVG — they touched/overlapped the pans
    # and are redundant with the legend directly beneath (Scott, 2026-07-09). Only the beam +
    # pans rotate; the counts live in the static legend below.
    svg = f'''<svg viewBox="0 0 400 200" style="max-width:520px;width:100%;">
      <line x1="200" y1="26" x2="200" y2="172" stroke="var(--border)" stroke-width="4"/>
      <polygon points="176,172 224,172 200,196" fill="var(--muted)"/>
      <g id="scale-beam" style="transform:rotate({ang}deg);transform-origin:200px 44px;transition:transform .7s cubic-bezier(.34,1.4,.5,1);">
        <line x1="60" y1="44" x2="340" y2="44" stroke="var(--text)" stroke-width="5" stroke-linecap="round"/>
        <circle cx="200" cy="44" r="7" fill="var(--accent)"/>
        <line x1="60" y1="44" x2="60" y2="86" stroke="var(--muted)" stroke-width="2"/>
        <line x1="340" y1="44" x2="340" y2="86" stroke="var(--muted)" stroke-width="2"/>
        <path d="M22,86 A38,38 0 0 0 98,86 Z" fill="rgba(248,113,113,0.15)" stroke="var(--red)" stroke-width="2"/>
        <path d="M302,86 A38,38 0 0 0 378,86 Z" fill="rgba(52,211,153,0.15)" stroke="var(--green)" stroke-width="2"/>
      </g>
    </svg>'''
    legend = (
        '<div style="display:flex;gap:1.8rem;align-items:center;justify-content:center;font-size:0.8rem;">'
        '<span style="display:inline-flex;align-items:center;gap:0.4rem;">'
        '<span style="width:12px;height:12px;border-radius:3px;background:rgba(248,113,113,0.35);border:1px solid var(--red);"></span>'
        'Production (commits): <b id="scale-legend-prod">' + str(total) + '</b></span>'
        '<span style="display:inline-flex;align-items:center;gap:0.4rem;">'
        '<span style="width:12px;height:12px;border-radius:3px;background:rgba(52,211,153,0.35);border:1px solid var(--green);"></span>'
        'Verified (reviewed): <b id="scale-legend-ver">' + str(reviewed) + '</b></span></div>')
    return (f'<div style="display:flex;flex-direction:column;align-items:center;gap:1rem;">'
            f'{svg}{legend}'
            f'<div id="scale-verdict" style="font-size:1.05rem;font-weight:600;color:{vcol};text-align:center;">{verdict}</div>'
            f'<div style="font-size:0.78rem;color:var(--muted);max-width:560px;text-align:center;line-height:1.5;">'
            f'Production = commits made. Verified = diffs you have reviewed and approved in the Diffs tab. '
            f'The beam tips toward production while any commit is unreviewed &mdash; the verification debt &mdash; '
            f'and settles level once you have reviewed everything. Mark a commit reviewed in the Diffs tab and '
            f'watch this settle. Recomputed live on every load.</div></div>')


CASSETTE_ART = "╭──────────────────────────────────────────────────────╮\n│ ┌──────────────────────────────────────────────────┐ │\n│ │ M I X T A P E   H A R N E S S      [ 90 ]        │ │\n│ │ ················································ │ │\n│ │ a research operating system       SIDE A         │ │\n│ └──────────────────────────────────────────────────┘ │\n│                                                      │\n│      .-------.      ________      .-------.          │\n│     | / . . \\ |    /::::::::::\\    | / . . \\ |       │\n│     |  (( o ))  |  |::::::::::::|  |  (( o ))  |     │\n│     | \\ . . / |    \\::::::::::/    | \\ . . / |       │\n│      '-------'      '''''''''''      '-------'       │\n│ ==================================================== │\n│  (o)                                            (o)  │\n╰──────────────────────────────────────────────────────╯"


def render_home():
    """The Home landing (git projects only). TWO things, in order: (1) the enlarged ASCII
    cassette — the harness's face; (2) the "Today" to-do card beneath it (which stage +
    what's left today, from TODAY.md, written by /amnesia). The four layer launch-cards were
    dropped (Scott, 2026-07-09) — the sidebar already navigates. The verification-debt scale
    was MOVED off Home to the top of the Diffs tab (Scott, 2026-09-21), so it sits beside the
    commits it weighs; render_diffs() is now the only place the scale renders."""
    # "Today" card — written by /amnesia each run (TODAY.md at the project root): which stage
    # we're in + what's left to do today. Rendered just below the scale. Absent-safe: if there's
    # no TODAY.md, the card is omitted.
    today_html = ""
    tf = ROOT / "TODAY.md"
    if tf.exists():
        import datetime as _dt
        raw = tf.read_text()
        stage_line, left_items, hdr_date = "", [], ""
        in_left = False
        for ln in raw.splitlines():
            s = ln.strip()
            if s.startswith("#"):
                m = re.search(r"(\d{4}-\d{2}-\d{2})", s)
                if m:
                    hdr_date = m.group(1)
                continue
            if s.lower().startswith("stage:"):
                stage_line = s.split(":", 1)[1].strip(); in_left = False
            elif s.lower().startswith("left:"):
                in_left = True
                rest = s.split(":", 1)[1].strip()
                if rest:
                    left_items.append(rest)
            elif in_left and s.startswith(("-", "*")):
                left_items.append(s.lstrip("-* ").strip())
        # Freshness: quietly flag if TODAY.md wasn't written today.
        try:
            today_str = _dt.datetime.fromtimestamp(tf.stat().st_mtime).strftime("%Y-%m-%d")
        except Exception:
            today_str = hdr_date
        stale = (hdr_date and today_str and hdr_date != today_str)
        # Each item is a click-to-check row: open box -> checked + struck through. State persists
        # in localStorage keyed by the TODAY.md date + index, so reloads keep the checks — but when
        # /sleep writes a NEW TODAY.md (new date) the keys change and everything comes back fresh.
        day_key = html_mod.escape(hdr_date or today_str)
        if left_items:
            rows = ""
            for i, x in enumerate(left_items):
                rows += (
                    f'<li class="today-item" data-key="td-{day_key}-{i}" onclick="toggleTodo(this)" '
                    f'style="list-style:none;display:flex;gap:0.55rem;align-items:flex-start;cursor:pointer;'
                    f'margin-bottom:0.4rem;padding:0.15rem 0;">'
                    f'<span class="today-box" style="flex:0 0 auto;font-size:1.05rem;line-height:1.35;'
                    f'color:#D97706;">&#9744;</span>'
                    f'<span class="today-text" style="flex:1;">{html_mod.escape(x)}</span></li>')
            left_html = rows
        else:
            left_html = '<li style="list-style:none;color:var(--muted);">(nothing recorded — run /amnesia)</li>'
        stamp = (f'<span style="font-size:0.66rem;color:var(--muted);font-family:\'SF Mono\',monospace;">'
                 f'{html_mod.escape(hdr_date or today_str)}'
                 + (' · may be stale' if stale else '') + '</span>')
        today_html = (
            f'<div style="border:1px solid var(--border);border-left:4px solid #D97706;border-radius:12px;'
            f'background:var(--surface);padding:1.1rem 1.4rem;margin-bottom:1.4rem;">'
            f'<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:0.6rem;">'
            f'<span style="font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;color:#D97706;'
            f'font-weight:700;">&#9675; Today</span>{stamp}</div>'
            + (f'<div style="font-size:0.92rem;margin-bottom:0.55rem;"><b>Stage:</b> '
               f'{html_mod.escape(stage_line)}</div>' if stage_line else '')
            + f'<div style="font-size:0.82rem;color:var(--muted);margin-bottom:0.35rem;"><b>Left to do today:</b> '
            f'<span style="font-weight:400;">click a box to cross it off</span></div>'
            f'<ul style="margin:0;padding:0;font-size:0.9rem;line-height:1.45;">{left_html}</ul></div>')
    return (
        f'<div style="max-width:1000px;margin:0 auto;">'
        # (1) The cassette — the harness's face, enlarged, standing alone. The
        # verification-debt scale that used to sit under it now lives on the Diffs tab,
        # next to the commits it weighs (Scott, 2026-09-21).
        f'<pre class="cassette">{CASSETTE_ART}</pre>'
        # (2) Today's to-do, below the cassette.
        f'{today_html}'
        f'</div>')


def render_diffs():
    """The Diffs tab: local-git commit history for the active project, with the green/red
    diff of each commit rendered in-browser. Read-only (log/show only; never writes, never
    pushes). Empty-state if the project is not a git repo. The point (Paul GP essay 8): the
    bounded diff is the unit of verification — review one small change at a time, visually."""
    if not (ROOT / ".git").exists():
        return ('<p class="empty">This project is not a local git repository yet, so there is no '
                'commit history to show. Diffs appear here once the project is under local git '
                '(local-only — nothing is ever pushed anywhere).</p>')
    # A GRID of compact commit cards (mirrors the figure cards): click one and it "jumps and
    # floats" open into the fullscreen flip modal below. Front of the open card = the green/red
    # diff; back = the two git dates (authored / committed) + the review sign-off. ← / → rotate
    # through commits inside the modal, exactly like the figure lightbox.
    grid = (
        # The verification-debt scale, FULL SIZE, at the top of this tab (Scott, 2026-09-21).
        # It moved here from Home so it sits beside the commits it actually weighs. This is
        # now the only place it renders, so it keeps render_scale()'s own element ids and the
        # live refreshScale() re-weighs it the moment you mark a commit reviewed.
        '<div style="border:1px solid var(--border);border-radius:14px;background:var(--surface);'
        'padding:1.5rem 1.5rem 1.7rem;margin-bottom:1.3rem;">'
        + render_scale() +
        '</div>'
        # UNDER CONSTRUCTION panel (Scott, 2026-09-23). This tab is the least settled part of
        # the harness, so it says so out loud, and says what it is trying to be: the place where
        # the acceptance step that git assumes — but that agentic work breaks — gets put back.
        # Collapsed by default so it does not crowd the commits; the summary row is the toggle.
        '<details style="border:1px solid var(--yellow);border-radius:12px;background:var(--surface2);'
        'margin-bottom:1.2rem;">'
        '<summary style="cursor:pointer;padding:0.7rem 1rem;font-size:0.8rem;font-weight:700;'
        'color:var(--yellow);list-style:none;">&#9888;&#65039; Under construction &mdash; what this tab '
        '<span style="font-weight:400;color:var(--muted);">is for, and what it does not do yet</span></summary>'
        '<div style="padding:0 1.3rem 1.2rem;font-size:0.85rem;line-height:1.65;color:var(--text);">'

        '<p style="margin:0 0 0.9rem;"><b>The goal.</b> Every change to this project gets read by a '
        'person, one bounded diff at a time, and the fact that it was read gets written down.</p>'

        '<p style="margin:0 0 0.9rem;"><b>How git normally handles this.</b> You edit, run '
        '<code>git diff</code> to read what changed, stage what you want, and commit. The reading '
        'happens <i>before</i> the commit &mdash; the commit <i>is</i> the acceptance. Nothing needs '
        'tracking afterward, because the person who wrote the change is the person who approved it. '
        'Git has no separate review step because, historically, it never needed one.</p>'

        '<p style="margin:0 0 0.9rem;"><b>Why that assumption breaks here.</b> When an agent writes '
        'the code and commits it, the writer and the approver are no longer the same person. The '
        'commit still gets made, but it no longer carries the meaning it used to: nobody has '
        'necessarily read anything. This is a principal&ndash;agent problem. The agent produces far '
        'faster than the principal can verify, and the receipt that used to certify acceptance keeps '
        'being issued regardless.</p>'

        '<p style="margin:0 0 0.9rem;"><b>What this tab does today.</b> It reads committed history '
        '(<code>git log</code>, <code>git show</code> &mdash; local only, no network) and keeps its own '
        'ledger of which commits you have marked reviewed. The scale above weighs commits made '
        'against commits read. Git itself is never written to.</p>'

        '<p style="margin:0 0 0.9rem;"><b>Known gap.</b> Only committed history appears here. If an '
        'agent edits files and does not commit, this tab shows nothing &mdash; the working tree is '
        'invisible to it.</p>'

        '<p style="margin:0;"><b>Open question.</b> Whether reviewing after the commit is the right '
        'shape at all, or whether the acceptance step belongs before it, where git puts it.</p>'
        '</div></details>'
        '<div id="diff-counter" style="font-size:0.75rem;color:var(--muted);margin-bottom:0.6rem;">loading…</div>'
        '<div id="diff-grid" class="ds-grid"></div>')
    # Fullscreen flip modal — reuses .ds-overlay / .ds-modal / .ds-flip / .fig-nav from the
    # figure lightbox so the float-open, flip, and arrow-nav feel identical.
    modal = (
        '<div id="diff-overlay" class="ds-overlay" onclick="if(event.target===this)closeDiff()">'
        '  <button class="fig-nav fig-prev" onclick="stepDiffModal(-1)" title="Older commit (&#8592;)">&#8249;</button>'
        '  <button class="fig-nav fig-next" onclick="stepDiffModal(1)" title="Newer commit (&#8594;)">&#8250;</button>'
        '  <div class="ds-modal fig-modal">'
        '    <button class="ds-x" onclick="closeDiff()" title="Close (Esc)">&#10005;</button>'
        # Whole card toggles on click (like the figure modal) — except on real controls or
        # inside the scrollable diff text (so selecting/scrolling the patch never flips it).
        '    <div id="diff-flip" class="ds-flip clickflip" onclick="diffCardClick(event)">'
        '      <div class="ds-inner">'
        # ---- FRONT: the diff ----
        '        <div class="ds-front fig-front-modal">'
        '          <div class="fig-modal-eyebrow" id="diff-front-eyebrow">Commit diff</div>'
        '          <div id="diff-subject" style="font-weight:800;font-size:1.15rem;line-height:1.2;color:var(--text);margin-bottom:0.15rem;">—</div>'
        '          <div id="diff-meta" style="font-size:0.72rem;color:var(--muted);font-family:\'SF Mono\',monospace;margin-bottom:0.9rem;"></div>'
        '          <div id="diff-patch" style="flex:1;min-height:0;overflow:auto;font-family:\'SF Mono\',monospace;'
        '            font-size:0.72rem;white-space:pre-wrap;word-break:break-word;background:var(--surface2);'
        '            border:1px solid var(--border);border-radius:10px;padding:0.9rem 1.1rem;">loading diff…</div>'
        '          <div class="fig-modal-bar">'
        '            <span id="diff-badge" style="padding:0.15rem 0.6rem;border-radius:10px;font-size:0.68rem;font-weight:600;"></span>'
        '            <button id="diff-fulltoggle" class="ds-flipbtn" onclick="event.stopPropagation();toggleDiffFull()">Show full context</button>'
        '            <button class="ds-flipbtn" onclick="flipDiffModal(true)">Dates &amp; verification &#8594;</button>'
        '          </div>'
        '        </div>'
        # ---- BACK: dates + review ----
        '        <div class="ds-back fig-back-modal">'
        '          <div class="fig-modal-eyebrow">When this was produced</div>'
        '          <div id="diff-back-subject" style="font-weight:800;font-size:1.2rem;line-height:1.2;color:var(--text);margin-bottom:1.2rem;">—</div>'
        '          <div class="ds-grid2" style="margin-bottom:1.6rem;">'
        '            <div class="ds-k">Authored</div><div class="ds-v" id="diff-adate">—</div>'
        '            <div class="ds-k">Committed</div><div class="ds-v" id="diff-cdate">—</div>'
        '            <div class="ds-k">Commit</div><div class="ds-v" id="diff-hash" style="font-family:\'SF Mono\',monospace;">—</div>'
        '          </div>'
        '          <div style="font-size:0.8rem;color:var(--muted);line-height:1.6;max-width:60ch;margin-bottom:1.2rem;">'
        '            <b>Authored</b> is when the change was originally written; <b>committed</b> is when it '
        '            entered the repository. They match unless the commit was later amended or rebased. '
        '            Marking a commit reviewed records your sign-off — that is what pays down verification debt on the scale.</div>'
        '          <div style="display:flex;align-items:center;gap:0.9rem;">'
        '            <button id="diff-reviewbtn" onclick="toggleReview()" style="padding:0.5rem 1rem;'
        '              border:1px solid var(--border);border-radius:8px;cursor:pointer;font-size:0.8rem;font-weight:600;">&#10003; Mark reviewed</button>'
        '            <button class="ds-flipbtn" style="margin-top:0;" onclick="flipDiffModal(false)">&#8592; Back to diff</button>'
        '          </div>'
        '        </div>'
        '      </div>'
        '    </div>'
        '  </div>'
        '</div>')
    return grid + modal



def render_skills_hooks():
    """Skills & Hooks tab — a showable, flip-through index-card view of the harness.
    Two iconic toggles (Skills / Hooks); a big carousel of index cards (arrow-key or
    button nav, click to flip). Front = what it does; back = examples / when to use.
    Content is authored here (static, harness-wide — same for every project). Fully
    self-contained CSS/JS scoped under #v-skills_hooks so it never collides with the
    shared dashboard. Added 2026-08-23 (Scott)."""
    SKILLS = [
        {"icon": "\U0001F50D", "cmd": "/referee2", "name": "Referee 2", "color": "var(--accent)",
         "tag": "The adversarial audit",
         "front": "A fresh, hostile reviewer in a separate session — never the Claude that built the thing. Three modes: <b>deck</b> (rhetoric + visuals + compile), <b>code</b> (cross-language replication + econometric audit), <b>drift</b> (reconcile every sample N against the anchor).",
         "back": "Run <b>code</b> before a submission, <b>deck</b> before a talk, <b>drift</b> to hunt silent sample-drift bugs. It caught a hand-coded estimator that wasn't the estimator it claimed to be — and a bootstrap p-value bug — both already committed and locked. <i>Your workhorse: used ×29 here.</i>"},
        {"icon": "\U0001F9E0", "cmd": "/amnesia", "name": "Amnesia", "color": "#38bdf8",
         "tag": "Session reload",
         "front": "The first command of any session. Reconciles STATE.md against git + disk (auto-fixing drifted facts), then reloads you <i>through a 5-question interview</i> — retrieving the state re-seats you better than reading a summary — and writes today's to-do.",
         "back": "Say “amnesia”, “where were we”, “get me up to speed.” Stage mode: “amnesia bite” reloads one checklist room and locks focus there. <i>You are literally inside it right now.</i>"},
        {"icon": "\U0001F319", "cmd": "/sleep", "name": "Sleep", "color": "#a78bfa",
         "tag": "End-of-session handoff",
         "front": "The bookend to Amnesia. Writes a dated progress log, updates STATE.md, and writes tomorrow's TODAY.md — so the next session opens onto a clean handoff instead of a cold start.",
         "back": "Say “sleep”, “wrap up”, “let's stop here.” Every <code>SLEEP …</code> commit in the git log is this skill closing a session. The loop: /sleep writes the handoff → /amnesia reads it back."},
        {"icon": "\U0001F4CB", "cmd": "/covariates", "name": "Covariates", "color": "var(--green)",
         "tag": "The Y(0) interview",
         "front": "Interview-based covariate selection for DiD / synth. Five questions, one at a time, then it synthesizes “the 10-chapter book by the world's leading expert on your outcome's untreated trend” — those ten chapters <i>are</i> your covariates.",
         "back": "Grounded in Heckman, Ichimura & Todd (1997): find the X that drives E[Y(0)] trends, not just comparable levels. Then it suggests data sources and fetches them once you confirm. <i>Used ×12 to pin the model's predictors.</i>"},
        {"icon": "\U0001F4C4", "cmd": "/three-pager", "name": "Three-Pager", "color": "#f59e0b",
         "tag": "Deck → deliverable",
         "front": "Turns a finished deck into a numbered Word (.docx) three-pager in the house format — per-section agents draft it, one assembler stitches it together.",
         "back": "<b>HARD GATE:</b> every deck figure/table must embed in the doc, or it STOPS. Built the manuscript .docx this way (all exhibits embedded, gate passed). <i>Used ×12.</i>"},
        {"icon": "\U0001F441", "cmd": "/blindspot", "name": "Blindspot", "color": "#ec4899",
         "tag": "Peripheral-vision audit",
         "front": "Finds what the author can't see — problems hiding in plain sight (<b>vices</b>) and opportunities being overlooked (<b>virtues</b>). Defamiliarization (Shklovsky) applied to empirical output.",
         "back": "Run it the moment output exists, <i>before</i> interpretation begins — same session is fine; it needs the person closest to the work. Flagged the broken raw-count pre-trend that the per-unit rate later fixed."},
        {"icon": "\U0001F393", "cmd": "/quiz", "name": "Quiz", "color": "#22d3ee",
         "tag": "Understanding check",
         "front": "Seven multiple-choice questions, one at a time, to check you <i>actually understand</i> a diff, an analysis, a decision, or a stage's evidence — and it scores you.",
         "back": "“quiz me on the evidence for X.” Grounded in Geoffrey Litt's “understanding is the new bottleneck”: the SCORE, not a click, is what pays down understanding debt. <i>Used ×10 — more than you'd have guessed.</i>"},
        {"icon": "\U0001F5C2", "cmd": "/outline", "name": "Outline", "color": "#94a3b8",
         "tag": "Paper structuring",
         "front": "Reads your completed pipeline first, then interviews you (five questions, one follow-up each) and recommends a ~3-page paper outline plus a long technical appendix — what goes in the paper vs. what goes in the back.",
         "back": "“outline the paper” / “what goes in the paper vs the appendix.” Sibling of /manuscript and /covariates. <i>Used ×8.</i>"},
        {"icon": "\U0001F4DA", "cmd": "/split-pdf", "name": "Split-PDF", "color": "#14b8a6",
         "tag": "Deep-read a paper",
         "front": "Download, split, and deeply read an academic PDF. Splits it into 4-page chunks, reads them in small batches, and produces structured reading notes — avoiding the context-window crash <i>and</i> the shallow skim.",
         "back": "Every academic paper, every time (skip only under ~15 pages). Used on victor.pdf (Chernozhukov–Wüthrich–Zhu, conformal inference for synthetic control) → <code>readings/victor_notes/</code>. Say “read / review / summarize this paper.”"},
        {"icon": "\U0001F3A8", "cmd": "/beautiful_deck", "name": "Beautiful Deck", "color": "#fb7185",
         "tag": "The Beamer machine",
         "front": "End-to-end beautiful Beamer deck: an original theme designed for the audience, an ethos / pathos / logos restructure, figures generated from code first, zero-warning compile, then a /tikz pass for visual-collision cleanup.",
         "back": "Fire it when a deck doesn't exist yet or needs a full rebuild. <i>Note: some projects' decks are HTML, so you may use this in sibling projects — it's in your toolkit, not this project's history.</i>"},
    ]
    HOOKS = [
        {"icon": "\U0001F6E1", "cmd": "protect-raw-data", "name": "Protect Raw Data", "color": "var(--green)",
         "tag": "PreToolUse · Edit / Write",
         "front": "Blocks any edit or write to a <code>data/raw/</code> file, in any project. Raw source data is immutable — every transform reads raw and writes a <i>derived</i> dir.",
         "back": "A hard exit-2 wall the agent cannot walk through, independent of whether it remembers the rule. Reading raw data is fine — only writes and edits are blocked. Enforces DCAS #2 (data availability)."},
        {"icon": "\U0001F6AB", "cmd": "no-fabricated-exhibit", "name": "No Fabricated Exhibit", "color": "var(--red)",
         "tag": "PreToolUse · Edit / Write",
         "front": "Blocks a figure/table script whose text says synthetic / illustrative / made-up / placeholder — <i>unless</i> it's an acknowledged Monte Carlo (the one carve-out).",
         "back": "Guards the <b>exposition door</b> the raw-data hook can't see. Prevents the incident that created the rule: an “illustrative synthetic” county series drawn on a slide bound for a reviewer, with a footnote. A footnote is not a defense."},
        {"icon": "⛔", "cmd": "no-offbook-exhibit", "name": "No Off-Book Exhibit", "color": "var(--red)",
         "tag": "PreToolUse · Bash",
         "front": "Blocks drawing a figure/table in an ad-hoc shell (<code>python -c “…savefig”</code>, <code>Rscript -e “…ggsave”</code>). Every exhibit must be born in a <b>named script</b> in <code>code/</code>.",
         "back": "A picture with no producer file can't be re-run, re-styled, audited, or reconciled — so “you're done” can't survive to the next session. Prefix <code>SCRATCH=1</code> to acknowledge a genuine throwaway exploration."},
        {"icon": "\U0001F517", "cmd": "deck-from-pipeline", "name": "Deck From Pipeline", "color": "var(--accent)",
         "tag": "PostToolUse · decks/*.html + *.tex",
         "front": "Every exhibit a deck or manuscript references must be produced by a script <b>wired into</b> <code>run_pipeline.sh</code>. “Exists on disk” / “ran once in chat” is not enough.",
         "back": "Prevents the GlanceViews incident: a whole outcome decked from 9 scripts, not one of them wired into the runner — caught only by memory, days later. If the runner can't rebuild it, it can't be shown."},
        {"icon": "\U0001F4CC", "cmd": "no-stale-canon", "name": "No Stale Canon", "color": "var(--yellow)",
         "tag": "PostToolUse · warns, doesn't block",
         "front": "When a stage's <code>exhibits.md</code> gets a CANON-closure line, it checks every listed exhibit and warns if any is <b>MISSING</b>, <b>UNWIRED</b>, or <b>STALE</b> (figure older than its script).",
         "back": "The certainty fence. “If I'm going to make 5× as much stuff, I need to be 5× as sure it's right.” Every canonized exhibit traces to a real, live, wired file — or you hear about it <i>right then</i>, not days later from memory."},
    ]

    def _cards(items):
        out = ""
        for i, it in enumerate(items):
            out += (
                '<div class="sh-card" data-idx="{i}" onclick="shFlip(this)">'
                '<div class="sh-inner">'
                '<div class="sh-face sh-front" style="border-top-color:{color}">'
                '<div class="sh-icon">{icon}</div>'
                '<div class="sh-cmd">{cmd}</div>'
                '<div class="sh-name">{name}</div>'
                '<div class="sh-tag">{tag}</div>'
                '<div class="sh-desc">{front}</div>'
                '<div class="sh-hint">click card to flip &#8594;</div>'
                '</div>'
                '<div class="sh-face sh-back" style="border-top-color:{color}">'
                '<div class="sh-back-label">In practice</div>'
                '<div class="sh-desc">{back}</div>'
                '<div class="sh-hint">&#8592; click to flip back</div>'
                '</div></div></div>'
            ).format(i=i, color=it["color"], icon=it["icon"], cmd=html_mod.escape(it["cmd"]),
                     name=it["name"], tag=it["tag"], front=it["front"], back=it["back"])
        return out

    skills_cards = _cards(SKILLS)
    hooks_cards = _cards(HOOKS)

    style = """
    <style>
    #v-skills_hooks .sh-toggle{display:flex;gap:0.6rem;margin:0.2rem 0 1.4rem;}
    #v-skills_hooks .sh-tab{flex:0 0 auto;display:flex;align-items:center;gap:0.55rem;
      padding:0.6rem 1.15rem;border:1px solid var(--border);border-radius:0.7rem;
      background:var(--surface);color:var(--muted);cursor:pointer;font-size:0.9rem;
      font-weight:600;transition:all .18s ease;user-select:none;}
    #v-skills_hooks .sh-tab .sh-tab-ic{font-size:1.15rem;line-height:1;}
    #v-skills_hooks .sh-tab:hover{border-color:var(--accent);color:var(--text);transform:translateY(-1px);}
    #v-skills_hooks .sh-tab.on{background:var(--accent);border-color:var(--accent);color:#fff;
      box-shadow:0 4px 14px rgba(139,92,246,0.28);}
    #v-skills_hooks .sh-tab .sh-count{font-size:0.72rem;opacity:0.75;font-weight:500;
      background:var(--surface3);color:var(--text);border-radius:1rem;padding:0.05rem 0.5rem;}
    #v-skills_hooks .sh-tab.on .sh-count{background:rgba(255,255,255,0.22);color:#fff;}
    #v-skills_hooks .sh-collection{display:none;}
    #v-skills_hooks .sh-collection.on{display:block;}
    #v-skills_hooks .sh-stage{display:flex;align-items:center;justify-content:center;gap:1.1rem;}
    #v-skills_hooks .sh-arrow{flex:0 0 auto;width:2.9rem;height:2.9rem;border-radius:50%;
      border:1px solid var(--border);background:var(--surface);color:var(--text);
      font-size:1.3rem;cursor:pointer;display:flex;align-items:center;justify-content:center;
      transition:all .16s ease;}
    #v-skills_hooks .sh-arrow:hover:not(:disabled){border-color:var(--accent);color:var(--accent);
      transform:scale(1.08);}
    #v-skills_hooks .sh-arrow:disabled{opacity:0.3;cursor:default;}
    #v-skills_hooks .sh-deck{flex:0 1 560px;perspective:1600px;min-height:430px;position:relative;}
    #v-skills_hooks .sh-card{display:none;cursor:pointer;}
    #v-skills_hooks .sh-card.on{display:block;animation:shIn .32s cubic-bezier(.2,.7,.3,1);}
    @keyframes shIn{from{opacity:0;transform:translateY(10px) scale(.985);}to{opacity:1;transform:none;}}
    #v-skills_hooks .sh-inner{position:relative;width:100%;min-height:430px;
      transition:transform .55s cubic-bezier(.4,.15,.2,1);transform-style:preserve-3d;}
    #v-skills_hooks .sh-card.flipped .sh-inner{transform:rotateY(180deg);}
    #v-skills_hooks .sh-face{position:absolute;inset:0;backface-visibility:hidden;
      -webkit-backface-visibility:hidden;background:var(--surface);border:1px solid var(--border);
      border-top:4px solid var(--accent);border-radius:1rem;padding:2rem 2.1rem;
      box-shadow:0 10px 34px rgba(0,0,0,0.22);display:flex;flex-direction:column;}
    #v-skills_hooks .sh-back{transform:rotateY(180deg);}
    #v-skills_hooks .sh-icon{font-size:2.5rem;line-height:1;margin-bottom:0.7rem;}
    #v-skills_hooks .sh-cmd{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:0.82rem;
      color:var(--accent);background:var(--surface2);border:1px solid var(--border);
      border-radius:0.4rem;padding:0.15rem 0.5rem;align-self:flex-start;margin-bottom:0.65rem;}
    #v-skills_hooks .sh-name{font-family:'Cormorant Garamond',Georgia,serif;font-size:2rem;
      font-weight:600;line-height:1.05;color:var(--text);margin-bottom:0.15rem;}
    #v-skills_hooks .sh-tag{font-size:0.82rem;font-weight:600;color:var(--muted);
      text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.9rem;}
    #v-skills_hooks .sh-desc{font-size:0.98rem;line-height:1.55;color:var(--text);opacity:0.92;}
    #v-skills_hooks .sh-back-label{font-size:0.72rem;font-weight:700;letter-spacing:0.09em;
      text-transform:uppercase;color:var(--accent);margin-bottom:0.9rem;}
    #v-skills_hooks .sh-back .sh-desc{opacity:0.95;}
    #v-skills_hooks .sh-hint{margin-top:auto;padding-top:1rem;font-size:0.72rem;color:var(--muted);
      opacity:0.7;font-style:italic;}
    #v-skills_hooks .sh-dots{display:flex;justify-content:center;gap:0.45rem;margin-top:1.3rem;}
    #v-skills_hooks .sh-dot{width:0.5rem;height:0.5rem;border-radius:50%;background:var(--surface3);
      cursor:pointer;transition:all .16s ease;}
    #v-skills_hooks .sh-dot:hover{background:var(--muted);}
    #v-skills_hooks .sh-dot.on{background:var(--accent);transform:scale(1.25);}
    #v-skills_hooks .sh-pos{text-align:center;font-size:0.78rem;color:var(--muted);margin-top:0.7rem;}
    </style>
    """

    body = (
        '<div class="sh-toggle">'
        '<div class="sh-tab on" data-mode="skills" onclick="shMode(\'skills\')">'
        '<span class="sh-tab-ic">\U0001F6E0</span> Skills <span class="sh-count">' + str(len(SKILLS)) + '</span></div>'
        '<div class="sh-tab" data-mode="hooks" onclick="shMode(\'hooks\')">'
        '<span class="sh-tab-ic">\U0001FA9D</span> Hooks <span class="sh-count">' + str(len(HOOKS)) + '</span></div>'
        '</div>'
        '<div class="sh-collection on" id="sh-col-skills">'
        '<div class="sh-stage"><button class="sh-arrow" id="sh-prev-skills" onclick="shNav(\'skills\',-1)">&#8592;</button>'
        '<div class="sh-deck" id="sh-deck-skills">' + skills_cards + '</div>'
        '<button class="sh-arrow" id="sh-next-skills" onclick="shNav(\'skills\',1)">&#8594;</button></div>'
        '<div class="sh-dots" id="sh-dots-skills"></div><div class="sh-pos" id="sh-pos-skills"></div></div>'
        '<div class="sh-collection" id="sh-col-hooks">'
        '<div class="sh-stage"><button class="sh-arrow" id="sh-prev-hooks" onclick="shNav(\'hooks\',-1)">&#8592;</button>'
        '<div class="sh-deck" id="sh-deck-hooks">' + hooks_cards + '</div>'
        '<button class="sh-arrow" id="sh-next-hooks" onclick="shNav(\'hooks\',1)">&#8594;</button></div>'
        '<div class="sh-dots" id="sh-dots-hooks"></div><div class="sh-pos" id="sh-pos-hooks"></div></div>'
    )

    script = """
    <script>
    window.SH = window.SH || {mode:'skills', idx:{skills:0, hooks:0}, init:false};
    function shDeck(m){return document.getElementById('sh-deck-'+m);}
    function shCards(m){return shDeck(m).querySelectorAll('.sh-card');}
    function shRender(m){
      var cards = shCards(m), n = cards.length, i = SH.idx[m];
      cards.forEach(function(c,k){c.classList.toggle('on', k===i); if(k!==i) c.classList.remove('flipped');});
      var prev=document.getElementById('sh-prev-'+m), next=document.getElementById('sh-next-'+m);
      if(prev) prev.disabled = (i===0);
      if(next) next.disabled = (i===n-1);
      var dots=document.getElementById('sh-dots-'+m);
      if(dots && dots.children.length!==n){
        dots.innerHTML='';
        for(var k=0;k<n;k++){var d=document.createElement('div');d.className='sh-dot';
          (function(kk){d.onclick=function(e){e.stopPropagation();SH.idx[m]=kk;shRender(m);};})(k);
          dots.appendChild(d);}
      }
      if(dots) Array.prototype.forEach.call(dots.children,function(d,k){d.classList.toggle('on',k===i);});
      var pos=document.getElementById('sh-pos-'+m); if(pos) pos.textContent=(i+1)+' / '+n;
    }
    function shNav(m,delta){
      var n=shCards(m).length, i=SH.idx[m]+delta;
      if(i<0)i=0; if(i>n-1)i=n-1; SH.idx[m]=i; shRender(m);
    }
    function shFlip(card){card.classList.toggle('flipped');}
    function shMode(m){
      SH.mode=m;
      document.querySelectorAll('#v-skills_hooks .sh-tab').forEach(function(t){t.classList.toggle('on',t.dataset.mode===m);});
      document.getElementById('sh-col-skills').classList.toggle('on', m==='skills');
      document.getElementById('sh-col-hooks').classList.toggle('on', m==='hooks');
      shRender(m);
    }
    function shInitOnce(){
      if(SH.init) return; SH.init=true;
      shRender('skills'); shRender('hooks');
      document.addEventListener('keydown', function(e){
        var v=document.getElementById('v-skills_hooks');
        if(!v || !v.classList.contains('active')) return;
        if(e.target && /INPUT|TEXTAREA/.test(e.target.tagName)) return;
        if(e.key==='ArrowLeft'){shNav(SH.mode,-1);} else if(e.key==='ArrowRight'){shNav(SH.mode,1);}
      });
    }
    if(document.readyState!=='loading'){shInitOnce();}else{document.addEventListener('DOMContentLoaded',shInitOnce);}
    </script>
    """
    return style + body + script



def build_page(hypotheses, insights, decisions, pipeline, figures, code_files, data_entries):
    # Grouped-spine dashboard. Base (non-git) tabs; git adds Home and Diffs.
    # Groups: The Map (Decks · Template), The Checklist (Checklist · Diffs),
    # The Evidence (Figures · Tables · Decisions), The Machinery (Code · Data · Skills & Hooks).
    tabs = [
        ("decks", "Decks"),
        ("narrative", "Template"),
        ("checklist_per_analysis", "Checklist"),
        ("figures", "Figures"),
        ("tables", "Tables"),
        ("decisions", "Decisions"),
        ("code", "Code"),
        ("data", "Data"),
        ("skills_hooks", "Skills & Hooks"),
    ]
    # Git projects land on a HOME tab (the cassette + today's to-do) and gain a Diffs tab (the
    # bounded diff as the unit of verification) — Diffs sits in The Checklist group, right after
    # Checklist. Gated on a local .git dir so a non-git clone stays lean. The in-page Chat tab was
    # removed from the nav (Scott, 2026-09-23); you talk to Claude in the terminal, not here.
    _home = (ROOT / ".git").exists()
    if _home:
        tabs.insert(0, ("home", "Home"))
        _cl_idx = next(i for i, (tid, _) in enumerate(tabs) if tid == "checklist_per_analysis")
        tabs[_cl_idx + 1:_cl_idx + 1] = [("diffs", "Diffs")]
    _default_tab = "home" if _home else "decks"
    nav_groups = {"decks": "The Map", "checklist_per_analysis": "The Checklist",
                  "figures": "The Evidence", "code": "The Machinery"}
    group_classes = {"The Map": "group-map", "The Checklist": "group-checklist",
                     "The Evidence": "group-evidence", "The Machinery": "group-machinery"}

    nav_html = f'<div class="title">Mixtape Harness</div><button class="theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Theme: auto / light / dark"><span class="theme-icon" id="theme-icon">&#9790;</span><span id="theme-label">Dark</span></button>'
    for tab_id, tab_label in tabs:
        if tab_id in nav_groups and nav_groups[tab_id] is not None:
            grp = nav_groups[tab_id]
            cls = group_classes.get(grp, "")
            nav_html += f'<div class="group {cls}">{grp}</div>'
        active = " active" if tab_id == _default_tab else ""
        nav_html += f'<button class="btn{active}" data-tab="{tab_id}" onclick="show(\'{tab_id}\')">{tab_label}</button>'

    # Reorient banner — the "video tape"
    reorient_html = ""
    audits_recent = scan_audits()
    na_file = ROOT / "NEXT_ACTIONS.md"
    if audits_recent or na_file.exists():
        last_audit = audits_recent[0] if audits_recent else None
        na_lines = []
        if na_file.exists():
            na_lines = [l.strip().lstrip("0123456789. ") for l in na_file.read_text().split("\n") if l.strip() and not l.startswith("#")][:3]
        reorient_parts = []
        if last_audit:
            reorient_parts.append(f'<strong>Last session ({last_audit["date"]}):</strong> {html_mod.escape(last_audit["conclusion"])}')
        if na_lines:
            reorient_parts.append('<strong>Next:</strong> ' + " · ".join(html_mod.escape(l) for l in na_lines))
        if reorient_parts:
            reorient_html = f'<div class="reorient-banner">{"<br>".join(reorient_parts)}</div>'

    _ph = 'color:var(--muted);font-size:0.85rem;line-height:1.6;max-width:60ch;padding:1.5rem;border:1px dashed var(--border);border-radius:8px;background:var(--surface);'
    views = f"""
    <div class="view{' active' if _home else ''}" id="v-home"><h2>Verification Debt</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">Where you always land. The scale weighs work <em>produced</em> (commits) against work <em>verified</em> (diffs you reviewed) — accept a diff in the Diffs tab and it settles live. Below it, today's to-do (from <code>TODAY.md</code>).</p>{render_home() if _home else ''}</div>
    <div class="view{'' if _home else ' active'}" id="v-decks"><h2>Decks</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">Self-contained HTML decks under <code>decks/html/</code>, embedded live and newest-first. Pick one from the rail; it renders in place.</p>{render_decks()}</div>
    <div class="view" id="v-narrative"><h2>Template</h2>{reorient_html}<p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">The research-appendix genre — the standing pattern the write-up follows. The empty form; no project findings.</p>{render_narrative(hypotheses, insights)}</div>
    <div class="view" id="v-checklist_per_analysis"><h2>Checklist</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">The methodological gate upstream of everything. <strong>Click an analysis row</strong> to open its stages and their exhibits in place — each figure/table flips from the exhibit to its description to the scrollable source code that made it (Esc backs out). Per-analysis grid + Step 0 package cards below. Every DiD analysis instantiates <code>analyses/&lt;slug&gt;/checklist.md</code> from the template — the AI invokes <code>/checklist</code> to walk Steps 0–11.</p>{render_checklist_per_analysis()}</div>
    <div class="view" id="v-diffs"><h2>Diffs</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">Local git history for this project — the <strong>bounded diff as the unit of verification</strong>. Click a commit card and it floats open into a full-screen view — the front shows only what changed (green added / red removed); hit "Show full context" to expand, or flip the card for authored/committed dates and the review sign-off. Use ← → to walk commits. Mark a commit reviewed once you agree with it — that pays down verification debt and the scale settles live. Read-only on git: the dashboard runs <code>git log</code>/<code>git show</code> only, never commits or pushes.</p>{render_diffs()}</div>
    <div class="view" id="v-figures"><h2>Figures</h2><div style="{_ph}">Flip-card gallery of pipeline-produced figures. Each card shows the figure with its source script and a status badge; click a card to flip it for full provenance (script path, line number, approval state). This tab is populated automatically once the analysis pipeline emits figures to <code>output/figures/</code>. It is empty until then — nothing appears here that the runner did not produce.</div></div>
    <div class="view" id="v-tables"><h2>Tables</h2><div style="{_ph}">Flip-card gallery of pipeline-produced tables. Each card shows a table with the source script that generated it and a status badge; click to flip for provenance and approval state. This tab is populated automatically once the analysis pipeline emits tables to <code>output/tables/</code>. It is empty until then — every table shown traces back to a wired script.</div></div>
    <div class="view" id="v-decisions"><h2>Decisions</h2><div style="{_ph}">Audit trail of binding design decisions. Each entry records the choice that was made, the alternatives that were considered, and the rationale for the pick — so every downstream number can be traced back to a logged decision. Once a decision is committed here, every script downstream must respect it. Empty until the first decision is logged.</div></div>
    <div class="view" id="v-code"><h2>Code</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">The workshop. Pipeline = verified and approved. For Review = needs verification. Sandbox = experimental.</p>{render_code_unified(pipeline, code_files)}</div>
    <div class="view" id="v-data"><h2>Data</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">Raw source datasets. What we have, where it came from, what consumes it. The raw materials — immutable, never edited in place.</p>{render_data(data_entries)}</div>
    <div class="view" id="v-skills_hooks"><h2>Skills &amp; Hooks</h2><p style="color:var(--muted);font-size:0.78rem;margin-bottom:1rem;">The harness you actually work with. <strong>Skills</strong> are commands you invoke in the Claude Code terminal; <strong>Hooks</strong> are silent guardrails that fire on every tool call. Toggle between them, then flip through the index cards — front is what it does, back is how it's used. Use &#8592; &#8594; or the arrows; click a card to flip.</p>{render_skills_hooks()}</div>
    """

    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>Mixtape Harness</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
    <style>{CSS}</style></head><body>
    <nav>{nav_html}</nav><main>{render_epigraph()}{views}</main>
    <script>window.PIN_STAGES = {json_top.dumps(list_analysis_stages())};</script>
    <script>{JS}</script></body></html>"""


# =============================================================================
# SERVER
# =============================================================================

MANIFEST_PATH = ROOT / "PIPELINE_MANIFEST.json"


def read_manifest():
    """Read the pipeline manifest. Returns dict of script_path → status."""
    if MANIFEST_PATH.exists():
        import json as json_mod
        return json_mod.loads(MANIFEST_PATH.read_text())
    return {}


def write_manifest(manifest):
    """Write the pipeline manifest."""
    import json as json_mod
    MANIFEST_PATH.write_text(json_mod.dumps(manifest, indent=2) + "\n")


def get_script_tier(script_path):
    """Get the tier for a script from the manifest. Default: review."""
    manifest = read_manifest()
    return manifest.get(script_path, "review")


class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global ROOT
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)

        # Project switching via ?project=dirname
        if "project" in qs:
            proj_name = qs["project"][0]
            proj_dir = ROOT.parent / proj_name
            if not proj_dir.exists():
                proj_dir = Path.home() / "Documents" / proj_name
            if proj_dir.exists() and proj_dir.is_dir():
                ROOT = proj_dir
                os.chdir(ROOT)

        if parsed.path in ("/", "/dashboard"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            hypotheses = scan_hypotheses()
            insights = scan_insights()
            decisions = scan_decisions()
            pipeline = scan_pipeline()
            figures = scan_figures()
            code_files = scan_code_files()
            data_entries = scan_data()
            page = build_page(hypotheses, insights, decisions, pipeline, figures, code_files, data_entries)
            self.wfile.write(page.encode())
        elif parsed.path == "/api/code":
            qs = parse_qs(parsed.query)
            path = qs.get("path", [""])[0]
            fp = ROOT / path
            if fp.exists() and fp.is_file() and not ".." in path:
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(fp.read_bytes())
            else:
                self.send_error(404, f"Not found: {path}")
        elif parsed.path == "/api/git-log":
            # READ-ONLY commit list for the active project (newest first). Never writes.
            # Returns JSON [{hash, short, date, subject, reviewed}]; empty list if not a git repo.
            out = []
            if (ROOT / ".git").exists():
                led = ROOT / ".commit_reviews.json"
                try:
                    reviews = json_top.loads(led.read_text()) if led.exists() else {}
                except Exception:
                    reviews = {}
                try:
                    raw = subprocess.run(
                        ["git", "-C", str(ROOT), "log", "--no-color", "-n", "100",
                         "--pretty=format:%H%x1f%h%x1f%ad%x1f%cd%x1f%s", "--date=format:%Y-%m-%d %H:%M"],
                        capture_output=True, text=True, timeout=10).stdout
                    for ln in raw.splitlines():
                        parts = ln.split("\x1f")
                        if len(parts) == 5:
                            rv = reviews.get(parts[0])
                            out.append({"hash": parts[0], "short": parts[1],
                                        "date": parts[2], "adate": parts[2], "cdate": parts[3],
                                        "subject": parts[4], "reviewed": bool(rv),
                                        "reviewed_at": (rv or {}).get("at", "")})
                except Exception:
                    pass
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json_top.dumps(out).encode())
        elif parsed.path == "/api/git-diff":
            # READ-ONLY diff for one commit (its change vs its parent). Never writes.
            # ?hash=<full sha>. Validates the hash is hex to avoid arg injection.
            h = qs.get("hash", [""])[0]
            body = ""
            if (ROOT / ".git").exists() and re.fullmatch(r"[0-9a-fA-F]{7,40}", h or ""):
                try:
                    body = subprocess.run(
                        ["git", "-C", str(ROOT), "show", "--no-color", "--stat", "--patch", h],
                        capture_output=True, text=True, timeout=10).stdout
                except Exception:
                    body = "(diff unavailable)"
            else:
                body = "(no git repo, or invalid commit id)"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(body.encode())
        elif parsed.path == "/reorient":
            # Serve the reorient deck (the /amnesia output). Disposable HTML
            # generated from STATE.md + most recent progress log; falls through
            # to a placeholder if the file doesn't exist yet.
            reorient_html = ROOT / "reorient" / "index.html"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
            self.end_headers()
            if reorient_html.exists():
                self.wfile.write(reorient_html.read_bytes())
            else:
                placeholder = (
                    "<!DOCTYPE html><html><head><meta charset='utf-8'>"
                    "<title>Reorient — not yet generated</title>"
                    "<style>body{font-family:Inter,sans-serif;padding:3rem;max-width:48rem;"
                    "margin:0 auto;color:#1A202C;line-height:1.6}"
                    "code{background:#F1F5F9;padding:0.15rem 0.45rem;border-radius:3px;"
                    "font-family:'SF Mono',monospace;font-size:0.9em}"
                    "h1{color:#0B2545}</style></head><body>"
                    "<h1>Reorient deck not yet generated</h1>"
                    "<p>The reorient deck is built on demand. In a Claude Code session in this "
                    "project, ask: <em>get me up to speed</em>, or invoke <code>/amnesia</code>.</p>"
                    "<p>The skill reads <code>STATE.md</code> plus the most recent file in "
                    "<code>audits/</code> and writes a short HTML deck to "
                    "<code>reorient/index.html</code>, which this URL serves.</p>"
                    "</body></html>"
                )
                self.wfile.write(placeholder.encode())
        else:
            # Static files — disable caching so updated figures always show
            self.send_response(200)
            path = parsed.path.lstrip("/")
            fp = ROOT / path
            if fp.exists() and fp.is_file():
                if fp.suffix == ".png":
                    self.send_header("Content-Type", "image/png")
                elif fp.suffix == ".pdf":
                    self.send_header("Content-Type", "application/pdf")
                elif fp.suffix == ".csv":
                    self.send_header("Content-Type", "text/csv")
                elif fp.suffix in (".html", ".htm"):
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                elif fp.suffix == ".js":
                    self.send_header("Content-Type", "application/javascript; charset=utf-8")
                elif fp.suffix == ".css":
                    self.send_header("Content-Type", "text/css; charset=utf-8")
                elif fp.suffix in (".jpg", ".jpeg"):
                    self.send_header("Content-Type", "image/jpeg")
                elif fp.suffix == ".svg":
                    self.send_header("Content-Type", "image/svg+xml")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
                self.send_header("Pragma", "no-cache")
                self.send_header("Expires", "0")
                self.end_headers()
                self.wfile.write(fp.read_bytes())
            else:
                self.send_error(404, f"Not found: {path}")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/order":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            import json as json_mod
            order_file = ROOT / "FIGURE_ORDER.json"
            order_file.write_text(body)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"ok":true}')
            return
        elif parsed.path == "/api/tier":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode()
            import json as json_mod
            data = json_mod.loads(body)
            script = data.get("script", "")
            tier = data.get("tier", "review")
            if script and tier in ("approved", "review", "sandbox"):
                manifest = read_manifest()
                manifest[script] = tier
                write_manifest(manifest)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json_mod.dumps({"ok": True, "script": script, "tier": tier}).encode())
            else:
                self.send_error(400, "Bad request")
        elif parsed.path == "/api/pin-figure":
            # Pin a figure into a checklist stage by APPENDING its path to that stage's exhibits.md
            # (exhibits.md stays the source of truth — canon-closure gate). Returns whether the figure's
            # producing script is wired into run_pipeline.sh so the UI can badge unwired pins (warn-but-
            # allow). Idempotent: skips if the figure path is already in the file.
            length = int(self.headers.get("Content-Length", 0))
            import json as json_mod
            data = json_mod.loads(self.rfile.read(length).decode() or "{}")
            slug = data.get("slug", "")
            stage = data.get("stage", "")
            fig_path = data.get("path", "")          # e.g. output/figures/foo.png
            fig_name = data.get("name", "")
            script = data.get("script", "") or ""
            st_dir = ROOT / "analyses" / slug / "stages" / stage
            # guard: no traversal, stage must exist
            if (".." in slug or ".." in stage or ".." in fig_path or not st_dir.is_dir()
                    or not fig_path or slug.startswith("_")):
                self.send_error(400, "Bad request"); return
            ex = st_dir / "exhibits.md"
            existing = ex.read_text() if ex.exists() else "# exhibits\n"
            already = fig_path in existing
            wired = _script_is_wired(script)
            if not already:
                src_note = f" — src: {script}" if script else " — src: (UNWIRED — provenance not proven)"
                line = f"- `{fig_path}`{src_note} — pinned via dashboard {datetime.now().strftime('%Y-%m-%d')}\n"
                if not existing.endswith("\n"):
                    existing += "\n"
                ex.write_text(existing + line)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json_mod.dumps({
                "ok": True, "slug": slug, "stage": stage, "name": fig_name,
                "wired": wired, "already": already,
            }).encode())
        elif parsed.path == "/api/git-review":
            # Record (or clear) the human sign-off on a commit. This is a REVIEW LEDGER,
            # not a git operation — writes .commit_reviews.json in the project root. Git is untouched.
            length = int(self.headers.get("Content-Length", 0))
            import json as json_mod, datetime as _dt
            data = json_mod.loads(self.rfile.read(length).decode() or "{}")
            h = data.get("hash", "")
            reviewed = bool(data.get("reviewed", True))
            if (ROOT / ".git").exists() and re.fullmatch(r"[0-9a-fA-F]{7,40}", h or ""):
                led = ROOT / ".commit_reviews.json"
                try:
                    rec = json_mod.loads(led.read_text()) if led.exists() else {}
                except Exception:
                    rec = {}
                if reviewed:
                    rec[h] = {"by": "reviewer", "at": _dt.datetime.now().strftime("%Y-%m-%d %H:%M")}
                else:
                    rec.pop(h, None)
                led.write_text(json_mod.dumps(rec, indent=2))
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json_mod.dumps({"ok": True, "hash": h, "reviewed": reviewed}).encode())
            else:
                self.send_error(400, "Bad request")
        else:
            self.send_error(404)

    def log_message(self, format, *args):
        pass


class ThreadingDashboardServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    # Multi-threaded so one slow request (a big diff, a git log) doesn't block the rest of the
    # dashboard.
    # daemon_threads so Ctrl+C exits cleanly.
    daemon_threads = True


if __name__ == "__main__":
    os.chdir(ROOT)
    # Bind to loopback ONLY (127.0.0.1), not all interfaces. The dashboard reads the whole project
    # and writes to it (review ledger, figure order), with no authentication of any kind — a
    # network-reachable bind would hand all of that to anyone on the same network. Loopback means
    # the only client is the local browser.
    server = ThreadingDashboardServer(("127.0.0.1", PORT), DashboardHandler)
    print(f"Dashboard live at http://localhost:{PORT}/")
    print(f"Reading from: {ROOT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
