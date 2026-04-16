# Evidence Pipes v1 — Design Spec

**Date:** 2026-04-16
**Status:** Approved for implementation planning
**Scope:** Axis B of the v4.0 enhancement plan — External Truth / Data Pipes
**Sequel:** A+D (Memory & Calibration) — separate spec after B ships

---

## Purpose

Turn every `[FACT]` emitted by a Forge agent into a linkable, timestamped, graded, reproducible, cached, and conflict-aware Evidence object. Move The Forge from "ChatGPT with personality" to "board-room-defensible recommendations with an audit trail."

## Competition class

Not other AI agents. The comparison is Bloomberg Terminal, Perplexity, Palantir Foundry, Elicit. Every claim must be:

1. **Linkable** — click, see source
2. **Timestamped** — "as of YYYY-MM-DD," decay flagged
3. **Graded** — source quality ranked (government > analyst > blog)
4. **Reproducible** — anyone can re-run the query
5. **Cached** — same query twice in 10 min doesn't hit the network twice
6. **Conflictable** — when two sources disagree, that surfaces, doesn't silently resolve

Current Forge state: zero of six. That's the magnitude of the lift.

---

## Architecture

```
User brief
   │
   ▼
Flint (orchestrator)
   │
   ├─► Scope brief, identify workstreams
   ├─► Activate relevant agents (existing scoring)
   ├─► Generate a per-agent sub-brief for the 4 evidence agents
   │
   ▼
 PARALLEL FAN-OUT — superpowers:dispatching-parallel-agents
   │
   ├─► Vex subagent    ← WebSearch (+ Chrome MCP phase 2)
   ├─► Nyx subagent    ← WebSearch (+ Chrome MCP phase 2)
   ├─► Echo subagent   ← Chrome MCP primary (phase 2) + WebSearch
   ├─► Talon subagent  ← WebSearch (+ Chrome MCP phase 2)
   │
   ▼
 FAN-IN (Flint)
   │
   ├─► Receive N evidence bundles in parallel
   ├─► Dedupe sources by URL
   ├─► Detect conflicts (numeric divergence > 20%)
   ├─► Persist to forge-evidence.json
   │
   ▼
 Reasoning agents (sequential, existing)
   │
   ├─► Ren, Sable, Atlas, Kira synthesize using the Evidence bundle
   │
   ▼
 War Room (Phase 3, existing; now conflicts are evidence-backed)
   │
   ▼
 Final Deliverable + Sources Appendix
```

**Key property:** parallelism happens at the I/O boundary, not the reasoning boundary. Evidence agents fan out; reasoning agents run sequentially because they depend on the fan-in.

---

## Data model — Evidence object

```json
{
  "id": "ev-7f2a3c",
  "claim": "Saudi pet care market grew 14% YoY in 2024",
  "source_url": "https://mewa.gov.sa/.../annual-report-2024",
  "source_title": "MEWA Annual Report 2024 — Livestock & Companion Animals",
  "source_type": "primary_government",
  "quality_score": 5,
  "retrieved_at": "2026-04-16T14:32:00Z",
  "retrieved_by": ["agent-vexx"],
  "queried_via": "WebSearch",
  "excerpt": "...direct quote from the source, 15-40 words...",
  "confidence": 0.92,
  "signal_tag": "FACT"
}
```

### Source-type taxonomy → quality_score (1-5)

| Tier | Score | source_type | Examples |
|---|---|---|---|
| Primary government/regulatory | 5 | `primary_government` | MEWA, SAMA, MCIT, StatsBureau, SEC, ESMA |
| Primary company source | 4 | `primary_company` | 10-K, earnings, IR pages, official pricing |
| Reputable analyst/media | 3 | `analyst` / `reputable_media` | McKinsey, BCG, Gartner, FT, Reuters, Wamda |
| User-generated quality | 2 | `user_reviews` / `community` | App Store, Reddit, Product Hunt, HN |
| Blog / low signal | 1 | `blog` | Medium, Substack, unsigned content |

Unknown/no-match default → **score 2** (conservative — not worst, not trusted).

### Storage layout

```
forge-state.json        ← roster (existing; gains evidence_pipes.enabled flag)
forge-tasks.json        ← workflow (existing; gains subagent dispatch status)
forge-evidence.json     ← NEW — Evidence objects + project index
assets/.forge-cache/    ← NEW — query cache (gitignored)
```

`forge-evidence.json` shape:

```json
{
  "evidence": [<Evidence objects>],
  "project_evidence_index": {
    "proj-003": ["ev-7f2a3c", "ev-9b8e1d", ...]
  }
}
```

Separate file because: Evidence grows fast (dozens per project), roster grows slow (annual). Mixing them would bloat `forge-state.json` and churn git diffs.

---

## Protocol changes — collaboration v3.0 → v3.1

### Standing Rules additions

7. **No citation, no claim.** Any `[FACT]` or `[INFERENCE]` without an Evidence ID gets stripped and replaced with `[UNSUPPORTED — dropped by validator]`. Agent must re-run the query, or downgrade to `[OPINION]`.
8. **Quality floor for GO decisions.** Any GO recommendation citing ≥1 tier-1 (blog) source without tier-3+ backing is flagged `⚠ THIN EVIDENCE` in the deliverable.
9. **Freshness gate.** Evidence beyond the source-type's `stale` threshold is flagged `⏰ STALE`. Beyond `refetch` threshold → `⏰ REFETCH REQUIRED` (must re-query before citing).

### Phase 2 (Intelligence) — rewritten

**Before (v3.0):** Flint routes to Vex, Nyx, Echo, Talon sequentially. Each reasons from training data. Sources are persona-invented.

**After (v3.1):**

1. Flint scores all 4 evidence agents (Vex, Nyx, Echo, Talon) for relevance to the brief (0-3 scale, existing rubric). Activated threshold: score ≥ 2.
2. For each **activated** evidence agent, Flint generates a sub-brief (template below). If only 2 evidence agents are relevant (e.g., a non-Saudi brief skips Nyx), only 2 subagents are dispatched.
3. Flint dispatches the activated sub-briefs **in parallel** using `superpowers:dispatching-parallel-agents`. Fan-out width = number of activated evidence agents (1-4)
3. Each subagent:
   - Loads its persona + Second Brain
   - Generates a query plan (3-8 queries)
   - Executes queries via WebSearch (phase 1) and/or Chrome MCP (phase 2)
   - Builds Evidence objects for each usable result
   - Self-critiques: "Do I have enough evidence to answer my sub-brief?"
   - Returns a structured bundle `{ evidence[], recommendation, confidence, queried_count, quality_avg }`
4. Flint fan-in: dedupes, detects conflicts, persists to `forge-evidence.json`
5. Reasoning agents (Ren, Sable, Atlas, Kira) run Phase 3+ sequentially over the unified Evidence bundle

### Sub-brief template (Flint fills per evidence agent)

```
AGENT: <name> (<domain>)
ORIGINAL BRIEF: <user's full brief>

YOUR SUB-BRIEF:
Primary question: <one sharp question tailored to agent's domain>
Secondary questions:
- <question 2>
- <question 3>

CONSTRAINTS:
- Evidence budget: <N> queries max (default 8)
- Quality floor: <tier> (default 3)
- <domain-specific preferences, e.g., "Saudi-specific sources preferred">

RETURN:
- 5-12 Evidence objects
- Filled framework template from your brain file (e.g., Vex fills Competitive Matrix)
- Confidence 0-1 with reasoning
- Flag gaps you couldn't close
```

### Budgets and guardrails

| Parameter | Default | Purpose |
|---|---|---|
| Total query budget per brief | 40 | Cost cap |
| Per-agent query budget | 8 | Force focus |
| Wall-clock deadline | 4 min | Prevents hanging |
| Chrome MCP concurrent tabs | 5 | Local resource |
| Chrome MCP pages per brief | 15 | Cost cap |
| Kill switch | `evidence_pipes.enabled` in forge-state.json | Global off-switch |

### Failure modes

- **Subagent error or timeout** → Flint proceeds with `⚠ Vex unavailable — proceeding without market data` note. Deliverable explicit about what's missing.
- **Malformed Evidence JSON returned** → validator catches; Flint re-prompts subagent once; on second failure, flag + proceed
- **WebSearch returns nothing for a Saudi-specific query** → agent falls back to persona-reasoned claims **tagged `[OPINION]` not `[FACT]`** (never invent `[FACT]`)
- **Total budget exceeded mid-brief** → Flint stops dispatching new queries, delivers with `⚠ Budget exhausted at 40 queries; some sub-briefs incomplete`

---

## Source quality grading

### Rule-based (primary)

Regex patterns on URL / domain drive the default score. Ships as `tools/evidence_quality.py`:

```python
QUALITY_RULES = [
    # Tier 5
    (r"\.gov\.sa$|\.gov\b|mewa\.|sama\.|mcit\.|stats\.gov\.sa", 5, "primary_government"),
    (r"sec\.gov|esma\.europa\.eu", 5, "primary_government"),

    # Tier 4
    (r"/10-?k/|/10-?q/|/annual-?report/|/earnings/|ir\.[a-z]+\.com", 4, "primary_company"),
    (r"\.com/pricing$|/pricing/?$", 4, "primary_company"),

    # Tier 3
    (r"mckinsey\.com|bcg\.com|bain\.com|gartner\.com|forrester\.com", 3, "analyst"),
    (r"ft\.com|reuters\.com|bloomberg\.com|wsj\.com|wamda\.com|arabnews\.com", 3, "reputable_media"),

    # Tier 2
    (r"play\.google\.com/store|apps\.apple\.com", 2, "user_reviews"),
    (r"reddit\.com|producthunt\.com|news\.ycombinator\.com", 2, "community"),

    # Tier 1
    (r"medium\.com|substack\.com|\.blog", 1, "blog"),
]
```

### User extension

Optional `evidence-quality-overrides.json` at project root, merged on top at load time. Lets non-Python users extend without editing source:

```json
{
  "rules": [
    {"pattern": "westlaw\\.com", "score": 4, "type": "primary_legal"}
  ]
}
```

### LLM sanity check (cheap, batched)

Flint gets one pass over graded Evidence and can **override** any score with a written justification — e.g., "That Medium post is by a known Saudi VC partner, bumping to 3." Override logged in the Evidence object as `quality_override: { from: 1, to: 3, reason: "...", by: "agent-flnt" }`.

---

## Freshness model

Per-source-type staleness + refetch thresholds. Flat 90-day threshold is wrong — Saudi regulatory moves quarterly, pricing moves monthly, demographics annually.

```python
FRESHNESS_RULES = {
    "primary_government":    {"stale": 180, "refetch": 730},   # 6mo / 2y
    "primary_company":       {"stale": 90,  "refetch": 365},   # 3mo / 1y
    "analyst":               {"stale": 365, "refetch": 1095},  # 1y / 3y
    "reputable_media":       {"stale": 180, "refetch": 730},
    "user_reviews":          {"stale": 30,  "refetch": 180},   # Reviews rot fast
    "community":             {"stale": 30,  "refetch": 180},
    "blog":                  {"stale": 90,  "refetch": 365},
}
```

`stale` → flag in output (`⏰ 4 months old`). `refetch` → agent must re-query before citing.

---

## Caching

**Purpose:** prevent the same query hitting the network twice within a brief (or across briefs when fresh).

**Storage:** `assets/.forge-cache/<key>.json`, gitignored.

**Key:** `sha256(normalize(query) + "|" + source_url_if_fetched)`. Normalization: lowercase, strip punctuation, collapse whitespace.

**Entry shape:**

```json
{
  "key": "abc123...",
  "query": "Saudi pet clinics count 2024",
  "results": [<Evidence objects>],
  "fetched_at": "2026-04-16T14:32:00Z",
  "hits": 3
}
```

**TTL rule:** cache entry is valid if `fetched_at` is within the `stale` threshold for the highest-tier source in the cached results. Below-stale → serve from cache with `(cached)` annotation. Stale → agent sees cache but re-queries, then merges fresh data.

**Budget:** soft cap 50MB, LRU eviction. Inspectable via `tools/validator.py --cache-stats` (flag added).

---

## Conflict detection

Two agents citing contradictory claims on the same topic → the conflict surfaces into the War Room (Phase 3) for resolution instead of silently picking one.

### Detection algorithm (v1 — rule-based, deterministic)

1. Group Evidence by topic cluster (lightweight keyword overlap ≥ 0.6)
2. Within a cluster, extract numeric claims from `excerpt` via regex
3. If two numbers differ by > 20% relative → flag `⚠ CONFLICT`
4. Surface both Evidence IDs to Flint with conflict metadata

v2 (out of scope): LLM-based semantic conflict detection for non-numeric contradictions.

### Resolution precedence (locked)

`scope > tier > recency`

- **Scope wins first.** Saudi-specific beats MENA-regional beats global when brief is Saudi — even if global source is newer.
- **Tier wins second.** Tier-5 government beats tier-3 analyst when scope matches.
- **Recency wins third.** Within same scope and tier, newer wins.
- **Unresolvable** → deliverable carries both with `⚠ DISPUTED` and VP decides.

### Dedup

Two agents querying the same URL → single Evidence object, `retrieved_by` becomes an array `["agent-vexx", "agent-nyxx"]`. Prevents double-counting in citation counts.

---

## Rate limiting

- WebSearch: soft cap 40 queries per brief, hard cap 60 (prevents runaway)
- Chrome MCP: max 5 concurrent tabs, max 15 pages per brief
- Global kill switch: `forge-state.json` → `evidence_pipes.enabled: true/false`. Default **true** (pipes on by default — best-in-the-world). Flip to false → v3.0 behavior, zero pipe cost.

---

## Deliverable format — the VP artifact

Every brief in evidence mode ends with an upgraded headline block + Sources Appendix:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚒ THE FORGE — FINAL DELIVERABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT: Pet Healthcare Platform (Saudi)
RECOMMENDATION: GO at 80% confidence

EVIDENCE SUMMARY
  23 queries across 4 agents   |   17 sources cited
  Avg quality: 3.8/5            |   Avg freshness: 14 days
  Conflicts: 2 (see appendix)   |   ⚠ Thin evidence: 0
  Elapsed: 2m 47s                |   Cached hits: 6/23

[... recommendation body with inline citations [ev-7f2a3c] ...]

───────────────────────────────────────────
SOURCES APPENDIX
───────────────────────────────────────────

⭐⭐⭐⭐⭐ Primary Government (4)
  [ev-7f2a3c] MEWA Annual Report 2024 — https://mewa.gov.sa/...
    Retrieved: 2026-04-16 by Nyx | Freshness: 14d
    Cited in: Market Size §, Regulatory §

⭐⭐⭐⭐ Primary Company (3) ...
⭐⭐⭐   Analyst / Media (7) ...
⭐⭐    User / Community (3) ...

⚠ CONFLICTS (2)
  [ev-7f2a3c vs ev-4a2b9c] Market sizing disagreement
    Vex (McKinsey MENA 2023): $510M
    Nyx (MEWA Annual 2024): $340M
    Resolved by: Scope > Recency → MEWA wins
```

**Terminal presentation:** compact (one line per source, expandable).
**Markdown export (for sharing):** full (excerpt, retrieval metadata, cited-in sections). Best-in-the-world means the audit trail is complete when it leaves The Forge.

### Agent contributions get citation-dense

> **Vex — Market Intelligence**
> *Assessment:* Saudi pet care is fragmented with 3 players at scale [ev-1a2b], none tech-first. Pawable raised $4M pre-seed Mar 2025 [ev-2c4d]; remainder is WhatsApp-first clinics [ev-3e5f].
> *Key Insight:* The real competitor isn't a platform — it's clinic WhatsApp [FACT: ev-3e5f]. Platform adoption requires beating free.
> *Recommendation:* Don't position against platforms. Position against clinic ops pain [OPINION].
> *Confidence:* 0.78

---

## UI changes

### Dashboard tab 1 (Mission Control) — Evidence block

New block under the phase bar:
- Queries made: `23 / 40`
- Cache hit rate: `26%`
- Avg source quality: `3.8 ★`
- Freshness heatmap: 4 dots (one per evidence agent), green/amber/red
- Click an agent → drawer opens showing their Evidence list

### Dashboard tab 5 (Sources) — NEW

Dedicated Evidence table:
- Columns: ID, Claim, Source (title + tier stars), Agent, Date, Freshness badge, Cited-in
- Filters: agent / tier / freshness / project / has-conflict
- Search box (claim text + source title)
- Export button: Markdown, CSV, JSON

### Pixel office

- Evidence agents get a new idle-animation variant: pulsing `[!]` bubble above desk while subagent dispatched
- Desk gets subtle green glow on Evidence arrival
- Delight detail: Vex's desk gains a "books" sprite that grows into a stack as her Evidence count across projects rises. Echo's screen flickers through fake app-store review cards.

---

## Validator extension

`tools/validator.py` gains `validate_evidence(evidence_doc, state)`:

- Every `ev-*` ID in `project_evidence_index` must exist in `evidence[]`
- Every `retrieved_by` element must reference an active agent
- `quality_score` ∈ [1,5], `confidence` ∈ [0,1]
- `source_type` must be in the allowed enum
- `source_url` must be a valid URL or start with `local://`
- `retrieved_at` must parse as ISO 8601 UTC
- `signal_tag` ∈ {FACT, INFERENCE, HYPOTHESIS, OPINION}
- New CLI flag: `python3 tools/validator.py --cache-stats` reports cache size, hit rate, LRU victims

Real-file smoke test extended: shipped `forge-evidence.json` (even if empty) must validate cleanly.

---

## SKILL.md updates

- **New section: "Evidence Pipes"** — when to dispatch, when to skip (kill switch / single-agent mode / trivial brief), how sub-briefs are generated
- **Phase 2 rewritten** — parallel dispatch flow, reference `superpowers:dispatching-parallel-agents`
- **Output Format updated** — requires Evidence Summary + Sources Appendix when pipes enabled
- **Quality Standards adds:** *"No citation, no claim. Every `[FACT]` must reference an Evidence ID or be downgraded to `[OPINION]`."*

---

## Test strategy

**TDD mandatory.** Every line of production code preceded by a failing test. Target: **40+ tests** across:

| File | Tests | Covers |
|---|---|---|
| `test_evidence_quality.py` | ~12 | URL → score/type mapping, override JSON merge, Flint override logging |
| `test_evidence_freshness.py` | ~8 | Per-tier stale/refetch thresholds, boundary conditions |
| `test_evidence_cache.py` | ~10 | Key generation, TTL validity, LRU eviction, hit counting |
| `test_evidence_conflict.py` | ~8 | Clustering, numeric divergence detection, resolution precedence |
| `test_evidence_orchestration.py` | ~6 | Sub-brief generation (snapshot tests on Flint's prompts) |
| `test_validator.py` (extended) | +20 | `validate_evidence()` rules, real-file smoke test |

Non-deterministic parts get **fixture-based tests**:
- `tests/fixtures/websearch-responses/saudi-pet-market.json` — canned WebSearch return
- `tests/fixtures/chrome-mcp/app-store-petclinic-reviews.html` — canned DOM snapshots

Deterministic parts (grading, freshness, conflict detection, cache TTL) are pure functions, fully unit-tested.

---

## Success criteria — merge gate

All must be true:

1. **Behavioral:** User gives a brief → 4 evidence agents dispatch in parallel → fan-in merges → deliverable ships with Sources Appendix. Works end-to-end on the real Forge.
2. **Quality:** 40+ new tests green. All existing tests still green (no regressions).
3. **Backward compat:** `evidence_pipes.enabled: false` → v3.0 behavior preserved byte-for-byte.
4. **Cost visibility:** One full brief logs queries, elapsed, cache hits in the deliverable.
5. **Citation enforcement:** `[FACT]` without Evidence ID is stripped by the validator, not merely flagged.
6. **Code review:** `superpowers:code-reviewer` subagent reviews before merge. Critical → blocker. Important → addressed.
7. **Two real briefs:** One synthetic validation brief (Saudi fintech market entry, spec'd below) and one user-supplied real brief run end-to-end. Qualitative: outputs visibly more defensible than v3.0.

### Validation brief 1 (synthetic)

> **Brief:** "I want to launch a neobank targeting Saudi expats remitting to South Asia. Evaluate market, regulatory, user, and growth angles."
>
> Exercises all 4 pipes: Vex (competitive — STC Pay, Barq, urpay), Nyx (SAMA open banking, remittance regulation), Echo (App Store reviews of incumbents), Talon (pricing/fee structures).

### Validation brief 2 (real)

Placeholder for user to supply a live project.

---

## Out of scope (explicit)

- **A+D (memory & calibration):** separate spec after B ships
- **Chrome MCP pipes for all 4 agents:** phase 2 of the implementation plan; MVP is WebSearch-only with Chrome MCP scaffolding in place
- **LLM-based semantic conflict detection:** rule-based numeric only
- **New agents (C — roster expansion):** deferred, separate
- **Domain templates (E — Bar, Clinic, Lab):** deferred

---

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| WebSearch returns low quality for Saudi-specific queries | Quality floor fails → brief blocked | Agent falls back to `[OPINION]`, never invents `[FACT]` |
| Parallel dispatch costs balloon | User bill shock | Budget caps (40/8/4min) + kill switch + cache; every brief reports cost |
| Quality regex misgrades a genuine source | User loses faith | Flint override + user overrides JSON |
| Subagent returns malformed Evidence | Fan-in crashes | Validator on every return; malformed → flag + re-prompt once |
| Chrome MCP brittle to site layout change | Phase 2 breakage | Phase 2 only; fixtures; WebSearch fallback always available |
| `superpowers:dispatching-parallel-agents` API changes | Orchestration breaks | Pin plugin version in package.json |

---

## Implementation sequence (batches — writing-plans will refine)

1. **Evidence object + schema + validator extension** (foundation — nothing else works without this)
2. **Quality grading module** (pure function, easy to TDD)
3. **Freshness module** (pure function)
4. **Cache module** (pure function with filesystem)
5. **Conflict detection module** (pure function)
6. **Orchestration layer** (sub-brief templates, dispatch scaffolding — dry-run first, no real calls)
7. **WebSearch pipes for Vex + Nyx** (real network, canned in tests)
8. **WebSearch pipes for Echo + Talon**
9. **Deliverable format update** (Sources Appendix, Evidence Summary block)
10. **Dashboard Evidence block (tab 1)**
11. **Dashboard Sources tab (tab 5)**
12. **SKILL.md v3.1 rewrite**
13. **Protocol doc v3.1 rewrite**
14. **End-to-end validation brief run (synthetic)**
15. **End-to-end validation brief run (real)**
16. **Code review → address → merge**

Chrome MCP pipes shipped as phase 2 after merge.
