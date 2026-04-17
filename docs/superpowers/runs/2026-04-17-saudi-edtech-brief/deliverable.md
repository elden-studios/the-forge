# Cabinet Verdict — proj-edtech-ksa

**Project:** Saudi K-12 Exam-Prep EdTech (simulation)
**Decision ID:** `dec-736a45fc`
**Decided at:** 2026-04-17T15:41:26Z
**Review at:** 2026-07-16T15:41:26Z (90 days, Type 1 reversibility)
**Phase:** 1.5 — Cabinet Framing
**Mode:** simulation (Phase 1.5 only — Phases 2-8 not exercised)

---

## Framing Brief

> Saudi K-12 students preparing for GAT/SAAT (Qudurat/Tahsili) need Nafath-verified, Ministry-of-Education-aligned practice at scale — not generic pan-Arab video libraries. Diagnosis: the current shelf (Abwaab, Noon, Kheyala, Emsat) treats Saudi as a feature of a regional product; none are built Saudi-exam-first, Nafath-verified, or Madrasati-curriculum-aligned. Guiding policy: become the only platform a Saudi parent trusts to move a student's Qudurat percentile in one semester. Coherent action: Ramadan-aware adaptive engine, Mada/STC Pay/Tamara checkout, Nafath-gated parent dashboard, 3-city pilot (Riyadh/Jeddah/Dammam) with certified MOE-curriculum teachers.

---

## Verdict

**GO at 75% confidence** — launch Riyadh-first pilot + Mada/STC Pay/Tamara checkout + 6-teacher content team, targeting 4,200 paying students by end of Year 2 to hit break-even.

### Decider
**Cade** (agent-cade) — Product lens. The strategic clarity of the 5 lenses + the dissent quality give me enough signal to commit. The window is open and the differentiation wedge is real.

### Dissent
- **Prism** (agent-prsm) — *"CAC at SAR 350 target is aggressive. MENA consumer-edtech baseline is SAR 600. If we miss and land at SAR 750 stressed, LTV/CAC drops to 7.2 — still viable but thin. If we miss harder and land at SAR 1,000+, we don't have runway to recover. Stage-gate the pilot on blended CAC trending to < SAR 450 within 90 days of Riyadh launch; fail fast to SAR 2,400 ARPU if CAC holds."*
- **Dune** (agent-dune) — *"Concurring dissent. The 18-24 month category-defining window is real but so is Abwaab's $10M+ war chest. If they launch a Saudi-specific vertical before we hit 10K paying students with brand recognition, the shelf-space fight becomes a funding fight we lose. Recommend a defensive PR cadence + MOE teacher exclusivity clauses from day one."*

### Alternatives considered
1. **NO-GO** — rejected because the Vision 2030 human-capital narrative is driving real MOE budget toward private-sector augmentation. Timing window is open now; delaying 12 months cedes the category-defining moment.
2. **ITERATE with Qudurat-only before Tahsili** — rejected because Saudi parents buy the full-semester package, not the half. Launching Qudurat-only creates a credibility gap vs. Abwaab's full-stack offering and signals a partial commitment.
3. **GO with Riyadh-first pilot + Mada/STC Pay/Tamara checkout + 6-teacher content team** — **SELECTED (this decision)**.

---

## Five Signature Artifacts (Phase 1.5 outputs)

### 1. Strategic Kernel — Flint (Rumelt)

**Diagnosis**: the pan-Arab incumbents (Abwaab, Noon) win on content volume but lose on Saudi-exam specificity — Qudurat question patterns, Tahsili science depth, and Madrasati curriculum sequencing are not their core loop. The market looks contested at first glance (four incumbents) but is actually unserved at the Saudi-exam-first layer.

**Guiding policy**: do not compete on hours-of-video. Compete on "verified percentile lift per riyal per semester" for Qudurat/Tahsili — a metric the incumbents cannot claim because they do not measure it.

**Coherent action**: (1) Nafath-gated parent reporting so families trust the progress data, (2) MOE-curriculum mapping as the content spine, not generic math/science topics, (3) Ramadan-aware scheduling as a first-class UX primitive, (4) Riyadh-first launch riding the Vision 2030 human-capital narrative.

### 2. Product Shape — Cade (Cagan)

**User**: Grade 11-12 Saudi student preparing for Qudurat + Tahsili, with a parent who pays and expects weekly visibility. Two-sided purchase: student is the user, parent is the buyer. Both need their own UX.

**Outcome**: 10 percentile-point Qudurat lift over a 14-week semester, verified by in-app mock-test scoring vs. SAR 3,500 private-tutor baseline. This is the claim the product must be able to defend with data by Month 6 of the pilot.

**Non-goals**: not a tutoring marketplace (no human matching — that's a different unit-economics model), not a general Arabic learning app (no KG-6 content — different funnel), not a competitor to Madrasati (we layer on top via SSO, not replace — this is a regulatory non-negotiable), not primarily English language (Qudurat is in Arabic; English is one section, not the product).

### 3. Build Class — Helix (Fournier)

**Classification**: Retrofit. We are not building an adaptive engine from scratch (10+ engineer-years) and we are not buying a white-label platform (no Saudi-exam differentiation).

**Buy**: the adaptive-learning engine itself. License Knewton/ALEKS Arabic variant or partner with Classera. ~SAR 2M upfront + royalty.

**Build**: (a) Qudurat/Tahsili item bank — 8,000 Qudurat + 6,000 Tahsili items authored by 6 Saudi-certified teachers over 6 months (SAR 1.8M content budget), (b) MOE-curriculum sequencing layer on top of the licensed engine, (c) Nafath integration for parent-dashboard KYC, (d) Mada + STC Pay + Tamara checkout in one Saudi-first payment orchestrator.

**Retrofit**: Madrasati SSO if MOE API access is granted in Phase 4. Non-blocker if denied — Nafath alone is sufficient for parent verification.

### 4. Economic Shape — Prism (Tunguz)

| Metric | Target | Stressed |
|---|---|---|
| ARPU / student / semester | SAR 1,800 | SAR 1,500 |
| ARPU / student / year | SAR 3,600 | SAR 3,000 |
| Private-tutor baseline | SAR 2,500-5,000/year | — |
| Blended CAC | < SAR 350 | SAR 750 |
| LTV (1.5 students/family × 1.8 sem retention) | SAR 5,400 | SAR 4,500 |
| **LTV/CAC** | **15.4** | **6.0** |
| Gross margin | 68% | 62% |
| Break-even | 4,200 paying students | 6,500 paying students |
| Addressable base (Grade 11-12 KSA) | ~1.05M | — |
| Break-even as % of TAM | 0.4% | 0.6% |

**Payment mix assumption**: Mada 55% (2.1% MDR), STC Pay 30% (1.8% MDR), Tamara 15% (6% MDR on BNPL volume). Blended payment cost ≈ 2.8%.

**Unit-econ sensitivity**: the plan holds at stressed CAC SAR 750; it breaks at CAC > SAR 1,000 because LTV/CAC falls below 4.5. **This is the dissent.** Prism's stage-gate: re-evaluate pricing ceiling if Riyadh pilot CAC is not trending to < SAR 450 by Day 90.

### 5. Market Bet — Dune (Dunford)

**Category**: "Saudi-exam-specific percentile prep" — not "Arabic e-learning" and not "MENA edtech". The category name matters because it determines the shelf we fight for — the parent's monthly education budget, not App Store top charts.

**Direct competition analysis**:
| Competitor | Core model | Saudi-exam-first? | Nafath parent dash? | Madrasati SSO? |
|---|---|---|---|---|
| Abwaab | Pan-Arab, Jordan HQ | No | No | No |
| Noon | Egypt-led live-class | No | No | No |
| Kheyala | Local Saudi, pre-Nafath gen | Partial | No | No |
| Emsat | UAE EmSAT-first, Saudi port | No | No | No |
| **Us** | **Saudi-exam-first, KSA-native** | **Yes** | **Yes** | **Yes (if granted)** |

**Differentiation wedge** (3 uncopyable-in-12-months advantages):
1. Nafath-verified parent dashboard — pan-Arab incumbents cannot build this without a Saudi entity and SAMA-adjacent compliance posture
2. Qudurat/Tahsili-first item bank authored by MOE-certified teachers with curriculum-advisor review — takes 6 months minimum and requires relationships
3. Ramadan-aware adaptive scheduling — study-load drops 40% during Ramadan and spikes post-Eid. Incumbents treat the calendar as MENA-generic; we treat it as a first-class product primitive

**Category narrative**: "the SAT-prep moment for Saudi." There is no Kaplan/Princeton Review of the Saudi exam system yet. Vision 2030 human-capital tailwind makes this a **3-5 year window** before a well-funded incumbent (Abwaab, or a new entrant backed by PIF-adjacent funding) tries to close it.

---

## Pre-Mortem — top 5 risks

| # | Failure mode | L | I | F | Owner | Phase | Mitigation |
|---|---|---|---|---|---|---|---|
| 1 | Abwaab launches Saudi-specific Qudurat vertical with $10M+ war chest, undercuts ARPU to SAR 900 | 4 | 5 | **20** | Dune | 5 GTM | Defensive PR cadence + MOE teacher exclusivity clauses from Day 1; price-match posture prepared but not triggered until signal |
| 2 | Nafath API rate limits + Madrasati SSO denial at scale block onboarding in peak Sept/Jan windows | 4 | 4 | **16** | Helix | 4 Arch | Pre-flight Nafath load test at 10× expected peak; Madrasati SSO optional not required; background queue for Nafath verification |
| 3 | Saudi parents continue to prefer human private tutoring for perceived "wasta" and accountability | 3 | 5 | **15** | Cade | 7 Delivery | Hybrid tier (SAR 2,400/sem) with one teacher check-in per fortnight; parent testimonial flywheel from Riyadh pilot cohort |
| 4 | Blended CAC climbs above SAR 500 in Ramadan CPM inflation + underperforming referral loop — LTV/CAC drops < 6 | 3 | 4 | **12** | Prism | 6 Challenge | 90-day CAC stage-gate (see Prism dissent); Ramadan-budget shift to content marketing / MOE-teacher affiliates |
| 5 | MOE policy shift mandates all K-12 test prep flow through Madrasati, invalidating standalone-app distribution | 2 | 5 | **10** | Nyxx | 5 GTM | Engage MOE advisory board pre-launch; architect content layer to plug into Madrasati as a marketplace partner if mandated |

---

## Decision Log entry

```json
{
  "id": "dec-736a45fc",
  "title": "GO at 75% confidence — Saudi K-12 Exam-Prep EdTech (simulation)",
  "context": "Phase 1.5 Cabinet Framing produced a 5-lens diagnosis for a Saudi Qudurat/Tahsili percentile-prep platform. 5 pre-mortem risks distributed across the 5x5 heatmap (top: Abwaab Saudi-vertical counter-launch F=20, Nafath+Madrasati SSO rate limits F=16, Cultural preference for human tutoring F=15). Cabinet reached majority GO with Riyadh-first pilot; Prism dissented on CAC sensitivity, Dune flagged category-defining window is 18-24 months.",
  "alternatives_considered": [
    "NO-GO (reject: Vision 2030 window is open now, incumbents are not Saudi-exam-first)",
    "ITERATE with Qudurat-only before Tahsili (reject: parents buy the full-semester package, not the half)",
    "GO with Riyadh-first pilot + Mada/STC Pay/Tamara checkout + 6-teacher content team (selected — this decision)"
  ],
  "decided_by": "agent-cade",
  "dissenting": ["agent-prsm", "agent-dune"],
  "dissent_reason": "CAC at SAR 350 target is aggressive; Abwaab's well-funded response could compress LTV/CAC below 6 before break-even. Dune concurs the 18-24 month category-defining window is tight.",
  "decided_at": "2026-04-17T15:41:26Z",
  "reversibility": "type_1",
  "review_at": "2026-07-16T15:41:26Z",
  "project_id": "proj-edtech-ksa",
  "related_evidence": [],
  "status": "open"
}
```

---

## Sources Appendix

_Simulation mode — no WebSearch queries made. All 5-lens propositions and 5 pre-mortem risks are authored fixtures grounded in publicly-known Saudi market facts but not individually cited._

In a live run, Phase 2 (Intelligence) would dispatch Vex / Nyx / Echo / Talon in parallel against this framing_brief and populate a Sources Appendix per the Evidence Pipes v1 pattern. Representative queries a live run would make:

- **Vex (Market Intel)**: "Abwaab funding rounds 2024 2025 total raised", "Noon Egypt edtech Saudi market share", "Saudi private tutoring market size SAR annual", "Kheyala Saudi edtech ARR 2025"
- **Nyx (Saudi Market)**: "Madrasati K-12 platform API third-party access 2026", "Nafath rate limits documentation for fintech edtech apps", "Saudi Ministry of Education Qudurat digital prep policy 2025", "Vision 2030 Human Capability Development Program education budget"
- **Echo (User Research)**: "Saudi parent purchase decision private tutoring decision criteria", "Qudurat Tahsili student stress pain points 2025", "Ramadan study habits Saudi high school students"
- **Talon (Growth)**: "Saudi TikTok CPM MENA consumer apps 2025", "MENA edtech CAC benchmarks Abwaab Noon 2024", "Saudi referral loop mechanics consumer apps"

Each would return 8-10 Evidence objects with tier-graded (⭐-⭐⭐⭐⭐⭐) sources, feeding into a `strip_unsupported_claims` pass over the 5-lens content so every numeric claim (SAR 3,500 tutor baseline, $10M+ Abwaab war chest, 40% Ramadan study-load drop, 1.05M Grade 11-12 cohort) resolves to a real citable URL.

---

**Next checkpoint:** 2026-07-16 — review whether the Riyadh pilot is trending to < SAR 450 blended CAC within 90 days of launch. If yes: green-light Jeddah. If no: re-open the pricing decision per Prism's stage-gate.
