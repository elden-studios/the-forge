# Wave 3 Task 10 Run Report — Saudi EdTech Brief

**Date:** 2026-04-17
**Project ID:** `proj-edtech-ksa`
**Branch:** `v3.2-cabinet-wave3`
**Decision ID:** `dec-736a45fc`
**Purpose:** Final Wave 3 verification — run the v3.2 Cabinet stack end-to-end on a fresh brief (not Saudi PropTech, Neobank, or Pet Health) to prove the visual pipeline (Cabinet Framing → Decision Log → Dashboard Cabinet block → Decisions tab) holds with different-shape data.

---

## The brief

> "Saudi K-12 exam-prep EdTech — a Nafath-verified, Ministry-of-Education-aligned Qudurat/Tahsili percentile-prep platform for Grade 11-12 students preparing for Saudi university admission. Ramadan-aware adaptive engine, Mada/STC Pay/Tamara checkout, Nafath-gated parent dashboard. 3-city pilot: Riyadh/Jeddah/Dammam."

Chosen because it exercises a very different shape than the Saudi PropTech fixture: B2C consumer purchase (not B2B transaction flow), student + parent personas (not a single expat buyer), content-heavy (not transaction-heavy) unit economics, and a competitive landscape already populated by four named incumbents (Abwaab, Noon, Kheyala, Emsat) rather than the two-player PropTech world.

---

## Scope note — simulation mode

This run exercises **Phase 1.5 Cabinet Framing only**. Phases 2-8 (Intelligence, War Room, Architecture, GTM, Challenge, Delivery, Retro) are not exercised here — they are exercised by the live skill session when a real user invokes The Forge on a real brief. The purpose of this task is to prove the Wave 3 visual plumbing works with different-shape Phase 1.5 data than the existing PropTech simulation fixtures, not to re-run Evidence Pipes on a new brief. Evidence Pipes v1 was verified end-to-end in Task 14/15 (see `../2026-04-17-neobank-brief/`).

No WebSearch calls were made. All 5-lens content and 5 pre-mortem items are authored fixtures grounded in publicly-known Saudi market facts (Vision 2030, Madrasati, Nafath, Mada/STC Pay, Ramadan study patterns, Abwaab/Noon competitive landscape) but not individually cited. A live run would populate per-agent Evidence returns in `subagent-returns/`.

---

## What happened — end-to-end

### Phase 1 — Intake (stubbed)

The EdTech brief arrived as a canned `framing_brief` string — the same shape The Forge receives from Flint in a live intake. The brief frames the problem as a category-positioning problem, not a content-volume problem:

> *the current shelf (Abwaab, Noon, Kheyala, Emsat) treats Saudi as a feature of a regional product; none are built Saudi-exam-first, Nafath-verified, or Madrasati-curriculum-aligned.*

### Phase 1.5 — Cabinet Framing (the exercised phase)

`scripts/cabinet_framing_simulate.py --brief edtech` drove the simulation. It:

1. Loaded `cabinet_lenses_edtech.json` (framing_brief + 5 lenses)
2. Loaded `pre_mortem_edtech.json` (5 risks distributed across the 5x5 heatmap)
3. Wrote both onto `forge-tasks.json` via the shipped `write_forge_tasks` function
4. Generated a Cabinet Verdict decision `dec-736a45fc` via `new_decision_id()` + `compute_review_at()`
5. Persisted it through `append_decision_persist()` — which atomically writes `forge-decisions.json`, mirror-writes to `assets/forge-decisions.json`, and updates `project_decision_index["proj-edtech-ksa"]`
6. Ran `validate_project()` — Rule 11 satisfied (cabinet_framing present AND ≥1 decision for current_project)

### Phases 2-8 — not exercised

See "Scope note" above. `subagent-returns/` contains a README explaining which agents would populate in a live run.

---

## The 5-Lens Diagnosis

### Strategic Kernel (Flint) — Rumelt diagnosis/guiding-policy/coherent-action

Diagnosis: the pan-Arab incumbents (Abwaab, Noon) win on content volume but lose on Saudi-exam specificity — Qudurat question patterns, Tahsili science depth, and Madrasati curriculum sequencing are not their core loop. Guiding policy: do not compete on hours-of-video; compete on "verified percentile lift per riyal per semester" for Qudurat/Tahsili. Coherent action: (1) Nafath-gated parent reporting so families trust the progress data, (2) MOE-curriculum mapping as the content spine, (3) Ramadan-aware scheduling as a first-class UX primitive, (4) Riyadh-first launch riding the Vision 2030 human-capital narrative.

### Product Shape (Cade) — Cagan user/outcome/non-goals

User: Grade 11-12 Saudi student preparing for Qudurat + Tahsili, with a parent who pays and expects weekly visibility. Outcome: 10 percentile-point Qudurat lift over a 14-week semester, verified by in-app mock-test scoring vs. SAR 3,500 private-tutor baseline. Non-goals: not a tutoring marketplace (no human matching), not a general Arabic learning app (no KG-6 content), not a competitor to Madrasati (we layer on top), not primarily English language (exams are in Arabic — English is ONE section, not the product).

### Build Class (Helix) — Fournier buy/build/retrofit

Retrofit. Buy the adaptive-learning engine (license Knewton/ALEKS Arabic variant or partner Classera); build the Qudurat/Tahsili item bank + MOE-curriculum mapping + Nafath integration + Mada/STC Pay/Tamara checkout in-house. Retrofit Madrasati SSO if MOE API access is granted in Phase 4. Content authoring is hybrid — 6 Saudi-certified teachers under contract authoring 8,000 Qudurat items + 6,000 Tahsili items in 6 months, reviewed by an MOE curriculum advisor.

### Economic Shape (Prism) — Tunguz unit economics

ARPU SAR 1,800/student/semester (two semesters = SAR 3,600/year — 28% cheaper than the SAR 2,500-5,000 private-tutoring baseline). CAC target < SAR 350 blended (vs. SAR 600 industry baseline in MENA consumer-edtech, achievable via parent-referral + MOE-certified-teacher affiliate program + TikTok/Snap in Arabic). LTV SAR 5,400 assuming 1.5-student-per-family attach and 1.8-semester retention. **LTV/CAC = 15.4 at target, 7.2 at stressed CAC of SAR 750.** Break-even at 4,200 active paying students (~0.4% of KSA's ~1.05M Grade 11-12 cohort). Gross margin 68% after content royalties and payment-gateway fees (Mada 2.1% + STC Pay 1.8% + Tamara 6% on 15% of volume).

### Market Bet (Dune) — Dunford category positioning

Category = "Saudi-exam-specific percentile prep" — not "Arabic e-learning" and not "MENA edtech". The shelf we fight for is the parent's monthly education budget decision, not App Store top charts. Differentiation wedge: (1) Nafath-verified parent dashboard — none of Abwaab/Noon/Kheyala/Emsat have this, (2) Qudurat/Tahsili-first item bank authored by MOE-certified teachers, (3) Ramadan-aware adaptive scheduling (study-load drops 40% during Ramadan and spikes post-Eid — our engine models this, theirs don't). Category narrative: "the SAT-prep moment for Saudi" — there is no Kaplan/Princeton Review of the Saudi exam system yet. Vision 2030 human-capital tailwind makes this a **3-5 year window** before a well-funded incumbent tries to close it.

---

## Pre-Mortem — top 5 risks

| # | Failure mode | L | I | F | Owner | Phase |
|---|---|---|---|---|---|---|
| 1 | **Abwaab launches a Saudi-specific Qudurat vertical** with $10M+ war chest and undercuts ARPU to SAR 900 | 4 | 5 | **20** | Dune | 5 GTM |
| 2 | Nafath API rate limits + Madrasati SSO denial at scale block parent-dashboard onboarding in peak Sept/Jan enrollment windows | 4 | 4 | **16** | Helix | 4 Arch |
| 3 | Saudi parents continue to prefer human private tutoring for the perceived "wasta" and accountability | 3 | 5 | **15** | Cade | 7 Delivery |
| 4 | Blended CAC climbs above SAR 500 due to TikTok/Snap CPM inflation in Ramadan + parent-referral loop underperforming — LTV/CAC drops below 6 | 3 | 4 | **12** | Prism | 6 Challenge |
| 5 | MOE policy shift mandates all K-12 test prep flow through Madrasati, invalidating standalone-app distribution | 2 | 5 | **10** | Nyxx | 5 GTM |

**Heatmap distribution:** risks populate four distinct cells — (4,5), (4,4), (3,5), (3,4), (2,5) — not clumped in one corner. This is what the Dashboard heatmap renders as five differently-placed markers across the 5×5 grid.

---

## Cabinet Verdict

**Decision:** `dec-736a45fc` — GO at 75% confidence — Saudi K-12 Exam-Prep EdTech (simulation)

**Selected alternative:** GO with Riyadh-first pilot + Mada/STC Pay/Tamara checkout + 6-teacher content team

**Rejected alternatives:**
- NO-GO — rejected because the Vision 2030 window is open now and incumbents are not Saudi-exam-first. Window estimated at 18-24 months.
- ITERATE with Qudurat-only before Tahsili — rejected because Saudi parents buy the full-semester package, not the half. Launching Qudurat-only creates a credibility gap vs. Abwaab's full-stack offering.

**Decided by:** Cade (agent-cade)

**Dissent:** Prism (agent-prsm) — CAC at SAR 350 target is aggressive; Abwaab's well-funded response could compress LTV/CAC below 6 before break-even. Dune (agent-dune) concurs the 18-24 month category-defining window is tight.

**Reversibility:** Type 1 (reversible — a pilot city can be shut down, a checkout provider swapped, a content partnership unwound). Review scheduled for **2026-07-16** (90 days).

**Related evidence:** none yet (simulation mode — live run would populate from Phase 2 dispatch).

**Status:** open

---

## Metrics

| Metric | Value |
|---|---|
| Brief | Saudi K-12 exam-prep EdTech |
| Project ID | `proj-edtech-ksa` |
| Mode | simulation |
| Cabinet lenses | 5 / 5 |
| Pre-mortem items | 5 / 5 |
| Decisions written | 1 (`dec-736a45fc`) |
| Validator Rule 11 | satisfied |
| Elapsed seconds | 0 (in-process simulation) |
| Tests after | 356 / 356 green |

---

## Dashboard verification — what an operator sees on Mission Control

**Mission Control tab — Cabinet block** (Wave 3 Task 5):
- Header: "Saudi K-12 Exam-Prep EdTech (simulation)" + 75% confidence pill
- 5 lens cards rendered in a 1×5 row (mobile stacks to 5×1): Strategic Kernel (Flint), Product Shape (Cade), Build Class (Helix), Economic Shape (Prism), Market Bet (Dune) — each with the authored content as the card body and a "view full" expander
- Verdict strip beneath: **GO 75%** — "Riyadh-first pilot + Mada/STC Pay/Tamara checkout + 6-teacher content team" — decided by Cade, dissent Prism + Dune
- Pre-mortem heatmap: 5×5 grid with 5 markers placed at (4,5), (4,4), (3,5), (3,4), (2,5). Top-right cluster is dense; bottom-left is empty. Each marker is clickable → opens the full failure_mode + mitigation_phase drawer
- "Review at 2026-07-16" countdown pill

**Decisions tab** (Wave 3 Task 7+8):
- One new row at top — `dec-736a45fc` — sorted by `review_at` ascending
- Filter chips: reversibility=Type 1, decider=Cade, project=proj-edtech-ksa
- Search for "Qudurat" → 1 hit (this row)
- Export buttons render MD / CSV / JSON downloads that include the full alternatives_considered array, dissent reason, and review_at ISO timestamp

**Tab-indicator** (Wave 3 Foundation review fix I2): clean swap with no first-paint flicker between Mission Control and Decisions. Mirror-write logging (I4) confirms both `forge-decisions.json` and `assets/forge-decisions.json` received the new decision atomically.

---

## Validator output

```
$ python3 tools/validator.py
OK — /Users/lbazerbashi/Elden Studios/the-forge passed all validation checks
```

Standing Rule 11 — "Every active project must have cabinet_framing AND at least one decision in the Decision Log" — is satisfied for `proj-edtech-ksa`:
- `forge-tasks.json.cabinet_framing` present with framing_brief + all 5 lenses populated
- `forge-decisions.json.project_decision_index["proj-edtech-ksa"]` = `["dec-736a45fc"]` (1 decision)
- Mirror file `assets/forge-decisions.json` is byte-synced (I4 mirror-write logging confirms)

---

## Qualitative observations

### What the EdTech brief surfaced that PropTech did not

1. **Heatmap variety.** PropTech fixtures clustered in the upper-right (two F=16 risks and one F=15 — all high-likelihood, high-impact). The EdTech pre-mortem spreads across four distinct heatmap cells, exercising the grid renderer more thoroughly. One risk (Abwaab counter-launch) sits at the maximum F=20 — the PropTech fixtures never hit F=20. If there is a top-right color-coding edge case, this run would catch it.

2. **Two-dissenter Verdict.** The PropTech Verdict has one dissenter (Prism). The EdTech Verdict has two (Prism + Dune). This exercises the dissent-list rendering and confirms the UI handles >1 dissenter without truncation.

3. **Project-ID switching.** `current_project` moves from `proj-simulation` to `proj-edtech-ksa`. `project_decision_index` now contains two keys. The Decisions-tab project filter (Task 7) needs to handle the new key correctly — filtering to proj-edtech-ksa should show 1 decision; filtering to proj-simulation should show 3.

4. **Longer alternatives_considered prose.** The EdTech alternatives are longer than the PropTech ones ("GO with Riyadh-first pilot + Mada/STC Pay/Tamara checkout + 6-teacher content team" vs. "GO with Riyadh-only pilot"). This exercises the alternatives-list wrapping in both the dashboard card and the CSV/JSON export.

### What a live run would add

- Per-agent Evidence returns in `subagent-returns/` (Phase 2)
- Sources Appendix in `sources-compact.txt` with tier-grouped citations for every numeric claim in the 5 lenses (Vision 2030 FSDP numbers, Abwaab funding, STC Pay fee schedules, Mada interchange rates)
- Non-zero `elapsed_sec` and `total_queries` in `stats.json`
- A `conflicts.json` with any numeric divergences the rule-based detector surfaces between Vex (competitive intel) and Prism (unit economics)

None of these are in scope for Task 10. They are in scope for the next live skill session when a real operator invokes The Forge on a real EdTech brief.

---

## Next

Wave 3 Task 10 is complete. Per the Wave 3 roadmap the remaining step is:

- **Wave 3 finish-branch ceremony** — merge `v3.2-cabinet-wave3` into `main` (gate: all tests green, validator OK on a non-PropTech brief — both now confirmed).

---

## Artifacts in this run dir

- `README.md` — this file
- `deliverable.md` — the consolidated Cabinet Verdict deliverable
- `run_pipeline.py` — reproducible driver (invokes `scripts/cabinet_framing_simulate.py --brief edtech`)
- `stats.json` — machine-readable run metrics
- `conflicts.json` — `{"conflicts": []}` (nothing to surface in simulation mode)
- `summary-block.txt` — one-line summary for dashboards
- `sources-compact.txt` — note on what a live run's sources file would contain
- `subagent-returns/README.md` — note on what a live run would populate here

---

## Reproduction

```bash
cd /Users/lbazerbashi/Elden\ Studios/the-forge
python3 scripts/cabinet_framing_simulate.py --brief edtech
python3 tools/validator.py
# Or equivalently:
python3 docs/superpowers/runs/2026-04-17-saudi-edtech-brief/run_pipeline.py
```

The driver is idempotent in shape (writes the same cabinet_framing + pre_mortem blocks each time) but generates a new `dec-xxxxxxxx` on each run (UUID-derived). `append_decision_persist` appends rather than replaces — re-running will accumulate additional decisions against `proj-edtech-ksa`, matching the PropTech fixture behavior.
