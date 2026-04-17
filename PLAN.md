# The Forge — Progress & Resume Guide

## Current Status: Evidence Pipes v1 in flight — 13/16 tasks complete

**GitHub:** https://github.com/elden-studios/the-forge
**Active branch:** `evidence-pipes-v1` (LOCAL ONLY — 21 commits ahead of main, not pushed)
**Last session:** 2026-04-16
**Test count:** 142/142 green
**Real project:** validates cleanly (`python3 tools/validator.py` → OK)

---

## Ship log before Evidence Pipes v1 (on `main`)

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
- 4-tab real-time dashboard (Mission Control, Network Graph, Kanban, Timeline)
- State validator, 26 tests, `tools/validator.py`
- Plugin packaged, installable via `npx skills add elden-studios/the-forge@the-forge -g`

### Completed projects (on main)
| # | Project | Decision | Confidence |
|---|---------|----------|------------|
| 1 | Digital Signature Platform | GO | 75% |
| 2 | Pet Healthcare Platform (Saudi) | GO | 80% |

---

## 🔥 IN FLIGHT — Evidence Pipes v1

**Spec:** `docs/superpowers/specs/2026-04-16-evidence-pipes-v1-design.md`
**Plan:** `docs/superpowers/plans/2026-04-16-evidence-pipes-v1.md`
**Branch:** `evidence-pipes-v1` (local, 21 commits ahead of main, NOT PUSHED)

### What Evidence Pipes v1 does
Turns every `[FACT]` tag in agent output into a linkable, timestamped, quality-graded, cached, conflict-aware Evidence object. Moves The Forge from "ChatGPT with personality" to "board-room-defensible recommendations with an audit trail."

- 4 research agents (Vex, Nyx, Echo, Talon) fan out in parallel via `superpowers:dispatching-parallel-agents`
- Each runs real WebSearch (Chrome MCP phase 2) against a sub-brief
- Fan-in merges Evidence, dedupes by URL, detects numeric conflicts
- Persists to `forge-evidence.json` (root + mirrored to `assets/` for live dashboard)
- Deliverable ships with Sources Appendix + EVIDENCE SUMMARY block
- `[FACT]` without Evidence ID gets stripped by the validator mechanically
- Kill switch: `forge-state.json` → `evidence_pipes.enabled: false` reverts to v3.0

### Tasks completed (13/16) — all TDD'd where applicable, two-stage reviewed

| # | Task | Commit SHA | Review findings addressed |
|---|------|------------|--------------------------|
| 1 | Evidence schema (dataclass, enums, ID gen) | `f24893d` → `18b3b86` | I2 (from_dict trust docstring), I3 (widen ID 6→8 hex), M3 (drop unused import) |
| 2 | Quality grading (regex rules + overrides) | `c6fc50d` → `7d05204` | C1 (anchor `ir.`/`reddit.` patterns), I3+I4 (harden load_overrides) |
| 3 | Freshness (per-tier stale/refetch bands) | `ac40d32` | (batched review with 4+5) |
| 4 | Cache (content-addressed + LRU) | `9e62753` | (batched review with 3+5) |
| 5 | Conflict detection (scope>tier>recency) | `b0e6517` → `4119d50` | C1 (atomic cache writes), C2 (fix number regex), I1 (deterministic clustering), I4 (graceful freshness errors) |
| 6 | Validator extension + `--cache-stats` CLI | `a9b3fe1` → `6dbde81` | I1 (retrieved_by type guard), I2 (missing id clear error), I3 (fractional ISO accepted) |
| — | **🛑 Foundation Code Review Gate** | `9c4b6a4` | C1 (idempotent sys.path), C2 (resolve empty guard), C3 (0% numeric pinning), I2 (cross-module consistency tests), I3 (ISO unification), I4 (remove hit-counter write-back) |
| 7 | Sub-brief generation + orchestrator | `3f70ac4` | (batched review with 8+9) |
| 8 | append_evidence + strip_unsupported_claims | `504a9a8` | (batched review with 7+9) |
| 9 | Sources Appendix renderer | `375b1da` → `a75589a` | I1 (atomic append_evidence), I2 (`!r` → natural Markdown), I3 (neobank/fintech keywords), M-dead-import |
| 10 | SKILL.md + protocol v3.1 + kill switch | `fda5702` | (docs-only; no review needed) |
| 11 | Dashboard Evidence block on MC tab | `ba774f0` | (reviewed with 12+13) |
| 12 | Dashboard Sources tab with export | `42d57af` | (reviewed with 11+13) |
| 13 | Pixel office dispatch animations | `fc52f8b` → `0bbbcea` | C1 (evidence file sync to assets/), C2 (URL scheme validation — XSS), C3 (clear evState between events), I1 (kill-switch hide UI) |

### Modules & files shipped

```
tools/
├── evidence_schema.py       ✅ Evidence dataclass, SOURCE_TYPES (8 incl 'unknown'), SIGNAL_TAGS, new_evidence_id()
├── evidence_quality.py      ✅ grade_url, load_overrides, merge_rules, DEFAULT_RULES
├── evidence_freshness.py    ✅ classify_freshness, FRESHNESS_RULES, days_between
├── evidence_cache.py        ✅ make_key, normalize_query, read/write_cache (atomic, no-mutation reads), cache_stats, evict_lru
├── evidence_conflict.py     ✅ cluster_by_keywords, extract_numbers, detect_conflicts, resolve
├── evidence_orchestrator.py ✅ EVIDENCE_AGENTS, score_agent_relevance, generate_sub_brief, merge_returns, append_evidence, strip_unsupported_claims, _atomic_write_json
├── evidence_appendix.py     ✅ render_compact, render_markdown, render_summary_block
└── validator.py             ✅ + validate_evidence(), --cache-stats flag, validate_project auto-loads forge-evidence.json

tests/ — 142 tests across 9 files
├── test_evidence_schema.py          5
├── test_evidence_quality.py         21
├── test_evidence_freshness.py       12
├── test_evidence_cache.py           11
├── test_evidence_conflict.py        16
├── test_evidence_orchestrator.py    15
├── test_evidence_appendix.py        6
├── test_validator.py                40
└── test_cross_module_consistency.py 4

assets/
├── dashboard.html          ✅ Evidence block on MC + Sources tab (filter/search/MD-CSV-JSON export)
├── office-template.html    ✅ 'dispatched' pulsing bubble + 'evidence_arrived' glow animations
├── office-live.html        ✅ Synced copy with same animations
├── forge-evidence.json     ✅ Empty shell; append_evidence mirrors here from root
└── .forge-cache/           ✅ Gitignored cache dir + .gitkeep

forge-state.json            ✅ evidence_pipes.enabled: true added
forge-evidence.json         ✅ Empty shell at project root
evidence-quality-overrides.json  (optional, not created yet)

references/
├── collaboration-protocol.md  ✅ Bumped v3.0 → v3.1, Standing Rules 7-9 added, Phase 2 rewritten
└── evidence-pipes-spec.md     ✅ NEW — operator-facing pipes protocol

SKILL.md                    ✅ NEW 'Evidence Pipes' section, Phase 2 pointer, Output Format + Quality Standards updates
```

### 21 commits on the feature branch (newest first)

```
0bbbcea Tasks 11-13 review response — sync evidence to assets, safe URLs, clear evState, kill switch
fc52f8b Pixel office — evidence dispatch animation variants
42d57af Dashboard — Sources tab with filters, search, export
ba774f0 Dashboard — Evidence block on Mission Control tab
fda5702 SKILL.md + protocol v3.1 — Evidence Pipes operator instructions
a75589a Tasks 7-9 review response — atomic append, natural Markdown, fintech keywords
375b1da Sources Appendix renderer — compact + Markdown
504a9a8 Orchestrator — append_evidence() + strip_unsupported_claims()
3f70ac4 Evidence orchestrator — sub-brief generation + fan-in merge
9c4b6a4 Foundation review response — idempotent path, empty-items guard, ISO unification
6dbde81 Task 6 review response — type guards, clear errors, fractional ISO, perf cleanup
a9b3fe1 Validator — add validate_evidence() + --cache-stats CLI flag
a10b7fc Checkpoint — Evidence Pipes v1, 5/16 tasks complete
4119d50 Tasks 3-5 review response — atomic cache, numeric parsing, deterministic clustering
b0e6517 Evidence conflict — detection + scope>tier>recency resolution
9e62753 Evidence cache — content-addressed, LRU
ac40d32 Evidence freshness — per-source-type stale/refetch bands
7d05204 Quality grading review response — anchor ir/reddit patterns, harden load_overrides
c6fc50d Evidence quality grading — regex rules + user overrides
18b3b86 Schema review response — widen ID, document from_dict trust, drop unused import
f24893d Evidence schema — dataclass, enums, ID generator
```

---

## 🎯 NEXT SESSION: Resume at Task 14

**Starting point:** Plan file, section `## Task 14: End-to-end validation — synthetic brief (Saudi expat neobank)`.

### What Task 14 does

**Real end-to-end demo of Evidence Pipes v1.** NOT a TDD task — it's a live exercise:

1. **Trigger the skill** on a fresh chat session (separate from implementation work). User prompt:
   > "Activate The Forge. Brief: I want to launch a neobank targeting Saudi expats remitting to South Asia. Evaluate market, regulatory, user, and growth angles."

2. **Observe the pipeline fire:**
   - Flint scores all 4 evidence agents → all should activate (brief touches market/regulatory/user/growth)
   - 4 subagents dispatched in parallel via `superpowers:dispatching-parallel-agents`
   - Each subagent returns 5-12 Evidence objects
   - Fan-in merges, dedupes cross-agent URL overlaps
   - `forge-evidence.json` grows with a `proj-003` index
   - Dashboard Evidence block fills with real metrics (green freshness dots appear)
   - Office renders `dispatched` pulsing bubbles, then `evidence_arrived` green glows
   - Sources tab in dashboard populates with ~20-40 rows, filterable
   - Deliverable ends with EVIDENCE SUMMARY + compact Sources Appendix
   - All `[FACT]` tags reference valid Evidence IDs

3. **Document the run** — create `docs/superpowers/runs/2026-04-<date>-neobank-brief-run.md` with:
   - Original brief
   - Evidence Summary box (literal copy from the deliverable)
   - Sources Appendix (compact form)
   - Qualitative notes: what was visibly better vs v3.0? What failed or rough edges?
   - Measured metrics: query count, elapsed, cache hit rate, avg quality, conflicts found

4. **Verify post-run integrity:**
   ```bash
   python3 tools/validator.py            # expect OK
   python3 tools/validator.py --cache-stats  # should show real entries after the run
   python3 -m unittest discover tests -v     # still 142 green
   ```

5. **Commit the run document:**
   ```bash
   git add docs/superpowers/runs/ forge-evidence.json
   git commit -m "Synthetic validation run — Saudi expat neobank brief"
   ```

### 🛑 Second Code Review Gate (after Task 14 run)

Immediately after Task 14 closes, invoke `superpowers:requesting-code-review` on commits Task 7 through Task 14 (orchestration → end-to-end). Pass the run document path as review context so the reviewer can evaluate actual output quality, not just code diffs.

### Tasks 15-16 (after review)

- **Task 15** — Address any Critical/Important findings from the final review. TDD each fix.
- **Task 16** — Invoke `superpowers:finishing-a-development-branch`. Present the 4 options (merge locally / push PR / keep / discard). Branch currently has **21+ commits** ahead of main — PR option is probably the cleanest for review history and portfolio showcase value.

### How to resume

1. Open Claude Code in `/Users/lbazerbashi/Elden Studios/the-forge`
2. Confirm branch: `git branch --show-current` → `evidence-pipes-v1`
3. Tell Claude:
   > "Resume Evidence Pipes v1. Run Task 14 — the synthetic end-to-end brief (Saudi expat neobank → South Asia remittance). See PLAN.md 'NEXT SESSION' section for the full resume protocol."
4. Claude will trigger the skill with the synthetic brief prompt, observe the pipeline, document the run.
5. After Task 14, Claude invokes `superpowers:requesting-code-review` for the final gate.
6. After review, Tasks 15-16 to close.

### Discipline to carry forward

- Reviews (spec + quality) have caught real bugs at every single task — Critical ones included. Don't skip them.
- Subagent dispatches work but cost context. With Opus 4.7 at 1M tokens there's plenty of headroom, but for any task touching >5 files consider batching.
- Keep `forge-evidence.json` synced between root and `assets/` (the `append_evidence` helper does this automatically when assets/ sibling exists).

### Known non-blocking follow-ups

- **Spec divergence:** plan/code use Jaccard threshold 0.4 for conflict clustering, spec section 5 says "≥ 0.6". Either update spec or document rationale in `evidence_conflict.py`. Not a bug; drift.
- **Crunchbase / LinkedIn** missing from default quality rules. Can be added to `DEFAULT_RULES` or covered via `evidence-quality-overrides.json`.
- **Cross-module integration test** covering one Evidence through all 6 foundation modules end-to-end. Unit tests are strong but no single test walks the full lifecycle.
- **Merge commit messages drifted** from their diffs on the UI task batch (ba774f0 contains most of what 42d57af's message describes). Cosmetic; noted during review.
- **Tab nav indicator** briefly doesn't update when switching to Sources (Mission Control's orange underline persists). Panel swap works; indicator is cosmetic.

---

## Office access

- **Desktop launcher:** `~/Desktop/Forge Office.command` — double-click, syncs state, opens in browser
- **URL:** http://localhost:8765/office-live.html (when server is running)
- **Dashboard:** http://localhost:8765/dashboard.html (Evidence block on MC, Sources tab)

## Key commands

```bash
# Run full Python test suite
python3 -m unittest discover tests -v

# Validate all state/tasks/evidence files
python3 tools/validator.py

# Check evidence cache stats
python3 tools/validator.py --cache-stats

# See all commits on feature branch
git log --oneline evidence-pipes-v1 ^main

# Force-sync state/tasks into assets/ if office looks stale
cp forge-state.json forge-tasks.json forge-evidence.json assets/
```
