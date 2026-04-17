# ⚒ The Forge

### Your AI-powered product team. 9 elite agents. 6 departments. One office. Every claim cited.

Give a project brief. Watch 4 research agents fan out to the live web in parallel. Get a board-room-defensible answer with a Sources Appendix you can click through.

![Protocol v3.1 — Evidence Pipes](https://img.shields.io/badge/protocol-v3.1-purple) ![Tests 151 passing](https://img.shields.io/badge/tests-151%20passing-brightgreen) ![Stdlib only](https://img.shields.io/badge/deps-stdlib%20only-blue)

---

## What Is This?

The Forge is a Claude Code skill that simulates a **virtual company of specialized AI agents** who collaborate on product strategy using structured protocols inspired by Apple, Amazon, Netflix, Stripe, and Bridgewater.

Each agent has a distinct personality, expertise, controversial opinions, and they **challenge each other** — not just agree. The result is output that's been stress-tested through multiple expert lenses before it reaches you.

**v3.1 adds Evidence Pipes**: four research agents fan out in parallel via real WebSearch, pull Evidence from primary government sources, analyst reports, and app-store reviews, dedupe by (url, excerpt), detect numeric conflicts, and ship a Sources Appendix with every deliverable. No more "Vex said so" — every `[FACT]` tag resolves to a real URL with a timestamp and a quality tier.

```
You: "Launch a neobank for Saudi expats remitting to South Asia"

Vex:   "Corridor volume record: SAR 165.5B in 2025 [ev-f7e6d5c4]. Barq hit 1M
        users in 3 weeks. Careem Pay entered April 2026 [ev-0e1f2a3b] — window
        is closing."

Nyx:   "Don't need a full banking license — SAMA Payment Institution path via
        Sandbox. 42 firms permitted, 15 graduated [ev-c1d4887a]. Nafath is de
        facto mandatory for resident onboarding."

Echo:  "Vex is wrong that 'users just want speed'. Bangladeshis lost $1.3B to
        fees in 2024 [ev-e5b7003a]. Cost transparency is the #1 complaint
        volume driver — look at pissedconsumer, not App Store."

Talon: "Two channels: TikTok corridor-specific creative ('Abdullah received
        45,000 PKR') at $45-65 CAC, and double-sided WhatsApp referral gated
        on first transaction [ev-bb234567]. Not signup."

EVIDENCE SUMMARY
  32 queries across 4 agents   |   37 sources cited
  Avg quality: 3.5/5            |   Conflicts: 0
  ⚠ Thin evidence: 0            |   Cache hits: 0/32
```

Every `[ev-...]` is clickable. Every source is tier-graded. Click-through brings up MEWA, SAMA, Arab News, The Business Standard, Visa, World Bank — not a blog farm.

---

## The Team

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ⚒ THE FORGE — 9 Agents · 6 Departments                   │
│                                                             │
│  STRATEGY        RESEARCH           DESIGN                  │
│  ┌──────────┐   ┌──────────┐       ┌──────────┐           │
│  │  FLINT   │   │   VEX ⚡ │       │   REN    │           │
│  │ Ideation │   │ Market   │       │  UX/UI   │           │
│  │ Architect│   │ Intel    │       │ Alchemist│           │
│  └──────────┘   ├──────────┤       ├──────────┤           │
│                  │   NYX ⚡ │       │  SABLE   │           │
│                  │ Saudi    │       │  Brand   │           │
│                  │ Market   │       │ Alchemist│           │
│                  ├──────────┤       └──────────┘           │
│                  │  ECHO ⚡ │                              │
│                  │ User     │  GROWTH       ENGINEERING    │
│                  │ Research │  ┌──────────┐ ┌──────────┐   │
│                  └──────────┘  │ TALON ⚡ │ │  ATLAS   │   │
│                                │ Growth   │ │ Technical│   │
│  CONTENT                       │ Architect│ │ Architect│   │
│  ┌──────────┐                  └──────────┘ └──────────┘   │
│  │   KIRA   │                                              │
│  │ Content  │     ⚡ = Evidence Pipes agent                │
│  │ Architect│        (real WebSearch + parallel dispatch)  │
│  └──────────┘                                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

| Agent | Title | Hot Take | Pipes | Superpower |
|-------|-------|----------|-------|------------|
| **Flint** | Chief Ideation Architect | *"If your idea needs explaining, it's the wrong idea."* | — | Kills 7 out of 10 concepts before they waste your time. Red Team adversary. |
| **Vex** | Market Intelligence Lead | *"TAM is a vanity metric. Show me 10 paying customers."* | ⚡ | Finds competitors you've never heard of. Sizes markets with live WebSearch data. |
| **Nyx** | Saudi Market Strategist | *"The Saudi market doesn't follow Silicon Valley playbooks."* | ⚡ | Reaches primary SAMA/MCIT/Vision 2030 sources. Has veto power on Saudi briefs. |
| **Echo** | User Research Lead | *"Your persona is fiction until you've talked to 15 real humans."* | ⚡ | Scrapes real App Store, Play Store, and community reviews. |
| **Ren** | UX Alchemist | *"If the user needs onboarding, the design failed."* | — | Designs the anxiety out of every screen. Prototype in 48 hours. |
| **Sable** | Brand Alchemist | *"Brand isn't a logo. It's the feeling when the logo is removed."* | — | Creates identity systems that work at 16px and on billboards. |
| **Talon** | Growth Architect | *"SEO is dead for startups. Paid + viral or nothing."* | ⚡ | Teardowns of real competitor landing pages and CAC benchmarks. |
| **Atlas** | Technical Architect | *"If you can't build the MVP in 6 weeks, your scope is wrong."* | — | Turns "can we build this?" into a yes/no with an architecture diagram. |
| **Kira** | Content Architect | *"If your headline needs a subhead to make sense, rewrite it."* | — | Writes copy that converts — in English AND Arabic. |

---

## How It Works

### The 8-Phase Protocol (v3.1)

When you give a project brief, the team executes a structured workflow:

```
 ┌─────────────────────────────────────────────────────┐
 │ Phase 1: INTAKE & CHALLENGE                         │
 │ Flint attacks your brief. Hard questions. No mercy. │
 │ ⏸ CHECKPOINT: You answer before the team proceeds.  │
 └──────────────────────┬──────────────────────────────┘
                        ▼
 ┌────────────────────────────────────────────────────┐
 │ Phase 2: EVIDENCE PIPES  (v3.1 — parallel dispatch)│
 │                                                    │
 │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐          │
 │  │ Vex ⚡│ │ Nyx ⚡│ │Echo ⚡│ │Talon⚡│          │
 │  │Search │ │ SAMA/ │ │ App   │ │Compet.│          │
 │  │global │ │MCIT/  │ │Store/ │ │Landing│          │
 │  │market │ │Nafath │ │Reddit │ │ pages │          │
 │  └───────┘ └───────┘ └───────┘ └───────┘          │
 │                                                    │
 │  All 4 fan out via superpowers:dispatching-        │
 │  parallel-agents. Real WebSearch. 8 queries each,  │
 │  40 total. Each returns structured Evidence JSON.  │
 │                                                    │
 │  FAN-IN: dedupe by (url, excerpt), detect numeric  │
 │  conflicts (scope > tier > recency), persist to    │
 │  forge-evidence.json + mirror to assets/.          │
 └──────────────────────┬──────────────────────────────┘
                        ▼
 ┌─────────────────────────────────────────────────────┐
 │ Phase 3: WAR ROOM                                   │
 │ Agents debate — now with real citations.            │
 │ Red Team attacks the consensus with grounded facts. │
 │ ⏸ CHECKPOINT: You choose the direction.             │
 └──────────────────────┬──────────────────────────────┘
                        ▼
 ┌──────────┐  ┌──────────┐  ┌──────────┐
 │ Atlas    │→ │ Ren      │→ │ Sable    │  ← Phase 4: SEQUENTIAL
 │ Can we   │  │ How does │  │ What does│    architecture
 │ build it?│  │ it feel? │  │ it look? │    (each constrains next)
 └──────────┘  └──────────┘  └──────────┘
                     ▼
 ┌─────────────────────────────────────────────────────┐
 │ Phase 5: GO-TO-MARKET  (Talon + Kira + Nyx)        │
 │ Phase 6: CHALLENGE ROUND  "Why will this fail?"     │
 │ ⏸ CHECKPOINT: You prioritize risks.                 │
 │ Phase 7: FINAL DELIVERY  (EVIDENCE SUMMARY + cards) │
 │ Phase 8: POST-MORTEM  + Sources Appendix exported.  │
 └─────────────────────────────────────────────────────┘
```

### What Makes It Elite

| Feature | What It Does | Since |
|---------|-------------|-------|
| **⚡ Evidence Pipes** | 4 research agents fan out to live WebSearch in parallel. Every `[FACT]` tag resolves to a real URL. Sources Appendix shipped with every deliverable. | **v3.1** |
| **⚡ Quality Grading** | Each source graded 1–5: gov > primary company > analyst > user/community > blog. Tier stars visible in dashboard and exports. | **v3.1** |
| **⚡ Freshness Bands** | Per-source-type stale/refetch thresholds (gov 6mo, reviews 30d). `⏰ STALE` / `⏰ REFETCH` flagged in output. | **v3.1** |
| **⚡ Conflict Detection** | Numeric divergence > 20% in a topic cluster triggers `⚠ CONFLICT`. Resolution by scope > tier > recency. | **v3.1** |
| **⚡ Citation Enforcement** | `[FACT]` / `[INFERENCE]` / `[ev-X]` without valid Evidence IDs mechanically stripped or flagged. Not politely requested — enforced. | **v3.1** |
| **⚡ Sources Tab** | Dashboard tab with filter by tier/agent/freshness, full-text search, MD/CSV/JSON export. XSS-safe URL validation. | **v3.1** |
| **⚡ Atomic Evidence Cache** | Content-addressed cache with tempfile+replace atomicity. Parallel subagents can't corrupt entries. LRU eviction. | **v3.1** |
| **Signal Tags** | Every claim tagged `[FACT]` `[INFERENCE]` `[HYPOTHESIS]` `[OPINION]` — you know exactly what to trust | v3.0 |
| **Quantify or Die** | No vague claims allowed. "Growing fast" → "Growing 35% YoY (MEWA 2024)" | v3.0 |
| **Confidence Scoring** | Each agent rates HIGH/MEDIUM/LOW with justification (Tetlock Superforecasting) | v3.0 |
| **Red Team** | Flint argues AGAINST the consensus in every War Room (Amazon "bar raiser") | v3.0 |
| **Cross-Examination** | Agents formally challenge each other's claims with specific questions | v3.0 |
| **Handoff Memos** | Structured 3-line handoffs prevent information loss between phases | v3.0 |
| **Agent Rivalries** | Flint vs Atlas (dream vs ship), Talon vs Ren (growth vs quality), Vex vs Echo (data vs users) | v3.0 |
| **Mentorship Chains** | Flint coaches strategy, Atlas coaches feasibility, Nyx coaches Saudi context | v3.0 |
| **Hot Takes** | Each agent has a controversial opinion that shapes their worldview — they're opinionated, not generic | v3.0 |
| **Second Brains** | Each agent has a knowledge file with framework templates they actually fill out per project | v3.0 |
| **Project Memory** | Lessons from past briefs inform future ones — the team gets smarter over time | v3.0 |
| **Deliverable Templates** | Lean Canvas, AARRR Funnel, C4 Architecture, Competitive Matrix — filled, not just cited | v3.0 |
| **Nyx Veto Power** | On Saudi briefs, Nyx becomes routing lead with authority to reject GTM plans that ignore Saudi reality | v3.0 |
| **Pixel Art Office** | Watch agents at their desks, walking to meetings, getting coffee in a Stardew Valley-style office — now with `dispatched` pulsing bubbles + `evidence_arrived` glow animations | v3.0 + v3.1 |

---

## Evidence Pipes v1 — the upgrade in one screenshot

Before (v3.0):
```
Vex: "Saudi pet care is growing 35% YoY. [FACT]"
```
*(Source? Vex's training data. Probably 2023. Probably approximate.)*

After (v3.1):
```
Vex: "Saudi pet care is growing 35% YoY [ev-c1d2e3f4]."

Sources Appendix
⭐⭐⭐⭐⭐ Primary Government (1)
  [ev-c1d2e3f4] World Bank — Remittance Prices Q1 2025 — https://remittanceprices.worldbank.org/...
    Retrieved: 2026-04-17 by Vex | Freshness: 14d
```

A VP can click the URL and verify the claim in 10 seconds. That's the difference.

**Full end-to-end run documented at** [`docs/superpowers/runs/2026-04-17-neobank-brief/`](docs/superpowers/runs/2026-04-17-neobank-brief/README.md) — Saudi expat neobank brief, 4 agents in parallel, 37 Evidence across 32 WebSearch queries, 0 numerical conflicts, 0 thin evidence, all citations resolve.

**Kill switch:** set `"evidence_pipes": { "enabled": false }` in `forge-state.json` to revert to v3.0 behavior byte-for-byte. Or say "no evidence" / "skip pipes" for a one-shot override.

---

## Quick Start

```bash
# Clone
git clone https://github.com/elden-studios/the-forge.git
cd the-forge

# Run the tests (151 should pass)
python3 -m unittest discover tests -v

# Validate shipped state
python3 tools/validator.py

# Open in Claude Code
claude

# Use it
> "I have an idea for [product]. What does the team think?"
> "Hire a [role]"
> "Show the office"
> "Team roster"
> "Recommend hires"
```

### See the Office + Dashboard

```bash
python3 -m http.server 8765 -d assets
# Office:     http://localhost:8765/office-live.html
# Dashboard:  http://localhost:8765/dashboard.html   (Mission Control + Sources tab)
```

6 department rooms with distinct floors, thick walls, doors, hallway with vending machines, break room with coffee machine. Agents sit at desks with laptops, walk to get coffee, gather for meetings. When Phase 2 fires, the 4 evidence agents pulse yellow `[!]` bubbles; when their Evidence returns, their desks glow green.

The dashboard's **Sources tab** (new in v3.1) lets you filter the shipped `forge-evidence.json` by tier, agent, freshness, or free-text search, and export to Markdown / CSV / JSON.

---

## Project Structure

```
the-forge/
├── SKILL.md                              # Orchestration brain
├── README.md                             # This file
├── TEAM.md                               # Detailed agent profiles
├── PLAN.md                               # Progress & resume guide
├── CHANGELOG.md                          # v3.0 → v3.1 changelog
├── forge-state.json                      # Live roster + project history + pipes.enabled
├── forge-tasks.json                      # Real-time task tracking
├── forge-evidence.json                   # Evidence bank (auto-mirrored to assets/)
├── evidence-quality-overrides.json       # Optional user extensions to quality rules
├── references/
│   ├── collaboration-protocol.md         # v3.1 — 8 phases, 15 enhancements, Standing Rules 7-9
│   ├── evidence-pipes-spec.md            # Operator reference for Phase 2 pipes
│   ├── agent-design-guide.md             # How to create agents
│   ├── pixel-office-spec.md              # Visual spec
│   └── brains/                           # Agent Second Brain files (9 agents × 1 brain)
├── tools/                                # Python stdlib — Evidence Pipes engine
│   ├── validator.py                      # State / task / evidence integrity checks + CLI
│   ├── evidence_schema.py                # Evidence dataclass, enums, ID generator
│   ├── evidence_quality.py               # URL → (score, source_type) with user overrides
│   ├── evidence_freshness.py             # Per-tier stale/refetch band classifier
│   ├── evidence_cache.py                 # Atomic content-addressed cache + LRU
│   ├── evidence_conflict.py              # Numeric clustering + scope>tier>recency resolver
│   ├── evidence_orchestrator.py          # Sub-briefs, fan-in merge, citation enforcement
│   └── evidence_appendix.py              # Compact + Markdown Sources Appendix rendering
├── tests/                                # 151 unit tests, TDD-built
│   ├── test_validator.py                 # 40 tests
│   ├── test_evidence_schema.py           # 5
│   ├── test_evidence_quality.py          # 21
│   ├── test_evidence_freshness.py        # 12
│   ├── test_evidence_cache.py            # 11
│   ├── test_evidence_conflict.py         # 16
│   ├── test_evidence_orchestrator.py     # 26
│   ├── test_evidence_appendix.py         # 6
│   ├── test_cross_module_consistency.py  # 4
│   └── fixtures/                         # Test fixtures
├── assets/
│   ├── office-template.html              # Pixel art office engine (with v3.1 animations)
│   ├── office-live.html                  # Hydrated live preview
│   ├── dashboard.html                    # Mission Control + Sources tab
│   ├── forge-evidence.json               # Live mirror of root evidence
│   └── .forge-cache/                     # Gitignored WebSearch cache dir
├── docs/superpowers/
│   ├── specs/                            # Design specs (incl. Evidence Pipes v1)
│   ├── plans/                            # Implementation plans
│   └── runs/                             # Permanent records of live runs
│       └── 2026-04-17-neobank-brief/     # First Evidence Pipes end-to-end run
└── .claude/launch.json                   # Dev server config
```

---

## Commands

| Command | What Happens |
|---------|-------------|
| `[any product brief]` | Full 8-phase team analysis with 3 checkpoints — Phase 2 fans out to real web |
| `no evidence` / `skip pipes` | One-shot override: revert to v3.0 sequential behavior for this brief only |
| `hire a [role]` | Design + credential check + avatar + add to roster |
| `fire [name]` | Remove agent from roster |
| `recommend hires` | Team analyzes capability gaps |
| `team roster` | Show all agents and departments |
| `show the office` | Render pixel art visualization |
| `meeting room: [topic]` | Force a cross-agent debate |
| `auto-approve` | Let the team make checkpoint decisions for you |

---

## Completed Projects

| # | Project | Decision | Confidence | Key Insight |
|---|---------|----------|------------|-------------|
| 1 | Digital Signature Platform | **GO** | 75% | Saudi-first with Nafath integration. Meeting room debate: mobile vs web (resolved: mobile signing + web dashboard) |
| 2 | Pet Healthcare Platform | **GO** | 80% | "Booking is the hook. Pet profile is the lock-in. Health records are the moat." Clinic land-grab strategy for Riyadh |
| 3 | Saudi Expat Neobank *(v3.1 validation run)* | Research | 82% avg | Corridor volume SAR 165.5B/yr. SAMA Sandbox path avoids banking license. Cost, not speed, is the #1 user pain. [Full run →](docs/superpowers/runs/2026-04-17-neobank-brief/README.md) |

---

## Protocol Sources

The collaboration protocol draws from documented practices at:

- **Apple** — DRI (Directly Responsible Individual) model
- **Amazon** — Working Backwards, "bar raiser" adversary role
- **Google Ventures** — Design Sprint methodology
- **Netflix** — Informed Captain, Blameless Retrospectives
- **Stripe** — "Ship, iterate, scale" + Write-First culture
- **Bridgewater** — Radical Transparency, believability-weighted decisions
- **Philip Tetlock** — Superforecasting confidence calibration
- **Eisenhower** — Urgency × Impact prioritization matrix

v3.1 adds evidence-grading lineage inspired by:

- **Bloomberg Terminal** — timestamped, sourced, linkable primary data
- **Perplexity** — every claim cited, every source auditable
- **Palantir Foundry** — provenance tracked across transformations
- **Elicit / Consensus** — source-quality tiering and confidence bands

---

## Built With

- **Claude Code** — Skill execution engine
- **superpowers:dispatching-parallel-agents** — Phase 2 fan-out
- **WebSearch** — Real-time evidence retrieval (Chrome MCP scaffolded for phase 2)
- **HTML Canvas** — Procedural pixel art rendering (no external images)
- **Python stdlib** — Zero-dependency Evidence Pipes engine
- **Python HTTP server** — Local preview
- **Claude Preview MCP** — Live visualization

## Credits

Built by **Elden Studios** with Claude Code.

See [`CHANGELOG.md`](CHANGELOG.md) for the v3.0 → v3.1 release notes.

---

*"Give a brief. Watch 4 agents fan out to the real web. Get a cited answer."*
