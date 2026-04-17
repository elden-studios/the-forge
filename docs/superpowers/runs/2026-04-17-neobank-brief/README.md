# Task 14 Run Report — Saudi Expat Neobank Brief

**Date:** 2026-04-17
**Project ID:** `proj-003`
**Branch:** `evidence-pipes-v1`
**Purpose:** First live end-to-end exercise of Evidence Pipes v1 — the synthetic validation brief from the spec.

---

## Post-review update (Task 15)

**Task 15 fix commit:** `dd6e7f2`

The second formal Code Review Gate blocked the merge and surfaced **2 Critical bugs** that were invisible in the original report:

### C1 — `strip_unsupported_claims` regex gap (Silent no-op on real output)

The original `_CLAIM_RE` only matched `[FACT]` / `[FACT: ev-X]` / `[INFERENCE]` forms. All four agents' actual prose used **naked bracket citations** — `[ev-a3f1c2d7, ev-b7e90014, ev-f8a1c9e6]` — which the regex never touched. Standing Rule 7 enforcement was a complete no-op on the Task 14 deliverable: every naked cite passed through regardless of whether the ID existed.

**What the original report claimed:** "strip_unsupported_claims() ran over all four agent recommendations against the 35 valid Evidence IDs — no claims stripped."

**What was actually true:** The function ran, found zero `[FACT]`/`[INFERENCE]` forms to match, and returned the text unchanged — including the two orphan IDs described below. It was not enforcing anything.

**Fix:** `strip_unsupported_claims` now handles both tagged and naked forms. Mixed-validity naked brackets rewrite inline — valid IDs survive, invalid ones become `⚠ <id> unsupported`.

### C2 — `merge_returns` dedup key was `source_url` alone (Silent evidence loss)

The old dedup keyed on `source_url`. Nyx cited two different excerpts from `rulebook.sama.gov.sa/en/3-2-domestic-and-international-money-transfers` (ev-b7e90014 and ev-f8a1c9e6 — two distinct AML claims). Echo cited two different complaints from `barq-finance.pissedconsumer.com/review.html` (ev-c3f5e218 and ev-d4a6f329). In both cases the second Evidence was silently dropped, producing 35 instead of 37 Evidence — and leaving the agents' prose citing IDs that no longer existed in the merged bundle.

**What the original report said:** "37 → 35 unique Evidence (2 merged out — both were the Barq pissedconsumer.com URL appearing in Echo's return, and one SAMA rulebook URL Nyx cited twice with different excerpts)" and listed this as a "rough edge" rather than a bug. This was wrong — distinct excerpts from the same page are distinct claims; collapsing them is data loss that orphans citations.

**Fix:** Dedup key changed to `(source_url, excerpt)`. Only genuinely-identical (URL + excerpt) Evidence collapse.

### Post-fix metrics

| Metric | First run (buggy) | Re-run (Task 15) |
|---|---|---|
| Evidence after dedup | 35 | **37** |
| Orphan citations in deliverable | 2 (ev-f8a1c9e6, ev-d4a6f329) | **0** |
| Standing Rule 7 actually enforced | No (silent no-op) | **Yes** |
| Tests | 142 | **151** (+9 regression tests) |

The re-run pipeline was executed after landing `dd6e7f2`. All 37 citations in the new deliverable resolve to valid Evidence objects. No `⚠ unsupported` markers were emitted — all IDs survived because the C2 fix means none were orphaned.

---

---

## The brief

> "Launch a mobile-first neobank targeting Saudi expats remitting to South Asia. Evaluate market, regulatory, user, and growth angles."

Chosen from the spec because it exercises all four evidence agents: market (Vex), regulatory (Nyx), user (Echo), growth (Talon).

---

## What happened — end-to-end

### 1. Phase 2 dispatch

All four evidence agents scored ≥ 2 on relevance and were activated in parallel:

| Agent | Score | Keywords that hit |
|---|---|---|
| Vex (Market Intel) | 3 | market, competitive, competitor |
| Nyx (Saudi Market) | 2 | saudi |
| Echo (User Research) | 2 | user |
| Talon (Growth) | 2 | growth, launch, gtm |

Four subagents dispatched simultaneously via Claude's `Agent` tool (model: sonnet). Each received its persona-adjusted sub-brief from `evidence_orchestrator.generate_sub_brief()`, a budget of 8 WebSearch queries, and a strict JSON return contract matching the Evidence schema.

### 2. Subagent returns

All four returned structured JSON envelopes within a few minutes. Raw returns archived at `./subagent-returns/{vex,nyx,echo,talon}.json`.

| Agent | Evidence | Queries | Subagent confidence | Subagent quality_avg | Gaps flagged |
|---|---|---|---|---|---|
| Vex | 10 | 8 | 0.78 | 3.2 | 6 |
| Nyx | 9 | 8 | 0.82 | **4.78** | 5 |
| Echo | 8 | 8 | 0.82 | 2.5 | 5 |
| Talon | 10 | 8 | 0.71 | 3.5 | 4 |
| **Total** | **37** | **32** | — | — | **20** |

Nyx hit primary-government SAMA rulebook URLs at tier-5 quality — that's the Saudi market specialist doing their job. Echo legitimately pulled tier-2 user_reviews (App Store, Play Store, pissedconsumer) because that's where user pain-point signal lives.

### 3. Fan-in merge

`evidence_orchestrator.merge_returns()` deduped by `(source_url, excerpt)` (post-Task 15 fix):
- 37 → **37 unique Evidence** (0 merged out — all items have distinct (URL, excerpt) pairs)
- `retrieved_by` arrays grew on merged evidence (none across agents this run — all overlaps were within a single agent)

> **Note:** The first run (before Task 15 fixes) produced 35 after silently dropping ev-f8a1c9e6 and ev-d4a6f329 — distinct excerpts from shared URLs. See "Post-review update (Task 15)" above.

### 4. Validation

`validator.validate_evidence()` on the merged bundle + current `forge-state.json` → **✅ passed**. All 37 Evidence objects well-formed:
- IDs match `ev-[0-9a-f]{8}` regex
- `source_type` values all in the allowed enum
- `quality_score` 1-5, `confidence` 0-1
- `retrieved_at` parses as ISO 8601 UTC
- `retrieved_by` references only active agents

### 5. Persistence

`evidence_orchestrator.append_evidence("proj-003", bundle, "forge-evidence.json")`:
- Atomic write to `/forge-evidence.json` at repo root
- Mirror write to `/assets/forge-evidence.json` (confirmed sync — both files carry 37 Evidence)
- `project_evidence_index["proj-003"]` populated with all 37 IDs

### 6. Conflict detection

`evidence_conflict.detect_conflicts(bundle["evidence"])` — **0 numerical conflicts** surfaced. Subagents pulled aligned figures (e.g., all cited $38B Saudi outflows consistent within ~0.5%). Rule-based v1 (20% divergence threshold) did its job; no false positives.

### 7. Deliverable render

- `evidence_appendix.render_summary_block` → the EVIDENCE SUMMARY box above the recommendation
- `evidence_appendix.render_compact` → tier-grouped one-line-per-source for terminal
- `evidence_appendix.render_markdown` → full appendix with excerpts, retrieval dates, agent attribution for sharing

Full deliverable at `./deliverable.md`. Additional artifacts: `summary-block.txt`, `sources-compact.txt`, `conflicts.json`, `stats.json`, `run_pipeline.py` (the driver).

### 8. Citation enforcement

`strip_unsupported_claims()` ran over all four agent recommendations against the 37 valid Evidence IDs — **no claims stripped**. All citations in the agents' prose (which use naked `[ev-X, ev-Y]` bracket form) resolved to real Evidence objects.

> **Correction from first run:** The original report claimed enforcement passed with "no claims stripped" — which was literally true but misleading. The C1 regex gap meant the function was not examining naked bracket forms at all; it only matched `[FACT: ev-X]` tagged forms (which agents don't use). The post-Task 15 fix now enforces both forms. On the re-run, no markers were emitted because the C2 fix means no IDs are orphaned — all 37 cited IDs are present in the bundle.

---

## Evidence Summary (rendered block)

```
EVIDENCE SUMMARY
  32 queries across 4 agents   |   37 sources cited
  Avg quality: 3.5/5              |   Conflicts: 0
  ⚠ Thin evidence: 0                |   Cache hits: 0/32
  Elapsed: 0s
```

> Note: `Elapsed: 0s` reflects only the fan-in pipeline wall-clock (the Python orchestrator post-returns). The actual parallel dispatch of the 4 subagents took roughly 3-4 minutes of real time — each subagent made 8 WebSearch queries serially. Future versions should instrument this.

---

## What the dashboard looks like with real evidence

**Mission Control tab — Evidence block:**
- 37 ITEMS badge (was 35 before Task 15 fixes)
- Queries: 32 / 40 (under budget)
- Sources cited: 37
- Avg quality: 3.5 ★
- Freshness dots: all four GREEN (Vex, Nyx, Echo, Talon all contributed fresh evidence)

**Sources tab (new in Task 12):**
- 37 rows with ID, Claim, Source (clickable, scheme-validated), Tier stars, Agent, Retrieved date
- Filter to Echo → 8 results (user signal, mix of ⭐⭐ app stores + ⭐⭐⭐ reputable media — was 7 before ev-d4a6f329 was restored by C2 fix)
- Export buttons render MD / CSV / JSON downloads
- Result count updates live as filters change

All UX confirmed via Claude Preview MCP screenshots.

---

## Qualitative comparison vs. v3.0

### What v3.0 would have produced
A five-page recommendation grounded in the personas' training-data intuitions. Numbers like "$38B outflow" and "Barq hit 1M users" would appear, but with no traceability — the honest answer to "where did that come from?" would be "the persona said so."

### What v3.1 with pipes produced
Every numeric claim in every agent's prose cites an Evidence ID. Every Evidence ID resolves to a real URL, a real excerpt, and a quality tier. A VP reading the deliverable can click through to the MEWA report, the SAMA rulebook, the Arab News piece, the App Store review — and verify the claim themselves.

**That's the entire point of the feature.** This run shows it working.

### Specific wins worth highlighting
- **Nyx reached primary-government tier-5 sources** (SAMA rulebook URLs, Vision 2030 FSDP annual report PDF). Not just "MEWA says" — a citable, re-fetchable path.
- **Echo found the $1.3B Bangladeshi worker loss figure** from The Business Standard — a real number a VP can defend in a board meeting.
- **The rivalry showed up in the output.** Echo's recommendation paragraph says *"Vex's likely assumption that 'users just want speed' is wrong — cost is the primary complaint volume driver."* Vex's own recommendation prioritized competitive pricing. The friction is visible and grounded in evidence, which is exactly what the v3.0 protocol says rivalries should do.
- **All agents flagged honest gaps.** Nyx couldn't reach public capital-threshold documentation; Talon couldn't find a MENA-specific CAC benchmark; Echo couldn't scrape Reddit. These gaps are in the JSON envelopes, not hidden. In v3.0 they'd have been invisible.

### Rough edges discovered
1. **Source URL dedup can swallow distinct excerpts from the same page.** Echo cited two different user complaints on the same Barq pissedconsumer URL (ev-c3f5e218 and ev-d4a6f329); fan-in kept only one. The other excerpt is gone from the final deliverable. Not a bug (spec'd behavior) but worth documenting as an I-level finding — v2 could key on `(source_url, excerpt_hash)` or `retrieved_by + source_url`.
2. **No wall-clock instrumentation** on parallel dispatch. Elapsed timer in `run_pipeline.py` is post-dispatch only. Real "how long did fan-out take" isn't captured.
3. **Subagent-reported `quality_avg` drifts from real average** (Vex said 3.2, actual 3.4; Nyx said 4.78, actual 4.78; Echo said 2.5, actual 2.5; Talon said 3.5, actual 3.6). The orchestrator should compute this post-hoc from the actual `quality_score` field — not trust the subagent's self-reported number, which is a rough estimate. Low priority.
4. **UI tab-indicator visual bug** (noted in earlier review): when Sources tab is clicked, the Mission Control underline briefly persists. Panel swap works; cosmetic only.

---

## Metrics vs. success criteria

| Spec criterion | Target | First run (pre-Task 15) | Post-Task 15 re-run | Status |
|---|---|---|---|---|
| Brief dispatches in parallel | All relevant agents | 4/4 activated, all parallel | Same | ✅ |
| Evidence schema validates | 100% | 35/35 pass validator | 37/37 pass validator | ✅ |
| Sources Appendix renders | Deliverable format | `render_compact` + `render_markdown` output | Same | ✅ |
| Dashboard reflects real evidence | Live on localhost | 35 ITEMS badge | 37 ITEMS badge | ✅ |
| No existing tests broken | 142/142 | 142/142 green | 151/151 green | ✅ |
| Real project validator pass | OK | OK | OK | ✅ |
| `forge-evidence.json` + mirror in sync | Same content | Both had 35 Evidence | Both have 37 Evidence | ✅ |
| No unsupported citation in output | 0 orphans | **FAILED** — 2 orphan IDs (ev-f8a1c9e6, ev-d4a6f329); enforcement was a regex no-op | **0 orphans — enforcement working** | ✅ (fixed in Task 15) |
| Budgets respected | ≤ 40 queries | 32 | 32 | ✅ |
| Cost visibility | Per-run metrics | `stats.json` emitted | `stats.json` emitted | ✅ |

**Nine of ten criteria met in the first run. All ten met after Task 15 fixes.**

The "No unsupported citation" criterion failed the first run due to C1 (regex gap silencing enforcement) and C2 (dedup collision orphaning IDs). Both were caught by the formal Code Review Gate, not by the original test suite.

---

## Next

Task 14 is complete. The foundation + orchestration + UI all behave correctly on a real brief. Next ceremony step per PLAN.md:

- **🛑 Second Code Review Gate** — invoke `superpowers:requesting-code-review` with the run-document path as context so the reviewer can evaluate actual output quality, not just code diffs.
- After review → Task 15 (address findings) → Task 16 (finish-branch ceremony).

---

## Artifacts in this run dir

- `README.md` — this file
- `run_pipeline.py` — reproducible driver
- `subagent-returns/` — raw JSON from each of the 4 evidence agents
- `deliverable.md` — full Markdown deliverable with Sources Appendix
- `summary-block.txt` — Evidence Summary for terminal output
- `sources-compact.txt` — compact tier-grouped source list
- `conflicts.json` — detected conflicts (empty this run)
- `stats.json` — run metrics for programmatic use
