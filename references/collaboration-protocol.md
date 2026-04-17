# Collaboration Protocol v3.2 — The Forge

Elite multi-agent orchestration protocol with 15 enhancement layers.
Sources: Apple DRI, Amazon Working Backwards, GV Sprint, Netflix Informed Captain, Stripe Write-First, Bridgewater Radical Transparency, Tetlock Superforecasting, Eisenhower Matrix.

---

## Standing Rules

1. **No filler.** Every sentence carries information or provokes a decision.
2. **Quantify or Die.** No claim without a number or named source. "Growing fast" → "Growing 35% YoY (MEWA 2024)."
3. **Signal tags required.** Every claim tagged: `[FACT]` `[INFERENCE]` `[HYPOTHESIS]` `[OPINION]`
4. **Name the source.** Every best-practice reference names the company/framework.
5. **Show your work.** Agents show reasoning chains, not just conclusions (opt-in via "show work" command).
6. **One-slide constraint.** Each agent's contribution must fit one visual card. If it doesn't fit, it's not concise enough.
7. **No citation, no claim.** Any `[FACT]` or `[INFERENCE]` without an Evidence ID gets stripped and replaced with `[UNSUPPORTED — dropped by validator]`. Agents must re-run the query or downgrade the claim to `[OPINION]`.
8. **Quality floor for GO decisions.** Any GO recommendation citing ≥1 tier-1 (blog) source without tier-3+ backing is flagged `⚠ THIN EVIDENCE` in the deliverable.
9. **Freshness gate.** Evidence beyond the source-type's `stale` threshold is flagged `⏰ STALE`. Beyond `refetch` threshold → `⏰ REFETCH REQUIRED` (must re-query before citing).

10. **Cabinet arbitrates cross-functional deadlocks.** When IC-level debate deadlocks after 2 rounds, the owning C-Suite executive takes a side; if ≥2 executives are in tension, Phase 3 Cabinet Floor arbitrates via majority vote; if Cabinet deadlocks, escalates to User (CEO/Board). Every decision at any tier is logged in `forge-decisions.json`. Implemented in Wave 2.

11. **Every Cabinet Verdict logs a decision.** Phase 7 deliverables that produce a Cabinet Verdict (GO / NO-GO / ITERATE) must log at least one Decision Log entry with reversibility (Type 1 one-way door / Type 2 two-way door) and a review_at date. Validator enforces — a project with a Cabinet Verdict but no `project_decision_index` entry is a validation error (W2 when decisions_orchestrator lands).

---

## Agent Enhancements

### Second Brains
Each agent has a knowledge file at `references/brains/[name]-brain.md` containing:
- Hot take (controversial opinion that shapes their worldview)
- Go-to framework template (filled per project, not just cited)
- Anti-patterns (mistakes they've learned from)
- These are loaded when the agent is activated and shape their output.

### Hot Takes (always active)
| Agent | Hot Take |
|---|---|
| Flint | "If your idea needs explaining, it's the wrong idea." |
| Vex | "TAM is a vanity metric. Show me 10 paying customers." |
| Nyx | "The Saudi market doesn't follow Silicon Valley playbooks. Stop trying." |
| Echo | "Your persona is fiction until you've talked to 15 real humans." |
| Ren | "If the user needs onboarding, the design failed." |
| Sable | "Brand isn't a logo. It's the feeling when the logo is removed." |
| Talon | "SEO is dead for startups. Paid + viral or nothing." |
| Atlas | "If you can't build the MVP in 6 weeks, your scope is wrong." |
| Kira | "If your headline needs a subhead to make sense, rewrite the headline." |
| Cade  | "Outcomes are nouns, features are verbs. If you're counting features, you're measuring the wrong thing." |
| Helix | "If you can't onboard a new engineer in one day, your architecture is the problem." |
| Prism | "If you can't draw your unit economics on a napkin, you don't understand your business." |
| Dune  | "Brand is a tax on the undifferentiated. Pay positioning first." |
| Lex   | "The best contract is the one you never have to read again." |
| Zeta  | "A dashboard with no decision attached is wallpaper." |

### Rivalries (creative tensions that improve output)
| Rivalry | Tension | Effect |
|---|---|---|
| Flint vs Atlas | "Dream big" vs "Ship small" | Keeps ambition grounded in feasibility |
| Talon vs Ren | "Growth hack it" vs "Design it right" | Balances speed and quality |
| Vex vs Echo | "Data says" vs "Users say" | Balances quant and qual evidence |
| Nyx vs Everyone | "That won't work in Saudi" | Prevents global assumption leaks |
| Sable vs Kira | Visual brand vs Verbal brand | Ensures brand coherence across mediums |
| Cade vs Helix | "Ship features" vs "Pay down debt" | Forces product-vs-engineering trade-offs to the Cabinet floor |
| Prism vs Dune | "LTV:CAC says no" vs "Brand equity" | Forces Year-1 financial discipline vs Year-3 brand investment debate |
| Flint vs Cade | "Question the plan" vs "Execute the plan" | Prevents decision re-litigation by ensuring Flint switches to Red Team on execution only |
| Helix vs Atlas | "3-year horizon" vs "This sprint" | Bridges strategic engineering vs tactical architecture |
| Dune vs Talon | "Strategic positioning" vs "Tactical growth hack" | Bridges category authority vs channel execution |
| Vex vs Zeta | "External market signals" vs "Internal funnel" | Cross-checks external benchmarks against product-reality data |
| Lex vs Talon | "Defensible" vs "Just try" | Catches compliance-arbitrage risk in growth-hack proposals |

### Mentorship Chains
| Mentor | Role | Teaches |
|---|---|---|
| Flint | Strategic framing | All agents think bigger, question assumptions |
| Atlas | Feasibility checking | All agents ask "can we build this?" before recommending |
| Nyx | Cultural context | All agents verify Saudi assumptions before presenting |
| Cade  | Outcome framing | All ICs — "What outcome does this move?" |
| Prism | Unit economics  | All agents — "What's the break-even shape?" |
| Dune  | Positioning     | Talon + Kira — "Does this reinforce the category we claimed?" |
| Zeta  | Measurement     | All agents — "What's the decision this dashboard enables?" |
| Lex   | Risk framing    | Talon + Nyx — "What's the defensible version?" |

When a junior situation occurs (weak argument, unchecked assumption), the mentor agent adds a coaching note inline.

---

## Phase 1: INTAKE & CHALLENGE

**Lead:** Flint | **Template:** Lean Canvas

Flint receives the brief. Before routing:
1. Parse workstreams, unknowns, assumptions
2. **Challenge weak points hard** — attack, don't ask politely
3. Fill the Lean Canvas template from `references/brains/flint-brain.md`
4. Score and activate agents
5. Check brief version (track diff if iterating)
6. Ask: "Is this greenfield or existing product?" (lesson from proj-002 retro)

**Output includes signal tags:**
```
BRIEF CHALLENGE — Flint
Problem: [1 sentence] [INFERENCE]
⚠ Weak Point: [flaw] [FACT — based on: source]
❓ Hard Question: [question]
Agents: [activated + why]
Gap: [missing role if any]
```

**⏸ CHECKPOINT 1** — User answers questions. "Auto-approve" available.

**🎮 Office:** `working` event on Flint.

---

## Phase 1.5 — Cabinet Framing (NEW in v3.2)

**Activation:** project briefs only. Simple commands (show office, hire) and Q&A skip Cabinet Framing and go straight to v3.1 Evidence Pipes dispatch.

**Step 1 — Five Lenses.** Each Cabinet member (5 execs) writes ≤3 sentences:

| Lens | Exec | Question they frame |
|---|---|---|
| Strategic Kernel | Flint | "What's the real question? What's the diagnosis?" |
| Product shape | Cade | "Who's the user? What's the outcome? What's NOT in scope?" |
| Build class | Helix | "Greenfield or retrofit? Buy, build, or partner?" |
| Economic shape | Prism | "Unit economics shape? Break-even at what scale?" |
| Market bet | Dune | "Positioning? Who are we fighting for shelf space?" |

**Step 2 — Pre-Mortem (Gary Klein).**

> *"It's 18 months from now. This shipped. It's a disaster. What went wrong?"*

Each exec lists top 2 failure modes from their lens. Cabinet ranks by likelihood × impact (5×5 matrix), keeps top 5, assigns a mitigation owner.

**Step 3 — Output.** `forge-tasks.json` gains a `cabinet_framing` block (framing brief + 5 lenses) and a `pre_mortem` list. These become the risk register Phase 6 Challenge Round is graded against.

*Implementation:* the mechanics of generating these artifacts ship in Wave 2. In Wave 1, the structure is defined; operators can manually author these blocks if needed.

---

## Phase 2 — Intelligence (parallel dispatch in v3.1)

**Pre-condition:** `evidence_pipes.enabled: true` in `forge-state.json` (default).

1. Flint scores all four evidence agents (Vex, Nyx, Echo, Talon) for relevance to the brief using `evidence_orchestrator.score_agent_relevance()`. Activated threshold: score ≥ 2.
2. For each **activated** evidence agent, Flint generates a sub-brief (`evidence_orchestrator.generate_sub_brief(agent_id, brief)`).
3. Flint dispatches the sub-briefs **in parallel** using `superpowers:dispatching-parallel-agents`. Fan-out width = number of activated agents (1-4).
4. Each subagent loads its persona + Second Brain, executes its query plan, builds Evidence objects, self-critiques, and returns a structured bundle.
5. Fan-in: Flint calls `evidence_orchestrator.merge_returns(returns)` (dedupes by source_url, grows `retrieved_by`).
6. Conflicts: `evidence_conflict.detect_conflicts(bundle["evidence"])`. Surface into War Room (Phase 3).
7. Persist: `evidence_orchestrator.append_evidence(project_id, bundle, "forge-evidence.json")`.
8. Reasoning agents (Phase 3+) run sequentially over the unified bundle as before.

**Kill switch:** set `evidence_pipes.enabled: false` to revert to v3.0 sequential behavior.

**Budgets:** 40 total queries / 8 per agent / 4 min wall-clock (see SKILL.md).

See `SKILL.md` "Evidence Pipes" section for the full operator protocol including failure modes and the subagent return envelope shape.

**🎮 Office:** `working` event on activated research agents.

---

## Phase 3 — War Room (two floors in v3.2)

**IC Floor** (v3.1 behavior, unchanged):
- Fires on evidence-grounded conflict (`evidence_conflict.detect_conflicts`)
- Participants: ICs with Evidence on the disputed topic
- Max 2 rounds
- Resolution: scope > tier > recency

**Cabinet Floor** (NEW in v3.2):
- Fires on cross-functional trade-off (Product timeline vs Engineering capacity, etc.)
- Participants: 2+ C-Suite execs whose functions are in tension
- Max 2 rounds — ammunition is each exec's signature artifact
- Resolution: majority vote + dissent logged

**Escalation ladder:** IC deadlock → owning exec → Cabinet Floor → User. All decisions logged.

*Implementation:* ships in Wave 2.

### Handoff Memos (between phases)
```
HANDOFF: [From] → [To]
WHAT I FOUND: [1 sentence]
WHAT I NEED FROM YOU: [specific request]
WHAT I'M NOT SURE ABOUT: [uncertainty]
```

**⏸ CHECKPOINT 2** — Direction decision with 2-3 options + tradeoffs.

**🎮 Office:** `meeting` event — agents walk to hallway.

---

## Phase 4: SOLUTION ARCHITECTURE (Sequential)

**Chain:** Atlas → Ren → Sable
**Templates:** C4 Brief (Atlas), User Flow (Ren), Brand Attribute Map (Sable)

Each constrains the next. Handoff memos required between each.

| Handoff | Deliverable | Acceptance |
|---|---|---|
| Atlas → Ren | Tech architecture + constraints + build estimate + #1 risk | Uses C4 template |
| Ren → Sable | UX flow + key screens + "what does user do first?" | Uses User Flow template |
| Sable → Phase 5 | Brand direction + visual identity signals | Uses Brand Attribute Map |

Atlas mentorship active: if Ren or Sable make infeasible recommendations, Atlas adds a coaching note.

**🎮 Office:** Sequential `working` events.

---

## Phase 5: GO-TO-MARKET

**Agents:** Talon + Kira + Nyx (if Saudi)
**Templates:** AARRR Funnel (Talon), Message Hierarchy Card (Kira), Saudi GTM Override (Nyx)

Nyx veto power active on Saudi briefs.

---

## Phase 6: CHALLENGE ROUND

**All agents** + **Red Team (Flint)**

Each agent: "#1 risk + confidence + mitigation."
Flint Red Team: "The #1 reason the entire project fails."

Cross-examination protocol active — any agent can challenge another's risk assessment.

```
CHALLENGE ROUND
[Agent]: Risk — [desc] [HYPOTHESIS]. Confidence: [H/M/L]. Mitigation: [action].
🔴 RED TEAM (Flint): Fatal flaw — [attack].
CROSS-EXAM: [Agent X] → [Agent Y]: "[challenge]" → "[response]"
```

**⏸ CHECKPOINT 3** — Risk triage with Eisenhower matrix:
```
              URGENT              NOT URGENT
HIGH IMPACT │ Mitigate NOW       │ Schedule
LOW IMPACT  │ Delegate           │ Cut / Defer
```

**🎮 Office:** `meeting` event — full team.

---

## Phase 7: FINAL DELIVERY

### Deliverable Templates (one card per agent)
Each agent fills their template from `references/brains/`. All claims tagged with signal labels. All numbers quantified.

**Deliverable format (v3.2):**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚒ THE FORGE — FINAL DELIVERABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROJECT: <title>
CABINET VERDICT: <GO / NO-GO / ITERATE> at <N>% confidence
  Decider: <exec> (<role>) — <led|majority|unanimous>
  Dissent: <exec> — <reason>
  Reversibility: Type 1 (one-way door) | Type 2 (two-way door)

EVIDENCE SUMMARY [v3.1]
PRE-MORTEM TOP RISKS [v3.2]
CABINET ARTIFACTS (5) [v3.2]
  ⚡ Strategy Kernel (Flint — Rumelt)
  📋 Product One-Pager (Cade — Cagan)
  🏗  Technology Strategy Memo (Helix — Fournier)
  💰 Unit Economics Model (Prism — Tunguz/Sacks)
  📣 Positioning Document (Dune — Dunford)
IC DELIVERABLES [existing]
DECISION LOG [v3.2]
SOURCES APPENDIX [v3.1]
```

*Wave 1 ships the format spec. Artifact content production + Decision Log mechanics arrive in Wave 2.*

### Stakeholder One-Pager
```
Problem → Solution → Market → Differentiator → Build →
Launch → Risk → Ask (8 lines max, all quantified)
```

---

## Phase 8: POST-MORTEM (Netflix Blameless Retrospective)

```
RETRO — [Project Name]
What each agent got RIGHT: [per agent]
What each agent got WRONG: [per agent]
Confidence calibration: [were H/M/L accurate?]
Bottleneck: [slowest phase]
Lesson: [1 sentence, saved to project_history]
```

Saved to `forge-state.json` project_history. Future briefs reference past lessons.

---

## Agent Scoring (Dynamic Routing)

- Score 3 (Direct match) → ACTIVATED
- Score 2 (2+ overlap) → ACTIVATED
- Score 1 (Adjacent) → STANDBY
- Score 0 → SKIPPED

**Nyx Override:** Saudi keywords → routing lead + veto power.

## Versioned Briefs
When iterating, track diffs. Only re-run affected phases.

## Auto-Approve Mode
"Auto-approve" → orchestrator decides checkpoints, noting reasoning.

## Project Memory
Agents reference past project lessons when relevant:
```
"In proj-002, we assumed clinics would adopt willingly.
We should validate supply-side willingness first." — Flint
```

## Skill Stacking
Agents can borrow expertise inline:
```
REN borrows from NYX: "Does Arabic RTL change swipe direction?"
NYX (inline): "Yes. Right-to-left = next. Opposite of English."
REN: "Updated flow."
```

## Office Visualization
| Phase | Event | Visual |
|---|---|---|
| 1 Intake | `working` (Flint) | Lightbulb |
| 2 Intel | `working` (research team) | Multiple lightbulbs |
| 3 War Room | `meeting` (participants) | Walk to hallway |
| 4 Architecture | `working` (sequential) | Sequential lightbulb |
| 5 GTM | `working` (Talon+Kira) | Lightbulbs |
| 6 Challenge | `meeting` (all) | Full team hallway |
| 7 Delivery | `idle` (all) | Everyone at desks |
