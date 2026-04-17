# Changelog

All notable changes to The Forge are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers track the collaboration protocol (`v3.x`), NOT the plugin's npm-style `package.json` version (which bumps with any user-visible change).

---

## [3.4.0] — 2026-04-17 — Sub-project E: Tools & Platforms Catalog

Second of the five v3.2 expansion sub-projects (shipping parallel to the others per the roadmap). Turns "list of SaaS we pay for" into a living inventory with teeth: per-agent assignments, usage status, shared-cost allocation, gap analysis, redundancy detection. New 8th dashboard tab. Independent of Sub-projects C / D — can ship in any order.

### Added
- `tools/platforms_catalog.py` — pure-function library: `load_catalog`, `validate_catalog` (enforces status enum, category_id integrity, non-negative numeric cost, list-typed agent fields), `gap_analysis(agent_id)`, `cost_breakdown` (total active / total dormant / by-category / by-agent with shared-cost split — tool cost ÷ num users allocated to each), `find_redundancies` (category_overlap for 2+ active tools in same category, confirmed listed_alternative when mutual alternatives are both active), `tools_by_agent(agent_id)` with `assigned` vs `recommended` tagging. `STATUSES = {active, dormant, unused}` frozen.
- `forge-platforms.json` + `assets/forge-platforms.json` mirror — 22 seed tools across 9 categories (Design, Research, Engineering, Growth, Content, Legal, Finance, Analytics, Saudi-specific). Realistic market prices (Figma $15, Notion $80, Ahrefs $99, SensorTower $349, HubSpot $20, Ironclad aspirational $500, etc.). Saudi-specific row includes Nafath / SAMA Sandbox / HyperPay-Mada. Seeded with intentional gaps (Echo recommended for Figma/Similarweb/Mixpanel; Lexx for Nafath/SAMA/Ironclad; Helix for Linear) and intentional redundancies (Similarweb↔Ahrefs, Mixpanel↔PostHog both listed alternatives).
- Dashboard "Tools" tab (tab 8) — 4-card summary row (Active Tools count, Monthly Spend, Dormant Waste warning-styled, Redundancies count) + three sections. Recommendations auto-generate kind-tagged entries (consolidate / dormant / gap) with red / yellow / purple left borders. By Category groups tools under colored category headers, each card showing status + redundancy badge + agent chips. By Agent renders one card per agent with department color strip, green assigned chips, red gap chips, allocated monthly spend.
- JS mirrors of all Python helpers — `getCostBreakdown`, `getGapAnalysis`, `getRedundancies`, `getToolsByAgent` — same Wave 3 mirror-discipline convention (divergence is a bug). Plus `fetchPlatforms()` that refreshes `forge-platforms.json` on the 3s tick.
- `docs/tools-catalog-audit-guide.md` — operator walkthrough: review the seed, edit to match real stack, mark dormant tools, run the dashboard, monthly / quarterly maintenance cadence, schema reference.
- `tests/test_subproject_e_integration.py` — validates the committed `forge-platforms.json` against the live `forge-state.json`: schema passes, ≥10 tools across ≥5 categories, ≥1 gap and ≥1 redundancy present, total active cost in [100, 10000]/mo, every agent id in `used_by_agents` / `recommended_for_agents` exists in state, assets mirror matches root.

### Changed
- `assets/dashboard.html` — tab button + panel + ~40 lines of new CSS for tools-summary-row / summary-card / tools-section / tool-card / tool-chip / recommendation-item; `switchTab` array extended to include `'tools'`; `render()` pipeline calls `renderToolsTab(_platformsDoc, STATE)` so the tab stays live. No touch to Wave 3 Cabinet, Decisions, Evidence, or Sub-project A Org Tree code paths.
- `tests/test_dashboard_org_tree.py::test_switchtab_array_includes_org_tree` — regex loosened from `…'org-tree'\]` to `…'org-tree'` (trailing entries accepted), same loosening the decisions test got in Sub-project A.

### Tests
- 406 → 470 (+64). Breakdown: 21 `test_platforms_catalog.py` (pure-helper unit tests — load, status enum, schema validation, gap semantics, cost breakdown active/dormant/by-category/shared-split, redundancy detection, agent tagging) + 34 `test_dashboard_tools_tab.py` (smoke: tab shell, CSS, summary row, section containers, JS mirrors defined, render templates) + 9 `test_subproject_e_integration.py` (integration against live state).

### Notes
- **No tool API integration in v1.** `status` is manually curated (`active` | `dormant` | `unused`). Automating "is this tool actually being used?" was explicitly out of scope — it rotted the v1 ship plan. The audit guide walks the operator through the monthly / quarterly cadence for keeping status honest.
- **Dashboard size.** After Sub-project E, `assets/dashboard.html` is ~1800 lines. A file split is queued for Wave 5 cleanup; not doing it inline here because Sub-projects C / D will reshape the dashboard further.

---

## [3.3.0] — 2026-04-17 — Sub-project A: Org Tree

First of the five v3.2 expansion sub-projects. Visualizes the two-tier v3.2 Cabinet hierarchy — built from the `reports_to` / `role` / `cabinet.executives` fields already on every agent — as a 7th dashboard tab. SVG-based (not Canvas), cleanly separated from the pixel office, DOM-queryable, scalable.

### Added
- `tools/org_tree.py` — pure `get_org_tree(state)` helper returning `{root, orphans, rivalry_edges}`. Root chosen from agents with no `reports_to`; tiebreak via `cabinet.executives[0]`. Rivalry edges are mutual-only, deduped, scale-tagged (`cabinet` when both sides are execs, else `ic`). Orphans (agents whose `reports_to` points at a missing id) surface rather than silently drop.
- Dashboard "Org Tree" tab (tab 7) with SVG-rendered 3-tier org chart. Parent-centered layered layout so a wide fan-out (Cade's 6 ICs) doesn't overlap; rounded node cards with a 4px department color strip on top; cubic-Bezier connectors for Reports-to; dashed-red peer lines for Rivalry (same-tier pairs only — cross-tier is elided to keep the chart legible).
- `getOrgTree(state)` JS mirror of the Python helper (Wave 3 mirror-discipline convention — divergence is a bug), plus `layoutTree` / `bezierPath` renderers and a legend row (Root / C-Suite / IC / Reports to / Rivalry).
- `tests/test_subproject_a_org_tree.py` — integration test validating the tree against the live committed `forge-state.json`: root is `agent-flnt`, tier-1 is exactly {cade, helx, prsm, dune, lexx} (4 reporting execs + Legal IC reporting directly to CSO), 15 total nodes, 0 orphans.

### Changed
- `assets/dashboard.html` — tab button + panel + CSS + SVG renderer; `switchTab` array extended to include `'org-tree'`; `render()` pipeline calls `renderOrgTree(STATE)` so the tree stays in sync with every state refresh. No touch to Wave 3 Cabinet or Decisions code paths.
- `tests/test_dashboard_decisions_tab.py::test_switchtab_array_includes_decisions` — regex loosened from `…'decisions'\]` to `…'decisions'` to permit trailing entries (the array is open-ended as new tabs ship).

### Tests
- 363 → 406 (+43). Breakdown: 17 `test_org_tree.py` (pure-helper unit tests — empty state, single agent, multi-root tiebreak, live shape, orphans, rivalry semantics) + 22 `test_dashboard_org_tree.py` (smoke: tab shell, CSS, legend, layout contract, SVG emission, rivalry class) + 4 `test_subproject_a_org_tree.py` (integration).

### Notes
- **Rivalries are empty in current state.** The `rivalries` field exists on every agent but is unpopulated; the renderer handles that path (no rivalry lines, no crash). A future task can populate rivalries per the v3.2 spec and the dashed-red peer lines will start rendering without further code changes.
- **SVG, not Canvas.** Intentional split from the pixel office. SVG gives hover-ready DOM, clean scaling, and simpler test assertions.

---

## [3.2.0-wave4] — 2026-04-17 — Cleanup

Consolidation commit addressing deferred Foundation review items from Wave 3. No new features — signature harmonization, helper consolidation, import hygiene, integration-coverage gap closed.

### Changed
- `append_decision_persist` signature harmonized to `(path, decision)` — matches `close_decision_persist(path, ...)` / `reverse_decision_persist(path, ...)`. Breaking for out-of-tree callers (in-tree driver + 5 test call sites updated). The `project_id` arg was redundant (already in `decision.project_id`); Wave 3's forced normalization block removed. `KeyError` raised when `decision["project_id"]` missing (surfaces misuse cleanly). Historical shape was `append_decision(project_id, decision, path)` in Wave 2, renamed to `append_decision_persist(project_id, decision, path)` in Wave 3, and harmonized to `(path, decision)` here.
- Merged `getAgentName(id)` into canonical `agentName(stateDoc, id)` in `assets/dashboard.html` — 5 call sites migrated from implicit-global lookup to explicit stateDoc arg (more testable, no hidden dep).
- Lifted `from datetime import timezone` to module top of `tools/decisions_orchestrator.py` — two inline re-imports inside function bodies removed.

### Added
- `tests/test_v32_wave3_integration.py` — walks pre_mortem → heatmap → Decision Log end-to-end via the Saudi EdTech fixture (7 tests). Closes M3 integration-coverage gap from Wave 3 Foundation review.

### Tests
- 356 → 363 (+7 integration tests).

---

## [3.2.0-wave3] — 2026-04-17 — Cabinet Visualization

### Added — v3.2 Cabinet Wave 3 (Visualization)

The visual surface of the v3.2 Cabinet. Pixel office grows to a 3×3 department grid with a new top-right Executive Suite boardroom; Mission Control gets a Cabinet block + Pre-Mortem heatmap widget; a new Decisions tab exposes the full Decision Log with filter / sort / export. Library Task 0 closes the three deferred Wave 2 Important items (upsert semantics, persistence wrappers, query helpers). Foundation Code Review Gate passed. First live end-to-end simulation run shipped (Saudi EdTech brief).

**Library Task 0** (`tools/decisions_orchestrator.py`)
- Pure `append_decision(doc, decision)` with **upsert semantics** — existing id updates in place; absent id appends. Previously, re-running the driver silently skipped duplicate ids, making replayable Cabinet Framing simulations surprising.
- Persistence wrappers — `close_decision_persist(path, id, new_status)` and `reverse_decision_persist(path, id, successor_id)` — atomic write + assets mirror, so dashboard-side buttons can write decisions without reimplementing the persistence dance.
- Query helpers — `query_by_project(doc, project_id)`, `query_by_status(doc, status)`, `query_due_soon(doc, now_iso, horizon_days)`, `query_sorted_by_review_at(doc)` — pure, composable, used by the Decisions tab rendering pipeline.
- `heatmap_buckets(pre_mortem)` — 5×5 aggregation (likelihood 1..5 × impact 1..5), returns 2D array of counts. Used by the Pre-Mortem heatmap widget.

**Pixel office layer** (`office-template.html`)
- Dept grid expanded 3×2 → 3×3 to accommodate new Product / Legal / Finance rooms (Wave 1 departments now have visible real estate).
- **Executive Suite boardroom** — new top-right room with conference table sprite + 5 chair sprites (one per C-Suite exec: Flint / Cade / Helix / Prism / Dune). Canvas grows 700×504 → 960×928 to fit.
- Canvas height math now computes from `ROW2_Y + ROOM_H + WALL + BREAK_H + MARGIN` (previously hardcoded).
- New animation events — `cabinet_dispatched` (exec walks from dept room to boardroom), `cabinet_arrived` (exec sprite arrives in boardroom), `routeCabinet(execId)` helper function, `cabinet_seated` sprite state when exec is at table.

**Mission Control Cabinet block** (`dashboard.html` + `dashboard-cabinet.js`)
- Verdict card — GO/NO-GO/NEEDS-WORK + confidence % + decider + Type 1/2 reversibility badge.
- 5 lens cards — strategic_kernel / product_shape / build_class / economic_shape / market_bet, one per canonical Cabinet Framing lens.
- Top 3 pre-mortem risks — sorted by likelihood × impact product, owner agent visible.
- 5×5 heatmap widget — likelihood × impact grid with cell-count gradient; hover shows which pre-mortem items fall in each bucket.

**Decisions tab (tab 6)** (`dashboard.html` + `dashboard-decisions.js`)
- Filters — project (dropdown), reversibility (Type 1 / Type 2 / all), status (open / reviewed / committed / reversed), decider (agent), free-text search across title + rationale.
- Sort — by review_at (toggleable ascending / descending), default descending so newest-due-first.
- Exports — Markdown, CSV, JSON. MD export writes a Decision Log section formatted like the Phase 7 deliverable template.

**Saudi EdTech live simulation run** — `docs/superpowers/runs/2026-04-17-saudi-edtech-brief/`
- First live end-to-end v3.2 simulation: project brief → Cabinet Framing driver → 5 lens artifacts + 5 pre-mortem items → Decision Log entry → validator OK → dashboard renders populated blocks.
- Documents run metrics, raw inputs, artifacts, honest post-run notes. Mirrors the Evidence Pipes v3.1 neobank-brief run structure.

**Tests** — +121 new across 4 new test files
- `test_decisions_orchestrator_wave3.py` — upsert, persistence wrappers, query helpers, heatmap_buckets
- `test_office_template_layout.py` — 3×3 grid geometry, boardroom placement, chair positions, canvas height math
- `test_dashboard_cabinet_block.py` — verdict/lens card data shaping, top-3 risk ordering, heatmap_buckets rendering
- `test_dashboard_decisions_tab.py` — filter composition, sort toggle, export MD/CSV/JSON output shape
- 356 tests total (235 Wave 2 baseline + 121 new)
- Backward compat preserved — all Wave 1 + Wave 2 + v3.1 Evidence Pipes tests still green.

### Changed

- `append_decision` name now refers to the **pure function** (`(doc, decision)` signature). The previous I/O-wrapping callable moved to `append_decision_persist(project_id, decision, path)`. Breaking for out-of-tree callers; all in-tree callers updated in the same commit.
- `SKILL.md` updated to reference `append_decision_persist` in 3 locations (Phase 3 code example, Phase 7 assembly pseudocode, Cabinet mechanics section).
- Office canvas grows 700×504 → 960×928 (3×3 grid + boardroom).
- Canvas height now derived from layout constants (`ROW2_Y + ROOM_H + WALL + BREAK_H + MARGIN`) instead of hardcoded.

### Fixed

**Deferred Wave 2 Important items (now closed in Wave 3 T0 library)**
- Wave 2 review I2: `append_decision` upsert semantics — shipped in T0.1. Previously silently skipped duplicate ids.
- Wave 2 review I1: Persistence wrappers (`close_decision_persist`, `reverse_decision_persist`) — shipped in T0.2. Dashboard-side writes no longer need to reimplement atomic write + mirror.
- Wave 2 review I4: Query helpers (`query_by_project` / `query_by_status` / `query_due_soon` / `query_sorted_by_review_at`) — shipped in T0.3. Decisions tab filter/sort rendering now uses these directly.

**Foundation Code Review Gate response**
- Critical C1: `SKILL.md` referenced the old `append_decision(project_id, decision, path)` signature after T0's rename. Updated to `append_decision_persist(...)` in all 3 locations.
- Critical C2: Mission Control verdict filter only included decisions with status `open`, silently hiding decisions in `committed` / `reviewed` states — so as soon as a Cabinet verdict was reviewed, the dashboard block showed "no verdict." Filter widened to `{open, reviewed, committed}`; `reversed` still excluded.
- Important I2: First-paint flicker — when `decisionsDoc` was `null` during initial render, Cabinet block briefly showed a "No Cabinet framing yet" state before the fetch resolved. Render now defers until `decisionsDoc` is non-null, or shows a loading skeleton.
- Important I4: Silent mirror-write failures — `close_decision_persist` / `reverse_decision_persist` would silently continue if the `assets/forge-decisions.json` mirror write failed (e.g. read-only assets dir), leading to dashboard showing stale state. Now logs a warning via stderr and the caller can see the mirror-write failed.

### Known follow-ups for Wave 4

See `PLAN.md` → "Known non-blocking follow-ups from v3.2 Wave 3 reviews" for the full list. Headline items:
- I1: signature asymmetry between `append_decision_persist(project_id, decision, path)` and `close/reverse_decision_persist(path, ...)` — harmonize to `(path, ...)` shape.
- M1-M7: module-level `timezone` import dedup, end-to-end integration test (pre_mortem → heatmap → Decision Log → dashboard), `exportDecisionsMd` markdown escape hardening, `getAgentName` / `agentName` duplication consolidation, `office-template.html` / `dashboard.html` file-split threshold watch.

---

## [3.2.0-wave2] — 2026-04-17

### Added — v3.2 Cabinet Wave 2 (Mechanics)

The engine behind Wave 1's structure. Decision Log lifecycle + Pre-Mortem + Cabinet Framing schema validation + operator-level SKILL.md mechanics + reproducible Cabinet Framing simulation driver. Wave 3 (UI) is next.

**Decision Log module** (`tools/decisions_orchestrator.py`)
- `new_decision_id()` → `dec-<8 hex chars>` (8.2B address space, mirrors Evidence Pipes' `ev-` scheme)
- `compute_review_at(decided_at_iso, reversibility)` — Type 1 = 90 days, Type 2 = 30 days. UTC-correct for explicit timezone offsets (`+03:00` Saudi time normalizes properly; previous behavior silently stripped offsets)
- `append_decision(project_id, decision, path)` — atomic write via tempfile + os.replace; mirrors to `<parent>/assets/<basename>` sibling when present; extends `project_decision_index` without overwriting; dedupes by id
- `review_decisions_due(doc, now_iso)` — returns open decisions whose review_at has passed
- `close_decision(doc, id, new_status)` — open → reviewed/committed; rejects terminal-state transitions (committed → reviewed, reversed → anything)
- `reverse_decision(doc, id, successor_id)` — marks reversed, links successor, adds `reversed_by` field; rejects self-reference and already-reversed
- `DECISION_STATUSES = {open, reviewed, reversed, committed}`
- `REVERSIBILITY = {type_1, type_2}`

**Validator extensions** (`tools/validator.py`)
- `validate_decisions(doc, state, evidence_doc=None)` — id format `dec-[0-9a-f]{8}`, uniqueness, agent references (decided_by + dissenting), enum constraints (reversibility + status), ISO 8601 timestamps (decided_at + review_at), project_decision_index referential integrity, related_evidence cross-ref (when evidence_doc supplied)
- `validate_project()` auto-loads `forge-decisions.json` when present; graceful JSON error handling
- `validate_tasks()` extended with `cabinet_framing` block schema (5 canonical lenses: strategic_kernel/product_shape/build_class/economic_shape/market_bet; framing_brief required) and `pre_mortem` block schema (likelihood/impact 1-5, owner_agent exists, mitigation_phase in {phase_4_arch, phase_5_gtm, phase_6_challenge, phase_7_delivery})
- **Standing Rule 11 auto-enforced:** when `forge-tasks.cabinet_framing` is non-null and `current_project` is set, validator requires at least one decision in `project_decision_index[current_project]`. Catches "Cabinet ran but Decision Log forgotten" failure silently.

**Kill switch reconciled**
- Canonical v3.2 kill switch: `cabinet.enabled: false` in `forge-state.json` (matches Evidence Pipes' `evidence_pipes.enabled` convention for UI parity)
- `cabinet.executives: []` (Wave 1 form) still accepted as a legacy alias for backward compat
- Validator tests pin both forms

**Initialized files**
- `forge-decisions.json` (project root) — empty shell
- `assets/forge-decisions.json` — auto-mirrored copy

**Reproducible driver** (`scripts/cabinet_framing_simulate.py` + `scripts/sample_inputs/`)
- Takes canned 5-lens input + 5 pre-mortem items from `scripts/sample_inputs/`
- Writes cabinet_framing + pre_mortem + current_project to forge-tasks.json
- Creates sample Cabinet Verdict (GO at 75% for Saudi PropTech, Cade decides, Prism dissents on unit econ, Type 1)
- Persists to forge-decisions.json + mirror to assets/
- Runs validate_project end-to-end (including the new Rule 11 check)
- Mirrors the pattern established by Evidence Pipes' `run_pipeline.py`

**SKILL.md mechanics** (operator-facing)
- **Phase 1.5 mechanics** — per-exec lens production rules: Flint (Rumelt 3-part kernel, 3 sentences max), Cade (≥3 non-goals per Cagan), Helix (greenfield/retrofit + buy/build/partner + onboarding time), Prism (all 4 numbers: unit/fee/CAC/break-even), Dune (positioning + competitors + narrow category); pre-mortem 10-failure-mode ranking process; exact forge-tasks.json output shape
- **Phase 3 two-floor mechanics** — IC Floor vs Cabinet Floor firing rules, escalation ladder (IC → owning exec → Cabinet → User), Type 1 vs Type 2 classification guidance ("If unsure: default to Type 1"), code example for invoking `append_decision` with a populated decision shape
- **Phase 7 deliverable format** — Cabinet Verdict + Pre-Mortem Top Risks + 5 Cabinet Artifacts + Decision Log section structure, assembly pseudocode for operators, conditional section rules (Cabinet sections skip when no cabinet_framing fired), Standing Rule 11 invariant now auto-checked

**Tests**
- +70 new tests (11 decisions schema + 5 append + 10 lifecycle + 7 Task-15 review response + 12 validate_decisions + 4 validate_project auto-load + 8 pre_mortem + 6 cabinet_framing + 3 kill-switch + 4 rule 11)
- 235 tests total (165 Wave 1 baseline + 70 new)
- Backward compat preserved — all v3.1 Evidence Pipes + v3.2 Wave 1 tests still green

### Fixed (via Code Review Gate + Review Response)

**Task 2-4 review response (c7332b4)**
- Critical C1: `compute_review_at` now correctly converts timezone offsets to UTC. Previously `+03:00` (Saudi time) inputs silently stripped the offset, producing review_at times 3 hours off.
- Important I3: `close_decision` rejects terminal-state transitions (reviewed/committed/reversed → anything). Lifecycle is `open → terminal`, not any-to-any.
- Important I4: `reverse_decision` rejects self-reference (decision_id == successor_id).
- Spec amendment: `reversed_by` field documented in Decision Log schema.

**Foundation Code Review Gate response (56a5b31)**
- Important I3 (Foundation): kill-switch naming reconciled (`cabinet.enabled: false` canonical, `cabinet.executives: []` alias).
- Important I5 (Foundation): Standing Rule 11 auto-enforced in validate_project.

### Backward compat

Every Wave 2 addition is optional in the data model: absent `forge-decisions.json`, absent `cabinet_framing` block, absent `pre_mortem` block — all continue to validate cleanly. Wave 1's `cabinet.executives: []` kill switch remains functional.

### Out of scope (deferred to Wave 3)

- Pixel office Executive Suite pixel room
- Dashboard Cabinet block + Decisions tab + Pre-Mortem heatmap widget
- Live end-to-end project run against a real brief
- Chrome MCP pipes (separate roadmap item)

**Wave 3 Task-0 items** (captured from Foundation review, deferred per reviewer guidance):
- I1: Persistence wrappers (`close_decision_persist`, `reverse_decision_persist`) for dashboard buttons that write decisions
- I2: Upsert semantics on `append_decision` (currently silently skips if id exists)
- I4: Query helpers (`decisions_by_project`, `decisions_by_status`, `decisions_due_soon`, `decisions_sorted_by_review_at`) for dashboard tab rendering

---

## [3.2.0-wave1] — 2026-04-17

### Added — v3.2 Cabinet Wave 1 (Roster & Protocol)

The roster + data-model foundation of the v3.2 Cabinet expansion. Evolves The Forge from a flat 9-agent peer strike team into a two-tier org with a real executive judgment layer. Cabinet mechanics (Wave 2) and UI (Wave 3) are follow-up releases; this wave is data + docs.

**6 new agents** — each with named practitioner playbooks and signature artifacts

- **Cade** (CPO) — Marty Cagan disciple. Product One-Pager signature artifact. Reports to Flint. Heads new Product department. Owns product intel ICs (Vex/Nyx/Echo/Ren/Sable/Zeta).
- **Helix** (CTO) — Camille Fournier (The Manager's Path) disciple. Technology Strategy Memo. Reports to Flint. Heads Engineering; Atlas now reports to Helix.
- **Prism** (CFO) — Tomasz Tunguz + David Sacks disciple. Unit Economics Model. Reports to Flint. Solo in new Finance department.
- **Dune** (CMO) — April Dunford + Bob Moesta disciple. Positioning Document. Reports to Flint. Heads Growth + Content; Talon + Kira now report to Dune.
- **Lex** (Chief Legal Counsel) — pragmatic commercial lawyering (Reed Smith school + Pat McKenna). Risk Register + Contract Brief. Solo in new Legal department. Reports to Flint.
- **Zeta** (Data Lead) — Benn Stancil + Emily Glassberg Sands disciples. Experiment Design Brief + KR Instrumentation Plan. IC in Research. Reports to Cade.

**3 new departments**
- **Product** (`dept-product`, #7E57C2 muted purple) — Cade
- **Legal** (`dept-legal`, #546E7A slate grey) — Lex
- **Finance** (`dept-finance`, #26A69A teal) — Prism

**Two-tier org structure — 15 agents total**
- 5 executives: Flint (CSO — now with Rumelt playbook disciple + Strategy Kernel signature artifact), Cade (CPO), Helix (CTO), Prism (CFO), Dune (CMO)
- 10 ICs: Vex, Nyx, Echo, Zeta (Research); Ren, Sable (Design); Atlas (Engineering); Talon (Growth); Kira (Content); Lex (Legal)
- Top-level `cabinet.executives` block names the Cabinet explicitly
- Every IC has `reports_to` pointing to its owning executive — validator enforces

**Protocol v3.1 → v3.2 (documented; mechanics implemented in Wave 2)**
- Phase 1.5 Cabinet Framing (5 lenses + Klein-style pre-mortem) — spec'd
- Phase 3 two-floor War Room (IC floor + Cabinet floor) — spec'd
- Phase 4 sequence now Helix → Atlas → Ren → Sable
- Phase 5 sequence now Dune → Talon → Kira → Nyx
- Phase 7 new deliverable format: Cabinet Verdict + 5 signature artifacts + Decision Log section + Sources Appendix
- Standing Rule 10 (escalation ladder — IC → owning exec → Cabinet → User)
- Standing Rule 11 (every Cabinet Verdict logs a Decision entry with reversibility)

**Rivalry matrix — 10 rivalries across 2 scales**

Cross-functional C-Suite (NEW):
- Cade ↔ Helix ("Ship features" vs "Pay down debt")
- Prism ↔ Dune ("LTV:CAC says no" vs "Brand equity")
- Flint ↔ Cade ("Question the plan" vs "Execute the plan")

Cross-layer (NEW):
- Helix ↔ Atlas ("3-year horizon" vs "This sprint")
- Dune ↔ Talon ("Strategic positioning" vs "Tactical growth hack")

IC-level (new + existing):
- Vex ↔ Zeta ("External market" vs "Internal funnel") — NEW
- Lex ↔ Talon ("Defensible" vs "Just try") — NEW
- Vex ↔ Echo (existing)
- Talon ↔ Ren (existing)
- Sable ↔ Kira (existing)

All rivalries now mirror-documented in both participants' brain files.

**Validator extensions**
- `role` field enforced as `"executive"` or `"ic"` when present
- `reports_to` must reference existing agent; ICs must report to executives; executives may report to other executives; self-reference rejected with clear error
- `cabinet.executives` block validated — members must exist + have `role: "executive"`; type guards on `cabinet` (must be dict) and `cabinet.executives` (must be list)
- Non-scalar `reports_to` values (list, dict) rejected cleanly instead of crashing
- Backward compat: all new fields are optional during migration — v3.1 state files still validate

**Brain files**
- 6 new brain files (Cade/Helix/Prism/Dune/Lex/Zeta) at the quality bar of the existing 9 — Hot Take with expansion, Playbook Disciple, Go-To Framework with filled examples referencing real Forge projects (Pet Healthcare, Digital Signature, Saudi Neobank), Anti-Patterns, Mentorship Role, Rivalries, Signal Tags, Signature Artifact, Cabinet Framing Lens (execs) or Consumed By (ICs), Evidence Pipes disposition
- **Flint's brain file uplifted** — now includes Playbook Disciple (Rumelt), Strategy Kernel framework with worked example, vs Cade rivalry, Cabinet Framing Lens section
- Atlas/Talon/Vex brain files updated with new cross-layer rivalries (vs Helix / vs Dune + vs Lex / vs Zeta)

**Documentation**
- `SKILL.md` gained Cabinet Framing (v3.2) section with activation triggers table
- `references/collaboration-protocol.md` bumped v3.1 → v3.2 with Phase 1.5, two-floor Phase 3, Phase 7 format, Standing Rules 10-11; Hot Takes / Rivalries / Mentorship Chains tables extended to full 15-agent roster
- `references/cabinet-framing-spec.md` NEW — operator-facing reference for Phase 1.5
- `references/agent-design-guide.md` — v3.2 fields section + 3 new department color palette entries

**Tests**
- +14 validator tests (8 initial v3.2 rules + 5 review-response type-guard tests + 1 portfolio-invariants smoke test)
- 165 tests total (151 Evidence Pipes baseline + 14 v3.2)
- Portfolio smoke test pins: 15 agents, 9 departments, 5 execs, 10 ICs, cabinet matches executive set, every IC reports to an executive

### Fixed (via Foundation Code Review Gate)

**Two-stage code review caught 2 Critical + 3 Important findings per batch:**

Task 2 review (validator rules):
- Critical: `cabinet.executives: null` was crashing with TypeError instead of producing a readable error. Added dict/list type guards.
- Critical: non-scalar `reports_to` (list, dict) crashed with unhashable-type TypeError. Added `isinstance(str)` check before set membership lookup.
- Important: self-reference in `reports_to` now produces dedicated "cannot reference itself" error.

Tasks 5-10 review (6 new agents):
- Critical: Lex and Zeta had `playbook_disciple: null` in state despite brain files naming practitioners. Backfilled.
- Critical: All 6 new agents were missing `avatar.department_accent_color` — pixel office would render orange-fallback. Backfilled from department colors.
- Flint's state-level `playbook_disciple` (Rumelt) and `signature_artifact` (Strategy Kernel) also backfilled.

Foundation Gate review (Wave 1 holistic):
- Important: Flint's brain file was still v3.0 (no Cabinet Framing Lens, no Rumelt section). Uplifted to match the depth of the new C-Suite brain files.
- Important: Rivalry asymmetry — the 4 pre-existing brain files (Flint, Atlas, Talon, Vex) didn't mirror the new cross-layer rivalries that the new 6 described. All 4 updated to close the asymmetry.
- Important: `collaboration-protocol.md` interior tables (Hot Takes, Rivalries, Mentorship Chains) still enumerated v3.0 roster. Extended all three to cover 15 agents / 10 rivalries / 8 mentors.

### Backward compat

Setting `cabinet.executives: []` or omitting the cabinet block restores v3.1 behavior byte-for-byte. All v3.1 state files continue to validate without modification. All 151 Evidence Pipes v3.1 tests remain green with zero regressions.

### Out of scope (deferred)

- Cabinet mechanics — `tools/decisions_orchestrator.py`, `validate_decisions()`, `forge-decisions.json`, Phase 1.5 artifact generation — **Wave 2**
- UI — Executive Suite pixel room, Cabinet block on Mission Control, Decisions tab, Pre-Mortem heatmap — **Wave 3**
- Hierarchy tree visualization — **Sub-project A** (post Wave 3)
- Subagent delegation, Context system, Tools catalog — **Sub-projects C/D/E**

---

## [3.1.0] — 2026-04-17

### Added — Evidence Pipes v1

The headline feature of this release. Four research agents (Vex, Nyx, Echo, Talon) gained real data pipes via `superpowers:dispatching-parallel-agents`. Every `[FACT]` emitted by a Forge agent is now linkable, timestamped, quality-graded, cached, and conflict-aware.

**Core data model**
- New `Evidence` dataclass with 12 fields (id, claim, source_url, source_title, source_type, quality_score 1–5, retrieved_at, retrieved_by, queried_via, excerpt, confidence, signal_tag)
- 8-character hex Evidence IDs (`ev-<8hex>`) — 4.3B address space, birthday collision at ~9,000 entries
- `SOURCE_TYPES` frozenset (8 values) and `SIGNAL_TAGS` frozenset (4 values) pin the taxonomy

**Orchestration**
- `evidence_orchestrator.score_agent_relevance(agent_id, brief)` scores 0–3; activated at ≥ 2
- `evidence_orchestrator.generate_sub_brief()` produces per-agent sub-briefs with persona-adjusted preferences, 8-query budget, tier-3 quality floor
- Parallel fan-out via `superpowers:dispatching-parallel-agents` — 4 concurrent subagent dispatches during Phase 2 (Intelligence)
- Fan-in merge dedupes by `(source_url, excerpt)` — distinct excerpts from the same page are preserved
- `evidence_orchestrator.append_evidence()` persists atomically to `forge-evidence.json` AND mirrors to `assets/forge-evidence.json` so the live dashboard stays in sync
- `evidence_orchestrator.strip_unsupported_claims()` mechanically enforces Standing Rule 7 — `[FACT]`, `[INFERENCE]`, and naked `[ev-X, ev-Y]` brackets with unknown IDs get flagged with `⚠ <id> unsupported` or collapsed to `[UNSUPPORTED — dropped by validator]`

**Quality grading**
- `evidence_quality.grade_url()` maps URLs to `(score 1–5, source_type)` via regex rules
- Default rules cover 5 tiers: primary_government (SAMA, MEWA, MCIT, SEC) > primary_company (10-K, IR, pricing) > analyst / reputable_media (McKinsey, FT, Wamda) > user_reviews / community (App Store, Reddit) > blog
- Anchored regex prevents false matches (`ir.apple.com` matches; `fair.apple.com` does not)
- User-extensible via `evidence-quality-overrides.json` at project root — rules prepend to defaults and win on match

**Freshness**
- Per-source-type stale/refetch bands in `evidence_freshness.FRESHNESS_RULES`: gov 180/730d, company 90/365d, analyst 365/1095d, reviews 30/180d, blog 90/365d
- `classify_freshness(source_type, retrieved_at, now_iso)` returns `"fresh" | "stale" | "refetch"`; pure function, caller supplies `now`

**Cache**
- Content-addressed cache at `assets/.forge-cache/` keyed on `sha256(normalize_query(q) + "|" + url)`
- Atomic writes via `tempfile.mkstemp` + `os.replace` prevent corruption under parallel subagent dispatch
- `read_cache` tolerates corrupt JSON and read-only files; no hit-counter mutation on read (preserves mtime-based LRU determinism)
- LRU eviction by mtime with `evict_lru(keep=N)`
- CLI stats: `python3 tools/validator.py --cache-stats`

**Conflict detection**
- `evidence_conflict.detect_conflicts()` clusters Evidence by Jaccard content-token overlap (≥ 0.4), extracts numerics from excerpts, flags divergence > 20% within a cluster
- Comma-thousands aware (`$1,340M` → `1340.0`), year-token-excluding (bare 4-digit `2024` ignored unless unit-suffixed)
- Deterministic clustering — items sorted by ID before iteration; output identical across runs regardless of input order
- `resolve(conflict, brief_scope)` picks winner by **scope > tier > recency**

**Protocol v3.1**
- Collaboration protocol bumped from v3.0 to v3.1
- Three new Standing Rules:
  - **7. No citation, no claim** — `[FACT]` / `[INFERENCE]` without Evidence ID gets stripped
  - **8. Quality floor for GO decisions** — GO with ≥ 1 tier-1 blog source and no tier-3+ backing gets flagged `⚠ THIN EVIDENCE`
  - **9. Freshness gate** — Evidence past `stale` threshold flagged `⏰ STALE`; past `refetch` requires re-query
- Phase 2 (Intelligence) rewritten as parallel dispatch flow
- `forge-state.json` gained `evidence_pipes.enabled` flag (default `true`)

**Deliverable format**
- New **EVIDENCE SUMMARY** block above every recommendation: queries, sources cited, avg quality, conflicts, cache hits, elapsed
- New **Sources Appendix** below every recommendation — compact one-line-per-source for terminal; full Markdown with excerpts + retrieval dates + agent attribution for export
- All agent contributions become citation-dense — `[ev-...]` inline references replace bare `[FACT]` tags

**Validator**
- New `validate_evidence(doc, state)` covering: ID uniqueness, index → evidence referential integrity, `retrieved_by` → agent existence, `quality_score` [1,5], `confidence` [0,1], `source_type` enum, `signal_tag` enum, URL scheme (http/https/local), ISO 8601 `retrieved_at` with fractional seconds
- `validate_project()` auto-loads `forge-evidence.json` and reports malformed JSON with a readable error (no traceback)
- `retrieved_by` must be a list — bare strings rejected with a clear error instead of iterating character-by-character
- Missing `id` produces "Evidence at index N is missing required field: id" instead of a misleading duplicate error

**Dashboard (v3.1 UI)**
- New **Evidence block** on Mission Control tab — queries progress, sources cited, avg quality stars, per-agent freshness dots (green < 90d worst age, amber 90–180d, red > 180d)
- New **Sources tab** (tab 5) — full Evidence table with free-text search, filter by tier / agent / freshness, export to Markdown / CSV / JSON
- XSS-safe URL rendering: `safeUrl()` only allows `http://`, `https://`, `local://`; anything else becomes `#`
- Kill switch handling: when `evidence_pipes.enabled: false`, the Evidence block and Sources tab are hidden entirely — no "0 queries" false-breakage signal

**Pixel office (v3.1 animations)**
- New `dispatched` event: yellow `[!]` bubble pulses above an agent's desk while their subagent is fetching evidence
- New `evidence_arrived` event: green `shadowBlur` glow around the desk outline when Evidence returns and merges
- `evState` reset between events — fan-out bubbles no longer persist through fan-in glow

**Tests**
- 151 unit tests, TDD-built, all green
- New test files: `test_evidence_schema.py` (5), `test_evidence_quality.py` (21), `test_evidence_freshness.py` (12), `test_evidence_cache.py` (11), `test_evidence_conflict.py` (16), `test_evidence_orchestrator.py` (26), `test_evidence_appendix.py` (6), `test_cross_module_consistency.py` (4)
- Extended `test_validator.py` +14 tests for `validate_evidence()` and `--cache-stats` CLI

**Documentation**
- New `references/evidence-pipes-spec.md` — operator-facing reference loaded during Phase 2
- SKILL.md gained **Evidence Pipes** section (9-step dispatch flow, budgets, kill switch, failure modes)
- Output Format requires EVIDENCE SUMMARY + Sources Appendix when pipes fire
- Quality Standards gains "No citation, no claim" bullet
- `docs/superpowers/specs/2026-04-16-evidence-pipes-v1-design.md` — full design spec (~540 lines)
- `docs/superpowers/plans/2026-04-16-evidence-pipes-v1.md` — 16-task implementation plan
- `docs/superpowers/runs/2026-04-17-neobank-brief/` — **first live end-to-end run**, fully documented with raw subagent JSON returns, deliverable Markdown, run metrics, and honest qualitative v3.0 vs v3.1 comparison

### Fixed (via two formal Code Review Gates)

Two `superpowers:requesting-code-review` gates caught real bugs across the feature branch — both blocked the merge until resolved:

**Foundation Code Review Gate (post Tasks 1-6)**
- C1: `sys.path.insert` mutation at import is now idempotent — prevents duplicate entries under repeated imports
- C2: `resolve()` guards against empty conflict items — raises `ValueError` with clear message instead of cryptic `max()` failure
- C3: `extract_numbers` v1 limitation (unit-mixed clusters) documented + pinning test added
- I2: Cross-module consistency tests added — `SOURCE_TYPES` (schema) / `FRESHNESS_RULES` (freshness) / `DEFAULT_RULES` source_types (quality) now pinned to stay in sync
- I3: ISO-8601 parsing unified across modules — all three use `datetime.fromisoformat` with `Z` → `+00:00` normalization; accepts fractional seconds (real WebSearch returns)
- I4: `read_cache` no longer writes back hit counter — preserves mtime-based LRU determinism under parallel dispatch

**Second (End-to-End) Code Review Gate (post Tasks 7-14)**
- C1: `strip_unsupported_claims` regex expanded to catch naked `[ev-X, ev-Y]` citation forms (the form agents actually emit). Previously only matched `[FACT: ev-X]`, making Standing Rule 7 enforcement a silent no-op on real agent prose.
- C2: `merge_returns` dedup key changed from `source_url` alone to `(source_url, excerpt)`. Two distinct excerpts from the same page are NO LONGER silently collapsed. Prevents orphaning citations to the second excerpt.
- I1: `evidence-quality-overrides.json` is now actually loaded in the orchestrator path via `PROJECT_QUALITY_RULES` at module scope. Previously shipped as dead code.
- I8: Original Task 14 run report contained factual errors (claimed "all criteria met" when citation enforcement was silently no-op'd). Corrected with a "Post-review update (Task 15)" section documenting the pre-fix and post-fix state honestly.

### Changed

- `forge-state.json` schema: added top-level `evidence_pipes: { enabled: true }` block
- `forge-tasks.json` schema: existing; unchanged in v3.1 but Phase 2 task entries now carry subagent dispatch status
- `.gitignore` updated to ignore `assets/.forge-cache/*` while preserving `.gitkeep`

### Meta

- 28 commits on the `evidence-pipes-v1` feature branch, merged with `--no-ff` to preserve the review history
- Zero new runtime dependencies — Python stdlib only (3.9+)
- Real-file smoke test guards against drift between validator and shipped state

---

## [3.0.0] — 2026-04-07

### Added — Elite Protocol

- **Collaboration Protocol v3.0** — 8 phases with 15 enhancement layers
- **9 Agent Second Brain files** (`references/brains/`) — framework templates, hot takes, anti-patterns, mentorship, rivalries, signal tags
- **Agent Design Guide** — credential checks, persona standards, avatar specs
- **Team of 9 agents across 6 departments**: Flint (Strategy), Vex/Nyx/Echo (Research), Ren/Sable (Design), Talon (Growth), Atlas (Engineering), Kira (Content)
- 15 elite enhancements: Second Brain files, Show Your Work, Disagree by Default, Deliverable Templates (Lean Canvas, AARRR, C4, etc.), Quantify or Die, One-Slide Constraint, Handoff Memos, Cross-Examination, Signal Tags ([FACT]/[INFERENCE]/[HYPOTHESIS]/[OPINION]), Hot Takes, Mentorship Chains, Rivalries, Project Memory, Skill Stacking, Live Office Visualization
- **Pixel art office** (1,300+ lines) — 6 rooms, hallway, break room, chibi sprites with 4-tone shading, door routing, event-driven animations
- **4-tab dashboard** — Mission Control, Network Graph (force-directed), Kanban, Timeline (Gantt)
- **Task visualization overlays** — task bubbles above agents, phase progress bar, room glow
- **State validator** (`tools/validator.py`) with 26 tests covering state/tasks/brain-file integrity
- **Plugin packaging** — installable via `npx skills add elden-studios/the-forge@the-forge -g`
- **README + TEAM + 4 design specs** in `docs/superpowers/specs/`

### Completed Projects (v3.0)
- Digital Signature Platform — GO at 75% confidence
- Pet Healthcare Platform (Saudi) — GO at 80% confidence

---

## [1.0.0] — 2026-04-05

Initial release. SKILL.md orchestration, first-run onboarding flow, agent creation protocol with credential check, department creation, roster/office commands, pixel art avatar specs.
