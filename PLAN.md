# The Forge — Progress & Roadmap

## Current Status: v3.1 SHIPPED — Evidence Pipes live on main

**GitHub:** https://github.com/elden-studios/the-forge
**Last release:** 2026-04-17 (v3.1 — Evidence Pipes v1)
**Merge commit:** `7c02d85`
**Tests:** 151/151 green
**Changelog:** see [`CHANGELOG.md`](CHANGELOG.md)

---

## What's shipped

### v3.1 — Evidence Pipes (2026-04-17)
Every `[FACT]` now linkable. Four research agents fan out to live WebSearch in parallel. Every deliverable ends with a Sources Appendix and EVIDENCE SUMMARY block. Source quality tier-graded 1–5. Numeric conflicts auto-detected. Kill-switchable.

- **Code:** 7 new stdlib-only Python modules under `tools/evidence_*.py` + extended `validator.py`
- **Tests:** 125 new tests (151 total, up from 26)
- **Protocol:** v3.0 → v3.1 with 3 new Standing Rules
- **UI:** Dashboard Evidence block on Mission Control + new Sources tab with filter/search/MD-CSV-JSON export
- **Office:** `dispatched` pulsing bubble + `evidence_arrived` green desk glow animations
- **Docs:** `references/evidence-pipes-spec.md` + SKILL.md Evidence Pipes section + full implementation spec/plan/run artifacts under `docs/superpowers/`
- **Real run:** `docs/superpowers/runs/2026-04-17-neobank-brief/` — 4 agents, 37 Evidence, 32 WebSearch queries, 0 numerical conflicts, all citations resolve

### v3.0 — Elite Protocol (2026-04-07)
9 agents across 6 departments. 8-phase collaboration protocol with 15 enhancements: Second Brain files, Quantify or Die, Red Team, Cross-Examination, Handoff Memos, Signal Tags, Rivalries, Mentorship Chains, Hot Takes, Project Memory, Deliverable Templates, more. Pixel art office with event-driven chibi sprite animations. State validator with 26 tests. 4-tab dashboard (Mission Control, Network, Kanban, Timeline). Plugin packaged for `npx skills add`.

**Projects delivered:**
| # | Project | Decision | Confidence |
|---|---------|----------|------------|
| 1 | Digital Signature Platform | GO | 75% |
| 2 | Pet Healthcare Platform (Saudi) | GO | 80% |
| 3 | Saudi Expat Neobank *(v3.1 validation run)* | Research | 82% avg |

---

## Team: 9 Agents, 6 Departments

| Agent | Title | Department | Evidence Pipe |
|-------|-------|------------|---|
| Flint | Chief Ideation Architect | Strategy | — (orchestrator) |
| Vex | Market Intelligence Lead | Research | ⚡ WebSearch |
| Nyx | Saudi Market Strategist | Research | ⚡ WebSearch (tier-5 SAMA/MCIT) |
| Echo | User Research Lead | Research | ⚡ WebSearch (App Store, Reddit) |
| Ren | UX Alchemist | Design | — |
| Sable | Brand Alchemist | Design | — |
| Talon | Growth Architect | Growth | ⚡ WebSearch (competitor pages) |
| Atlas | Technical Architect | Engineering | — |
| Kira | Content Architect | Content | — |

See [`TEAM.md`](TEAM.md) for full profiles.

---

## Next — possible v3.2 directions

The foundation + orchestration + real-run proof are done. From here:

### A. Chrome MCP pipes (phase 2 of Evidence Pipes)
Currently all 4 agents use WebSearch. Chrome MCP is scaffolded in the orchestrator but stubbed. Wiring it up unlocks:
- Echo → real app-store interaction (click through reviews, not just search snippets)
- Talon → competitor landing page teardowns with DOM-level access
- Nyx → authenticated SAMA documents via extension auth context
- Vex → deep Crunchbase / PitchBook / Similarweb crawls

Approach: per-agent pipe selection in `EVIDENCE_AGENTS` metadata; subagent prompts choose the right tool; fixtures for tests.

### B. Memory & Calibration (A+D from the v4.0 roadmap)
The sequel to Evidence Pipes, explicitly deferred from v3.1 scope.
- Track predictions → outcomes across project_history
- Brier scores per agent
- Post-mortem automation
- Agent weights in debates reflect track record ("the agent who's been right more gets more airtime")

### C. Roster expansion
The team keeps flagging the same gaps on new briefs: Pricing, Legal/Compliance, Data/Analytics, AI/ML specialist, Customer Success, Ops/Finance, Enterprise/Sales. v3.2 could hire 3–5 specialists. Each would benefit from the Evidence Pipes infrastructure already in place.

### D. Domain templates
Package the collaboration protocol for domains other than tech products:
- **The Bar** — legal strategy team (litigator, corporate, IP, compliance)
- **The Clinic** — medical product team (clinician, regulatory, bioethics, patient UX)
- **The Lab** — academic research (methodologist, statistician, literature reviewer, reviewer-2)

### E. Semantic conflict detection
Current `evidence_conflict.detect_conflicts` is rule-based (numeric divergence only). v2 could use LLM-based semantic conflict detection for non-numeric contradictions ("Vex says Saudi pay is card-first"; "Nyx says Saudi pay is Mada-first" — these disagree semantically, no numeric trigger).

### F. Dashboard polish
- Network Graph / Kanban / Timeline tabs still show v3.0 behavior — wire them up to show Evidence-augmented task state
- Agent performance mini-dashboard (quality_avg over time per agent)
- "Replay" a past project from saved forge-state snapshots

My read on priority (if pressed):
1. **B (Memory & Calibration)** — biggest compounding win, turns The Forge into a learning system, explicitly on the roadmap
2. **C (Roster expansion)** — lowest cost, visible "team keeps growing" story
3. **A (Chrome MCP)** — already scaffolded; slotting it in is follow-through
4. **E (Semantic conflict)** — high value, harder to evaluate correctness
5. **D (Domain templates)** — platformization; wait for more organic demand
6. **F (Dashboard polish)** — nice to have, not load-bearing

---

## Known non-blocking follow-ups from v3.1 reviews

- **Jaccard threshold drift** — plan/code use 0.4 for conflict clustering; spec section 5 originally said ≥ 0.6. Code won the argument; update the spec text.
- **Wall-clock instrumentation missing** on the run_pipeline driver (Elapsed: 0s is post-fan-in only). Low priority.
- **Subagent-reported `quality_avg` drifts slightly** from the orchestrator-computed real average. Orchestrator should trust the real `quality_score` field, not the subagent's self-reported summary.
- **UI tab-indicator cosmetic bug** — Mission Control underline briefly persists when switching to Sources tab. Panel swap works correctly; indicator update is cosmetic.
- **Crunchbase / LinkedIn** absent from default quality rules. Add to `DEFAULT_RULES` or cover via `evidence-quality-overrides.json`.
- **Cross-module integration test** covering one Evidence through schema → quality → freshness → cache → conflict → validator → persistence end-to-end. Unit tests are strong; no single test walks the full lifecycle.
- **`merge_returns` budget enforcement** (I3 from the second review gate) — currently accepts any return size. Soft caps + per-item schema check would harden against adversarial/malformed subagent returns.
- **`retrieved_by` attribution trust** (I4) — orchestrator currently accepts whatever `retrieved_by` the subagent returns. Should force it to `[ret["agent_id"]]`, merging additional agent IDs only via the dedup collapse path.

---

## Office access

- **Desktop launcher:** `~/Desktop/Forge Office.command` — double-click, syncs state, opens in browser
- **Office URL:** http://localhost:8765/office-live.html (when server is running)
- **Dashboard URL:** http://localhost:8765/dashboard.html (Mission Control + Sources tab)

## Key commands

```bash
# Run full Python test suite (151 tests)
python3 -m unittest discover tests -v

# Validate all state/tasks/evidence files
python3 tools/validator.py

# Check evidence cache stats
python3 tools/validator.py --cache-stats

# Start the preview server
python3 -m http.server 8765 -d assets

# Force-sync state files into assets/ if dashboard looks stale
cp forge-state.json forge-tasks.json forge-evidence.json assets/
```

## How to run Evidence Pipes on your own brief

Simplest: `claude` → "I have a brief: [your product]" → the team (with pipes enabled by default) will run the full 8-phase protocol, fanning out 4 WebSearch-enabled agents in Phase 2, and ending with a Sources Appendix you can click through.

Advanced: see `docs/superpowers/runs/2026-04-17-neobank-brief/run_pipeline.py` for a programmatic driver that reads subagent returns from disk.
