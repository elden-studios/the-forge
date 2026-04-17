"""Cabinet Framing simulation driver.

Takes canned 5-lens input + pre-mortem items from scripts/sample_inputs/
and produces valid forge-tasks (cabinet_framing + pre_mortem) plus a
sample Cabinet Verdict entry in forge-decisions.json. Runs the full
validator end-to-end.

Mirrors docs/superpowers/runs/2026-04-17-neobank-brief/run_pipeline.py
from Evidence Pipes v1 — a reproducible integration exercise over
the shipped pure-function modules.

Usage:
    python3 scripts/cabinet_framing_simulate.py

Writes to:
    forge-tasks.json (cabinet_framing + pre_mortem blocks)
    forge-decisions.json (sample Cabinet Verdict decision)

This simulation does NOT make LLM calls — the 5-lens content is canned
input. Real Cabinet Framing will be driven by SKILL.md protocol during
live project briefs (Wave 3 live run).
"""
import json
import os
import sys
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SAMPLE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sample_inputs")

sys.path.insert(0, os.path.join(REPO, "tools"))

from decisions_orchestrator import (  # noqa: E402
    new_decision_id,
    compute_review_at,
    append_decision,
)
from validator import validate_project  # noqa: E402


def load_sample_inputs():
    with open(os.path.join(SAMPLE_DIR, "cabinet_lenses.json")) as f:
        lenses_input = json.load(f)
    with open(os.path.join(SAMPLE_DIR, "pre_mortem_items.json")) as f:
        pre_mortem_input = json.load(f)
    return lenses_input, pre_mortem_input


def write_forge_tasks(lenses_input, pre_mortem_input, forge_tasks_path):
    """Write cabinet_framing + pre_mortem blocks onto forge-tasks.json."""
    if os.path.isfile(forge_tasks_path):
        with open(forge_tasks_path) as f:
            tasks = json.load(f)
    else:
        tasks = {"tasks": [], "handoffs": [], "current_phase": 0}

    tasks["cabinet_framing"] = {
        "framing_brief": lenses_input["framing_brief"],
        "lenses": lenses_input["lenses"],
    }
    tasks["pre_mortem"] = pre_mortem_input
    tasks["current_phase"] = 1

    with open(forge_tasks_path, "w") as f:
        json.dump(tasks, f, indent=2)


def create_cabinet_verdict_decision(project_id, project_title, forge_decisions_path):
    """Create and persist a sample GO decision for the simulated Cabinet Verdict."""
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    decision = {
        "id": new_decision_id(),
        "title": f"GO at 75% confidence — {project_title}",
        "context": (
            "Phase 1.5 Cabinet Framing produced a clean 5-lens diagnosis with "
            "5 pre-mortem risks (top: Bayut counter-move F=16, Nafath rate "
            "limits F=16). Cabinet reached majority GO; Prism dissented on "
            "unit-econ below SAR 500K."
        ),
        "alternatives_considered": [
            "NO-GO (reject: market window closing)",
            "ITERATE with Bahrain pilot first (reject: loses Saudi-first positioning)",
            "GO with Riyadh-only pilot (selected — this decision)",
        ],
        "decided_by": "agent-cade",
        "dissenting": ["agent-prsm"],
        "dissent_reason": "Unit economics break below SAR 500K properties",
        "decided_at": now_iso,
        "reversibility": "type_1",
        "review_at": compute_review_at(now_iso, "type_1"),
        "project_id": project_id,
        "related_evidence": [],
        "status": "open",
    }
    append_decision(project_id, decision, forge_decisions_path)
    return decision


def main():
    lenses_input, pre_mortem_input = load_sample_inputs()
    project_id = lenses_input["project_id"]
    project_title = lenses_input["project_title"]

    forge_tasks_path = os.path.join(REPO, "forge-tasks.json")
    forge_decisions_path = os.path.join(REPO, "forge-decisions.json")

    print(f"Simulating Cabinet Framing for: {project_title}")
    print(f"  project_id: {project_id}")
    print()

    print("→ Writing cabinet_framing + pre_mortem to forge-tasks.json")
    write_forge_tasks(lenses_input, pre_mortem_input, forge_tasks_path)
    print(f"  forge-tasks.json: 5 lenses written, {len(pre_mortem_input)} pre-mortem items")
    print()

    print("→ Creating sample Cabinet Verdict decision")
    decision = create_cabinet_verdict_decision(project_id, project_title, forge_decisions_path)
    print(f"  decision id: {decision['id']}")
    print(f"  reversibility: {decision['reversibility']} (review_at {decision['review_at']})")
    print()

    print("→ Validating project...")
    ok, errors = validate_project(REPO)
    if ok:
        print("  ✅ OK — validator passed all checks")
    else:
        print("  ❌ FAIL — validation errors:")
        for i, e in enumerate(errors, 1):
            print(f"    {i}. {e}")
        sys.exit(1)

    print()
    print("Simulation complete.")
    print(f"  • forge-tasks.json now has cabinet_framing + pre_mortem blocks")
    print(f"  • forge-decisions.json now has 1 decision (status=open)")
    print(f"  • Mirror written to assets/forge-decisions.json")
    print(f"  • All {len(pre_mortem_input)} pre-mortem risks have owners + mitigation phases")


if __name__ == "__main__":
    main()
