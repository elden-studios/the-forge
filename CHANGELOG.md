# Changelog

All notable changes to The Forge are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Version numbers track the collaboration protocol (`v3.x`), NOT the plugin's npm-style `package.json` version (which bumps with any user-visible change).

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
