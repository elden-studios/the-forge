"""Task 14 — fan-in pipeline driver for the Saudi expat neobank brief.

Loads 4 subagent returns, runs the shipped Evidence Pipes orchestrator
end-to-end, and emits the Deliverable Kit:
  - deliverable.md             — full Markdown including Sources Appendix
  - summary-block.txt          — Evidence Summary for terminal output
  - sources-compact.txt        — compact tier-grouped source list
  - conflicts.json             — detected conflicts (if any)
  - stats.json                 — run metrics

Run from repo root:
  python3 docs/superpowers/runs/2026-04-17-neobank-brief/run_pipeline.py
"""
import json
import os
import sys
import time

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
RUN_DIR = os.path.dirname(os.path.abspath(__file__))
RETURNS_DIR = os.path.join(RUN_DIR, "subagent-returns")

sys.path.insert(0, os.path.join(REPO, "tools"))

from evidence_orchestrator import merge_returns, append_evidence, strip_unsupported_claims  # noqa: E402
from evidence_conflict import detect_conflicts, resolve  # noqa: E402
from evidence_appendix import render_compact, render_markdown, render_summary_block  # noqa: E402
from validator import validate_evidence  # noqa: E402


PROJECT_ID = "proj-003"
BRIEF = (
    "Launch a mobile-first neobank targeting Saudi expats remitting to South Asia. "
    "Evaluate market, regulatory, user, and growth angles."
)


def main():
    t0 = time.time()

    # Step 1 — Load the 4 subagent returns
    returns = []
    for agent_file in ("vex.json", "nyx.json", "echo.json", "talon.json"):
        with open(os.path.join(RETURNS_DIR, agent_file)) as f:
            returns.append(json.load(f))
    print(f"Loaded {len(returns)} subagent returns.")

    # Step 2 — Fan-in merge
    bundle = merge_returns(returns)
    print(f"Merged: {len(bundle['evidence'])} unique Evidence (after dedup by source_url)")
    print(f"Agents: {bundle['agents']}")
    print(f"Total queries: {bundle['total_queries']}")
    print(f"Avg subagent-reported quality: {bundle['avg_quality']:.2f}")

    # Step 3 — Validate the merged evidence against current forge-state
    with open(os.path.join(REPO, "forge-state.json")) as f:
        state = json.load(f)
    evidence_doc = {
        "evidence": bundle["evidence"],
        "project_evidence_index": {PROJECT_ID: [e["id"] for e in bundle["evidence"]]},
    }
    ok, errors = validate_evidence(evidence_doc, state)
    if not ok:
        print(f"\n❌ VALIDATION FAILED — {len(errors)} errors")
        for e in errors[:10]:
            print(f"  - {e}")
        sys.exit(1)
    print(f"\n✅ Validation passed — {len(bundle['evidence'])} Evidence objects all well-formed")

    # Step 4 — Persist to forge-evidence.json (atomic + mirror to assets/)
    evidence_path = os.path.join(REPO, "forge-evidence.json")
    append_evidence(PROJECT_ID, bundle, evidence_path)
    print(f"Persisted to {evidence_path} (mirror in assets/)")

    # Step 5 — Conflict detection
    conflicts = detect_conflicts(bundle["evidence"])
    print(f"\nConflicts detected: {len(conflicts)}")
    resolved = []
    for conflict in conflicts:
        winner, rule = resolve(conflict, brief_scope="saudi")
        resolved.append({
            "evidence_ids": conflict["evidence_ids"],
            "divergence": conflict["divergence"],
            "winner_id": winner["id"],
            "resolution_rule": rule,
        })
        print(f"  • {conflict['evidence_ids']} divergence={conflict['divergence']:.1%} → winner {winner['id']} ({rule})")

    # Step 6 — Compute metrics
    elapsed = int(time.time() - t0)
    total_queries = bundle["total_queries"]
    cache_hits = 0  # No cache reuse in first run
    # Real-tier avg (from the actual quality_score fields on Evidence)
    qs = [e["quality_score"] for e in bundle["evidence"]]
    real_avg_quality = sum(qs) / len(qs)
    thin = sum(1 for e in bundle["evidence"] if e["quality_score"] == 1)
    # Per-agent metrics
    per_agent = {}
    for ret in returns:
        per_agent[ret["agent_id"]] = {
            "evidence_count": len(ret["evidence"]),
            "queried_count": ret["queried_count"],
            "confidence": ret["confidence"],
            "quality_avg": ret["quality_avg"],
            "gaps_count": len(ret.get("gaps", [])),
        }

    # Step 7 — Render the Sources Appendix
    summary = render_summary_block(
        bundle["evidence"],
        total_queries=total_queries,
        elapsed_sec=elapsed,
        cache_hits=cache_hits,
        conflicts=len(conflicts),
    )
    compact = render_compact(bundle["evidence"])
    md_appendix = render_markdown(bundle["evidence"])

    # Step 8 — Standing-rule enforcement sample: strip unsupported claims from each agent's recommendation
    valid_ids = {e["id"] for e in bundle["evidence"]}
    stripped_recs = {}
    for ret in returns:
        stripped_recs[ret["agent_id"]] = strip_unsupported_claims(ret["recommendation"], valid_ids)

    # Step 9 — Write outputs
    with open(os.path.join(RUN_DIR, "summary-block.txt"), "w") as f:
        f.write(summary)
    with open(os.path.join(RUN_DIR, "sources-compact.txt"), "w") as f:
        f.write(compact)
    with open(os.path.join(RUN_DIR, "conflicts.json"), "w") as f:
        json.dump(resolved, f, indent=2)
    with open(os.path.join(RUN_DIR, "stats.json"), "w") as f:
        json.dump({
            "brief": BRIEF,
            "project_id": PROJECT_ID,
            "elapsed_sec": elapsed,
            "total_queries": total_queries,
            "total_evidence_after_dedup": len(bundle["evidence"]),
            "total_evidence_before_dedup": sum(len(r["evidence"]) for r in returns),
            "cache_hits": cache_hits,
            "conflicts": len(conflicts),
            "avg_quality_real": real_avg_quality,
            "thin_evidence": thin,
            "per_agent": per_agent,
        }, f, indent=2)

    # Full Markdown deliverable
    deliverable = f"""# Final Deliverable — {PROJECT_ID}

## Brief

> {BRIEF}

## Evidence Summary

```
{summary}
```

## Agent Contributions

### Vex — Market Intelligence
{stripped_recs['agent-vexx']}

### Nyx — Saudi Market
{stripped_recs['agent-nyxx']}

### Echo — User Research
{stripped_recs['agent-echo']}

### Talon — Growth Architecture
{stripped_recs['agent-taln']}

## Conflicts Detected

"""
    if conflicts:
        for r in resolved:
            deliverable += f"- Evidence {r['evidence_ids']} diverged by {r['divergence']:.1%}. Resolved in favor of `{r['winner_id']}` via **{r['resolution_rule']}** rule.\n"
    else:
        deliverable += "_No numerically-divergent claims surfaced by the v1 rule-based detector._\n"

    deliverable += "\n" + md_appendix

    with open(os.path.join(RUN_DIR, "deliverable.md"), "w") as f:
        f.write(deliverable)

    print(f"\n{'=' * 60}")
    print(summary)
    print(f"{'=' * 60}")
    print(f"\nDeliverable: {os.path.join(RUN_DIR, 'deliverable.md')}")
    print(f"Elapsed: {elapsed}s | Real avg quality: {real_avg_quality:.2f} | Thin: {thin}")


if __name__ == "__main__":
    main()
