# The Forge — Progress & Resume Guide

## Current Status: Evidence Pipes v1 in flight — 5/16 tasks complete

**GitHub:** https://github.com/elden-studios/the-forge
**Active branch:** `evidence-pipes-v1` (LOCAL ONLY — not yet pushed)
**Last session:** 2026-04-16

---

## Ship log before Evidence Pipes v1

### Core system (v3.0 — shipped, live on main)
- SKILL.md orchestration brain
- Collaboration Protocol v3.0 — 8 phases, 15 elite enhancements
- 9 Agent Second Brain files (hot takes, frameworks, rivalries, mentorship)
- Agent Design Guide

### Team: 9 agents, 6 departments
| Agent | Title | Department |
|-------|-------|------------|
| Flint | Chief Ideation Architect | Strategy |
| Vex | Market Intelligence Lead | Research |
| Nyx | Saudi Market Strategist | Research |
| Echo | User Research Lead | Research |
| Ren | UX Alchemist | Design |
| Sable | Brand Alchemist | Design |
| Talon | Growth Architect | Growth |
| Atlas | Technical Architect | Engineering |
| Kira | Content Architect | Content |

### Office + Dashboard + Validator + Plugin (shipped to main)
- Pixel office with chibi sprites, door routing, event animations (`assets/office-template.html`)
- 4-tab real-time dashboard (Mission Control, Network Graph, Kanban, Timeline) — `assets/dashboard.html`
- State validator, 26 tests, `tools/validator.py`
- Plugin packaged, installable via `npx skills add elden-studios/the-forge@the-forge -g`

### Completed projects
| # | Project | Decision | Confidence |
|---|---------|----------|------------|
| 1 | Digital Signature Platform | GO | 75% |
| 2 | Pet Healthcare Platform (Saudi) | GO | 80% |

---

## 🔥 IN FLIGHT — Evidence Pipes v1

**Spec:** `docs/superpowers/specs/2026-04-16-evidence-pipes-v1-design.md`
**Plan:** `docs/superpowers/plans/2026-04-16-evidence-pipes-v1.md`
**Branch:** `evidence-pipes-v1` (local, 8 commits ahead of main, NOT PUSHED)
**Status:** 89 tests green. Pure-function foundation done. Ready for Task 6.

### What Evidence Pipes v1 does

Turns every `[FACT]` tag in agent output into a linkable, timestamped, quality-graded, cached, conflict-aware Evidence object. Moves The Forge from "ChatGPT with personality" to "board-room-defensible recommendations with an audit trail."

- 4 research agents (Vex, Nyx, Echo, Talon) fan out in parallel via `superpowers:dispatching-parallel-agents`
- Each runs real WebSearch (Chrome MCP phase 2) against a sub-brief
- Fan-in merges Evidence, dedupes by URL, detects numeric conflicts
- Persists to `forge-evidence.json`
- Deliverable ships with Sources Appendix (compact for terminal, full Markdown for export)
- `[FACT]` without Evidence ID gets stripped by the validator mechanically

### Tasks completed (5/16) — all TDD'd, both review gates passed inside each

| # | Task | Commit SHA | Tests added | Review findings addressed |
|---|------|------------|-------------|--------------------------|
| 1 | Evidence schema (dataclass, enums, ID gen) | `f24893d` → `18b3b86` | 5 | I2 (from_dict trust docstring), I3 (widen ID 6→8 hex), M3 (drop unused import) |
| 2 | Quality grading (regex rules + overrides) | `c6fc50d` → `7d05204` | 13 → 21 | C1 (anchor `ir.`/`reddit.` patterns), I3+I4 (harden load_overrides) |
| 3 | Freshness (per-tier stale/refetch bands) | `ac40d32` | 10 | (batched review with 4+5) |
| 4 | Cache (content-addressed + LRU) | `9e62753` | 9 | (batched review with 3+5) |
| 5 | Conflict detection (scope>tier>recency) | `b0e6517` → `4119d50` | 9 → 16 | C1 (atomic cache writes), C2 (fix number regex), I1 (deterministic clustering), I4 (graceful freshness errors) |

**Final test count at checkpoint: 89 green across 7 test files.**

### Modules shipped so far

```
tools/
├── evidence_schema.py      ✅ Evidence dataclass, SOURCE_TYPES, SIGNAL_TAGS, new_evidence_id()
├── evidence_quality.py     ✅ grade_url, load_overrides, merge_rules, DEFAULT_RULES
├── evidence_freshness.py   ✅ classify_freshness, FRESHNESS_RULES, days_between
├── evidence_cache.py       ✅ make_key, normalize_query, read/write_cache (atomic), evict_lru
├── evidence_conflict.py    ✅ cluster_by_keywords, extract_numbers, detect_conflicts, resolve
└── validator.py            (existing — Task 6 extends it)

tests/
├── test_evidence_schema.py       5 tests
├── test_evidence_quality.py      21 tests
├── test_evidence_freshness.py    12 tests
├── test_evidence_cache.py        11 tests
├── test_evidence_conflict.py     16 tests
├── test_validator.py             26 tests (existing)
└── (evidence-cache fixture dir, .gitkeep)

assets/.forge-cache/        ✅ created, gitignored except .gitkeep
.gitignore                  ✅ updated
```

---

## 🎯 NEXT SESSION: Resume at Task 6

**Exact starting point:** Plan file line ~540, Task 6 — "Extend validator — validate_evidence() + --cache-stats".

### What Task 6 does
- Extends `tools/validator.py` with `validate_evidence(evidence_doc, state)` covering all 11 rules in the spec
- Extends `validate_project()` to auto-load `forge-evidence.json` when present
- Adds `--cache-stats` CLI flag
- Initializes an empty `forge-evidence.json` at project root
- Ends with the **first 🛑 Code Review Gate** — dispatches `superpowers:requesting-code-review` against commits Task 1 through Task 6 (the full foundation)

### How to resume

1. Open Claude Code in `/Users/lbazerbashi/Elden Studios/the-forge`
2. Confirm you're still on branch `evidence-pipes-v1`: `git branch --show-current`
3. Say to Claude: **"Resume Evidence Pipes v1 implementation from Task 6 — see PLAN.md 'NEXT SESSION' section"**
4. Claude will use `superpowers:subagent-driven-development` ceremony (same as this session): dispatch implementer → spec review → code quality review → fix subagent
5. After Task 6 closes, there's a formal Code Review Gate on the whole foundation — plan says to invoke `superpowers:requesting-code-review`. Don't skip it.

### Remaining tasks after Task 6

| # | Task | Complexity |
|---|------|------------|
| 7 | Sub-brief generation + orchestrator skeleton (no real dispatch yet) | Medium |
| 8 | append_evidence + strip_unsupported_claims | Low |
| 9 | Sources Appendix renderer (compact + Markdown) | Low |
| 10 | SKILL.md + protocol v3.1 + evidence_pipes.enabled flag | Low-med |
| 11 | Dashboard Evidence block on Mission Control | Medium |
| 12 | Dashboard Sources tab (filter/search/export) | Medium |
| 13 | Pixel office dispatch animations | Low |
| 14 | **Synthetic end-to-end brief (Saudi expat neobank) + second Code Review Gate** | High |
| 15 | Address final review feedback (TDD) | Variable |
| 16 | Finish-branch ceremony (via `superpowers:finishing-a-development-branch`) | Low |

**Tasks 7-9 are good candidates for batching under one implementer** (pure functions + orchestration skeleton, all spec'd in the plan). Tasks 10-13 are docs + UI, different shapes — keep them serial. Task 14 is the big one and gets fresh attention.

### Discipline carried forward

- **TDD mandatory every task.** RED step first, then GREEN, verify no regression, commit with exact plan message.
- **Two-stage review every task.** Spec compliance first (haiku), then code quality (`superpowers:code-reviewer`).
- **Fix subagent after review** — same ceremony that's been working. Critical bugs found via review have averaged 2 per batch so far; expect similar.
- **Don't push to origin until Task 16.** Feature branch stays local until finish-branch ceremony.

### Office access (shipped during this session)

- Desktop launcher: `~/Desktop/Forge Office.command` — double-click, syncs state, opens in browser
- URL: http://localhost:8765/office-live.html (when server is running)

### Known follow-ups (non-blocking, noted during review)

- **Spec divergence:** plan/code use Jaccard threshold 0.4 for conflict clustering, but spec section 5 says "≥ 0.6". Either update the spec or document the rationale in `evidence_conflict.py` docstring. Not a bug, just a drift.
- **Crunchbase / LinkedIn** missing from default quality rules (flagged as M7 in Task 2 review). Can be added to rules or covered via user overrides JSON.
- **Cluster-of-3 determinism test** would strengthen Task 5. Current 2-item test is good but not exhaustive.

---

## Appendix — key commands

Run full test suite from repo root:
```bash
python3 -m unittest discover tests -v
```

Validate state/tasks/evidence files:
```bash
python3 tools/validator.py
```

See all commits on feature branch:
```bash
git log --oneline evidence-pipes-v1 ^main
```

Sync assets with latest state (if office looks stale):
```bash
cp forge-state.json forge-tasks.json assets/
```
