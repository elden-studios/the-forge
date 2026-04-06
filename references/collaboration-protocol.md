# Collaboration Protocol v2.1 — The Forge

Elite multi-agent orchestration protocol.
Sources: Apple DRI, Amazon Working Backwards, GV Sprint, Netflix Informed Captain, Stripe Write-First, Bridgewater Radical Transparency, Tetlock Superforecasting.

**Standing Rules:**
- No filler. Every sentence carries information or provokes a decision.
- Default concise. Expand only when asked.
- Name the source for every best-practice reference.
- Real operations engagement, not brainstorm dump.

---

## Phase 1: INTAKE & CHALLENGE

**Lead:** Flint (Strategy)

Flint receives the brief first. Before routing:
1. Parse all workstreams, unknowns, assumptions
2. Challenge weak points — hard questions, not polite ones
3. Score and activate agents (see Routing)
4. Define success criteria
5. Check brief version (if iterating, track diff from previous version)

**Output:**
```
BRIEF CHALLENGE — Flint
━━━━━━━━━━━━━━━━━━━━━━
[BRIEF v1] (or [BRIEF v2 — DIFF: target changed from X to Y])

Problem Statement: [1 sentence]
Target User: [who specifically]
Success Looks Like: [measurable outcome]

⚠ Weak Point #1: [flaw]
⚠ Weak Point #2: [flaw]
⚠ Assumption at Risk: [what could be wrong]

❓ Questions You MUST Answer:
  1. [hard question]
  2. [hard question]

Agents Activated: [names + why]
Agents on Standby: [names + why]
Gap Detected: [role missing, if any]
```

**⏸ CHECKPOINT 1** — User answers questions + confirms problem statement. "Auto-approve" to let Flint decide.

**🎮 Office Viz:** Set `active_event: { type: "working", agents: ["agent-flnt"] }` — Flint's lightbulb animation activates.

---

## Phase 2: INTELLIGENCE GATHERING (Parallel)

**Agents:** Vex (Global) + Nyx (Saudi) + Echo (User Signals)

Run in PARALLEL — no dependencies between them.

**Routing:**
- Vex: ALWAYS activated
- Nyx: Activated on Saudi/KSA/MENA/Arabic/Vision 2030 keywords → becomes **routing lead** with veto power
- Echo: Activated for consumer/user-facing products

**Handoff specs:**

| Agent | Deliverable | Format | Acceptance |
|---|---|---|---|
| Vex | Competitive Landscape | Table: Competitor / Strengths / Weakness / Our Angle. Max 1 page. | ≥3 competitors with data |
| Nyx | Saudi Market Brief | Regulatory + local competitors + culture. Max 1 page. | Cite specific Saudi entities |
| Echo | User Signal Report | Top 3 pain points + evidence type. Max 1 page. | Each backed by evidence |

**Each agent includes confidence scoring** (Tetlock Superforecasting):
```
MY FINDING: [what the data shows]
CONFIDENCE: HIGH / MEDIUM / LOW — [why]
WHY THIS COULD BE WRONG: [honest risk]
ASSUMPTION: [what needs verification]
```

**🎮 Office Viz:** Set `active_event: { type: "working", agents: [activated agent IDs] }`

---

## Phase 3: WAR ROOM (Brainstorming)

**Moderator:** Flint
**Participants:** All agents score ≥ 2
**Red Team:** Flint plays adversary role — argues AGAINST the emerging consensus (Amazon "bar raiser" principle)

**Rules** (Bridgewater + Amazon):
1. No seniority — evidence weighted equally
2. Evidence > opinion. "15 users told me" > "I think"
3. 2 rounds maximum
4. Every recommendation names its core assumption
5. Disagree and commit after decision

**Format:**
```
WAR ROOM — [Topic]
━━━━━━━━━━━━━━━━━

Round 1: Positions
[Agent A]: Position + Evidence + Concern with B
[Agent B]: Position + Evidence + Concern with A

🔴 RED TEAM (Flint): "Here's why the consensus is wrong: [attack]"

Round 2: Convergence
[Agent A]: Response + Resolution proposal
[Agent B]: Response + Resolution proposal

Resolution: [Consensus / Compromise / User Decides]
Named Source: [framework]
```

**⏸ CHECKPOINT 2** — Direction decision:
```
⏸ DECISION REQUIRED
Option A: [desc] — Tradeoff: [x]
Option B: [desc] — Tradeoff: [y]
Option C: [desc] — Tradeoff: [z]
↳ Recommendation: [X] because [reason]
```

**🎮 Office Viz:** Set `active_event: { type: "meeting", agents: [participant IDs] }` — agents walk to hallway for debate.

---

## Phase 4: SOLUTION ARCHITECTURE (Sequential)

**Chain:** Atlas → Ren → Sable

Sequential because each constrains the next.

| From → To | Deliverable | Acceptance |
|---|---|---|
| Atlas → Ren | Tech architecture + constraints + build estimate (weeks) + #1 hardest technical risk | Cites specific tech stack decisions |
| Ren → Sable | UX flow + key screens + "what does user do first?" | Flow is testable with real users |
| Sable → Phase 5 | Brand direction + visual identity signals | Distinct from top 3 competitors |

**Each includes confidence:**
```
RECOMMENDATION: [what]
CONFIDENCE: [H/M/L] — [why]
CONSTRAINT: [can't do]
BUILD SIGNAL: [effort]
NAMED SOURCE: [framework]
```

**🎮 Office Viz:** Set `active_event: { type: "working", agents: [current phase agent] }` — sequential lightbulb.

---

## Phase 5: GO-TO-MARKET

**Agents:** Talon + Kira + Nyx (if Saudi)

| Agent | Deliverable |
|---|---|
| Talon | Primary channel + viral mechanic + 3-month plan + key metric |
| Kira | Headline + subhead + 3 messages + CTA (bilingual if Saudi) |
| Nyx | Saudi channel, timing (Ramadan?), regulatory timeline |

---

## Phase 6: CHALLENGE ROUND

**All activated agents** + **Red Team (Flint)**

Each agent: "#1 risk from my domain + mitigation."
Flint as Red Team: "The #1 reason this entire project fails."

```
CHALLENGE ROUND
━━━━━━━━━━━━━━
[Agent]: Risk — [desc]. Confidence: [H/M/L]. Mitigation: [action].
...
🔴 RED TEAM (Flint): Fatal flaw — [the hardest truth]. Mitigation: [if any].

UNMITIGABLE RISK → HIRE RECOMMENDATION: [Role] — [justification]
```

**⏸ CHECKPOINT 3** — Risk prioritization:
```
⏸ RISK TRIAGE
                 URGENT              NOT URGENT
HIGH IMPACT  │ Mitigate NOW (Wk 1) │ Schedule (Wk 2-4)
LOW IMPACT   │ Delegate             │ Cut / Defer

□ Risk 1: [desc] — Cost: [effort] — Quadrant: [X]
□ Risk 2: [desc] — Cost: [effort] — Quadrant: [X]
Which risks do you want addressed?
```

---

## Phase 7: FINAL DELIVERY

### Full Deliverable
```
╔══════════════════════════════════════╗
║ THE FORGE — [Project Name]          ║
║ Brief v[N]                          ║
╠══════════════════════════════════════╣
║ EXECUTIVE SUMMARY (5 sentences max) ║
║ Decision: GO / NO-GO / PIVOT        ║
║ Confidence: ██████░░░░ 65%          ║
╠══════════════════════════════════════╣
║ MARKET    (Vex + Nyx + Echo)        ║
║ TAM: $__  Competitors: __           ║
║ Confidence: [H/M/L per agent]       ║
╠══════════════════════════════════════╣
║ SOLUTION  (Atlas + Ren + Sable)     ║
║ Architecture: __  UX: __            ║
║ Build: __ weeks  Risk: __           ║
╠══════════════════════════════════════╣
║ LAUNCH    (Talon + Kira)            ║
║ Channel: __  Message: __            ║
║ Timeline: __  Metric: __            ║
╠══════════════════════════════════════╣
║ RISKS (Priority Matrix)             ║
║ 🔴 NOW: __                          ║
║ 🟡 SCHEDULE: __                     ║
║ ⚪ DEFER: __                        ║
╠══════════════════════════════════════╣
║ ACTION ITEMS (Eisenhower)           ║
║         URGENT        NOT URGENT    ║
║ HIGH  │ [task+owner] │ [task+owner] ║
║ LOW   │ [delegate]   │ [cut]        ║
╠══════════════════════════════════════╣
║ TEAM GAPS                           ║
║ [Hire recommendation if applicable] ║
╚══════════════════════════════════════╝
```

### Stakeholder One-Pager
```
STAKEHOLDER BRIEF — [Project Name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Problem: [1 sentence]
Solution: [1 sentence]
Market: [TAM + insight]
Differentiator: [1 sentence]
Build: [timeline + cost]
Launch: [channel + metric]
Risk: [#1 + mitigation]
Ask: [what you need]
```

---

## Phase 8: POST-MORTEM (Netflix Blameless Retrospective)

After delivery, add to `project_history` in forge-state.json:
```
RETRO — [Project Name]
━━━━━━━━━━━━━━━━━━━━━
What each agent got RIGHT: [brief per agent]
What each agent got WRONG: [brief per agent]
Bottleneck phase: [which phase was slowest/weakest]
Lesson for next time: [1 sentence]
Confidence calibration: [were H/M/L ratings accurate?]
```

Saved to project_history so future briefs benefit from past lessons.

---

## Agent Scoring (Dynamic Routing)

- **Score 3** (Direct match) → ACTIVATED
- **Score 2** (2+ knowledge overlap) → ACTIVATED
- **Score 1** (Adjacent) → STANDBY (activated on request)
- **Score 0** → SKIPPED

**Nyx Override:** Saudi keywords → routing lead + veto power.

## Versioned Briefs

When user iterates (e.g., "now try B2B"):
```
BRIEF v2 — DIFF from v1:
+ Target changed: consumer → B2B
+ Nyx elevated to routing lead
- Echo de-prioritized (B2B = less consumer research)
= Market sizing recalculated, Architecture unchanged
```

Only re-run phases affected by the diff. Don't restart from scratch.

## Auto-Approve Mode

"Auto-approve" → orchestrator decides all checkpoints, noting:
```
[AUTO-APPROVED] Decision: [X] — Reason: [why]
```
Revokable anytime with direct input.

## Office Visualization Events

Each phase sets `active_event` in the rendered office:
| Phase | Event Type | Visual |
|---|---|---|
| 1 Intake | `working` (Flint) | Flint lightbulb |
| 2 Intel | `working` (Vex/Nyx/Echo) | Multiple lightbulbs |
| 3 War Room | `meeting` (all participants) | Agents walk to hallway |
| 4 Architecture | `working` (Atlas→Ren→Sable) | Sequential lightbulb |
| 5 GTM | `working` (Talon+Kira) | Lightbulbs |
| 6 Challenge | `meeting` (all) | Full team in hallway |
| 7 Delivery | `idle` (all) | Everyone back at desks |
