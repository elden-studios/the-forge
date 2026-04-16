# Evidence Pipes — Operator Protocol (v1)

This document is the in-skill reference for running Evidence Pipes during Phase 2 of the Collaboration Protocol. For the full design rationale see `docs/superpowers/specs/2026-04-16-evidence-pipes-v1-design.md`.

## When pipes fire

All of these must be true:
- `forge-state.json` → `evidence_pipes.enabled == true`
- User's brief touches market/research/growth/Saudi topics (check `evidence_orchestrator.score_agent_relevance` per agent)
- At least one evidence agent scores ≥ 2
- User didn't say "no evidence" / "skip pipes"

## The four evidence agents

| Agent | Domain | Data pipes |
|---|---|---|
| Vex | Market Intelligence | WebSearch (Chrome MCP phase 2) |
| Nyx | Saudi Market | WebSearch (Chrome MCP phase 2) |
| Echo | User Research | WebSearch now, Chrome MCP primary in phase 2 |
| Talon | Growth Architect | WebSearch (Chrome MCP phase 2) |

## Dispatch flow

1. Score → activate agents ≥ 2
2. For each active agent, generate sub-brief (`evidence_orchestrator.generate_sub_brief`)
3. Dispatch all sub-briefs in parallel via `superpowers:dispatching-parallel-agents`
4. Each subagent returns: `{ agent_id, evidence[], recommendation, confidence, queried_count, quality_avg, gaps[] }`
5. Fan-in: `evidence_orchestrator.merge_returns(returns)` (dedupe by source_url)
6. Persist: `evidence_orchestrator.append_evidence(project_id, bundle, "forge-evidence.json")`
7. Validate: `validator.validate_evidence(doc, state)` — re-prompt any subagent whose return fails
8. Conflicts: `evidence_conflict.detect_conflicts` → feed into War Room if any
9. Before final deliverable: `evidence_orchestrator.strip_unsupported_claims(text, valid_ids)` on every agent contribution
10. Render: `render_summary_block` above recommendation, `render_compact` as appendix (`render_markdown` on export)

## Evidence object shape (must match schema)

Every Evidence must have: `id` (ev-<8hex>), `claim`, `source_url`, `source_title`, `source_type` (one of 8 enum values), `quality_score` (1-5), `retrieved_at` (ISO 8601 UTC), `retrieved_by` (list of agent ids), `queried_via` (e.g. "WebSearch"), `excerpt` (15-40 word quote), `confidence` (0-1 float), `signal_tag` (FACT/INFERENCE/HYPOTHESIS/OPINION).

## Source quality tiers (see tools/evidence_quality.py)

| Tier | Examples | When to cite |
|---|---|---|
| 5 Primary government | MEWA, SAMA, MCIT | Regulatory or macro claims |
| 4 Primary company | 10-K, IR page, official pricing | Competitor product/financial claims |
| 3 Analyst/media | McKinsey, FT, Wamda | Market sizing, trends |
| 2 User/community | App Store reviews, Reddit, Product Hunt | UX signal, demand validation |
| 1 Blog / unknown | Medium, Substack | Only for directional hints, never anchor a claim |

## Failure modes

- Subagent timeout/error → `⚠ {Agent} unavailable` in deliverable; never fabricate
- Malformed Evidence return → re-prompt once, flag if second failure
- Saudi query with zero usable results → fall back to `[OPINION]` (never invent `[FACT]`)
- Budget exhausted (40+ queries) → stop, deliver with `⚠ Budget exhausted`

## Budgets

- 40 total queries per brief (soft); 60 hard cap
- 8 per agent
- 4 min wall-clock
- Chrome MCP phase 2: 5 concurrent tabs, 15 pages per brief

## Kill switch

Set `forge-state.json` → `evidence_pipes.enabled: false` → v3.0 sequential behavior restored, zero pipe cost.

User phrase overrides (one-shot): "no evidence", "skip pipes", "just use existing knowledge".
