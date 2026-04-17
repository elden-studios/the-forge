# The Forge — Progress & Roadmap

## Current Status: v3.2 Wave 2 SHIPPED — Cabinet mechanics live on main

**GitHub:** https://github.com/elden-studios/the-forge
**Last release:** 2026-04-17 (v3.2 Cabinet Wave 2 — Mechanics)
**Previous releases:** Wave 1 (2026-04-17), v3.1 Evidence Pipes (2026-04-17 `7c02d85`)
**Tests:** 235/235 green
**Changelog:** see [`CHANGELOG.md`](CHANGELOG.md)

**What's next:** Wave 3 (Visual) — Executive Suite pixel office room + Dashboard Cabinet block + Decisions tab + Pre-Mortem heatmap widget + live end-to-end run. See v3.2 Wave 3 section below.

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

## v3.2 — Cabinet expansion (in flight)

### Wave 1 — Roster & Protocol (SHIPPED 2026-04-17) ✅

Two-tier org: **15 agents across 9 departments**, 5 C-Suite + 10 ICs. Six new agents (Cade/Helix/Prism/Dune/Lex/Zeta) each with named practitioner playbooks (Cagan/Fournier/Tunguz/Dunford/pragmatic-legal/Stancil). Three new departments (Product/Legal/Finance). Protocol v3.1 → v3.2 with Phase 1.5 Cabinet Framing, two-floor Phase 3 War Room, new Phase 7 deliverable format, Standing Rules 10–11. Validator enforces role + reports_to + cabinet.executives with defensive type guards and self-reference detection.

**165 tests green** (151 Evidence Pipes baseline + 14 new v3.2 tests). Full Foundation Code Review Gate passed with 0 Criticals, 3 Importants addressed, minor cleanups landed. 10 rivalries across 2 scales, all mirror-documented in both participants' brain files. Flint uplifted from flat-team strategist to CSO with Rumelt's Strategy Kernel as signature artifact.

Backward compat preserved — v3.1 Evidence Pipes tests all green, kill switch via `cabinet.executives: []` restores v3.1 behavior byte-for-byte.

See [`CHANGELOG.md`](CHANGELOG.md) for the full v3.2 Wave 1 entry and `docs/superpowers/plans/2026-04-17-v3.2-cabinet-wave1-roster.md` for the implementation log.

### Wave 2 — Cabinet Mechanics (SHIPPED 2026-04-17) ✅

Decision Log lifecycle + Pre-Mortem + Cabinet Framing schema validation + operator-level SKILL.md mechanics + reproducible Cabinet Framing driver. Standing Rule 11 auto-enforced.

- `tools/decisions_orchestrator.py` — Decision Log module (lifecycle ops, atomic write, assets mirror; timezone-correct compute_review_at after review-response fix)
- `tools/validator.py` — `validate_decisions()` + auto-load of `forge-decisions.json` + Standing Rule 11 cross-check (cabinet_framing → ≥1 decision) + `validate_tasks()` schemas for `cabinet_framing` (5 canonical lenses) and `pre_mortem` (likelihood × impact, owner, mitigation_phase enum)
- `forge-decisions.json` + `assets/forge-decisions.json` mirror initialized
- Canonical kill switch: `cabinet.enabled: false` (Wave 1 `cabinet.executives: []` still accepted as alias)
- `scripts/cabinet_framing_simulate.py` — reproducible driver with canned Saudi PropTech inputs (matches Evidence Pipes' `run_pipeline.py` pattern)
- SKILL.md — Phase 1.5 lens-production rules (per-exec formats), Phase 3 two-floor War Room mechanics + escalation ladder + Type 1/2 guidance + code example, Phase 7 deliverable format with Cabinet Verdict + 5 signature artifacts + Decision Log section

**235 tests green** (+70 new: 26 orchestrator + 12 validate_decisions + 4 validate_project auto-load + 8 pre_mortem + 6 cabinet_framing + 3 kill-switch + 4 rule 11 + 7 review-response).

See `docs/superpowers/plans/2026-04-17-v3.2-cabinet-wave2-mechanics.md`.

### Wave 3 — Visual (queued)

- Pixel office Executive Suite boardroom (new top-right room with 5-chair conference table)
- Legal, Finance, Product pixel dept rooms
- Cabinet block on Mission Control tab (verdict / artifacts / pre-mortem risks)
- Decisions tab (tab 6) with filter by project/reversibility/status/decider, sort by review_at, export MD/CSV/JSON
- Pre-Mortem 5×5 heatmap widget
- C-Suite walk-to-boardroom animation (Cabinet-dispatched / Cabinet-arrived events)
- Live end-to-end run — project brief through full v3.2 flow (Task 14-style), documented in `docs/superpowers/runs/`

### After v3.2 — queued sub-projects per roadmap

Full roadmap at `docs/superpowers/specs/2026-04-17-v3.2-expansion-roadmap.md`.

- **Sub-project A** — Hierarchy tree visualization (unblocked after W3 — data model is ready)
- **Sub-project C** — Subagent delegation (biggest architectural change; two-tier structure from W1-W3 is prerequisite)
- **Sub-project D** — Context system / project-level memory (Decision Log from W2 seeds this)
- **Sub-project E** — Tools & platforms catalog (independent, can ship parallel to any wave)

### Post-v3.2 — deferred from earlier roadmap

- **Chrome MCP pipes** (phase 2 of Evidence Pipes) — per-agent pipe selection, Echo → app-store interaction, Talon → landing page teardowns, Nyx → authenticated SAMA docs
- **Memory & Calibration** (originally A+D in v4.0 roadmap) — now partially absorbed into sub-project D; prediction → outcome tracking with Brier scores remains future work
- **Domain templates** — The Bar (legal strategy), The Clinic (medical product), The Lab (academic research)
- **Semantic conflict detection** — LLM-based non-numeric contradiction detection (current conflict detector is rule-based numeric-divergence only)
- **Dashboard polish** — Network Graph / Kanban / Timeline tabs enriched with Evidence+Cabinet data; agent-performance over-time mini-dashboard; project-replay mode

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
# Run full Python test suite (235 tests — 151 Evidence Pipes + 14 v3.2 W1 + 70 v3.2 W2)
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
