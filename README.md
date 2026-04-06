# ⚒ The Forge

**An AI-powered virtual company of specialized agents for Claude Code.**

The Forge simulates a team of 9 expert agents across 6 departments who collaborate on product strategy, market research, UX design, technical architecture, growth, and content — all orchestrated through a pixel art office visualization.

Give a project brief. Watch the team debate, challenge, and deliver.

## What It Does

- **9 specialized AI agents** with distinct expertise, personas, and collaboration protocols
- **Structured multi-agent workflow** inspired by Apple, Amazon, Netflix, and Stripe team practices
- **Pixel art office visualization** — see your agents at their desks, walking to meetings, getting coffee
- **Project briefs** — describe a product idea and the full team analyzes it through 8 structured phases
- **Dynamic routing** — only relevant agents are activated per brief
- **Brainstorming war rooms** — agents debate each other with evidence-based arguments
- **Hire/fire agents** — grow the team based on capability gaps
- **Saudi market expertise** — dedicated Saudi market strategist with Vision 2030 knowledge

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/the-forge.git

# 2. Open in Claude Code
cd the-forge
claude

# 3. Start using The Forge
> show the office
> hire a [role]
> [describe any product idea]
> recommend hires
> team roster
```

## Team Roster

| Agent | Title | Department | Specialty |
|-------|-------|------------|-----------|
| **Flint** | Chief Ideation Architect | Strategy | Product concepts, SCAMPER, First Principles, Blue Ocean |
| **Vex** | Market Intelligence Lead | Research | Competitive analysis, TAM/SAM/SOM, global market data |
| **Nyx** | Saudi Market Strategist | Research | Saudi/GCC intel, Vision 2030, MEWA/MCIT/SAMA regulations |
| **Echo** | User Research Lead | Research | User interviews, The Mom Test, behavioral psychology |
| **Ren** | UX Alchemist | Design | User flows, prototyping, Double Diamond, accessibility |
| **Sable** | Brand Alchemist | Design | Visual identity, brand systems, Arabic typography |
| **Talon** | Growth Architect | Growth | AARRR metrics, viral loops, ASO/SEO, PLG |
| **Atlas** | Technical Architect | Engineering | System architecture, C4 modeling, API design, cloud infra |
| **Kira** | Content Architect | Content | Conversion copy, Arabic content, email sequences, ASO copy |

## Collaboration Protocol (v2.1)

When you give a project brief, the team executes an 8-phase workflow:

```
Phase 1: INTAKE & CHALLENGE    → Flint frames the problem, attacks weak points
Phase 2: INTELLIGENCE          → Vex + Nyx + Echo research in parallel
Phase 3: WAR ROOM              → Structured debate with Red Team adversary
Phase 4: SOLUTION ARCHITECTURE → Atlas → Ren → Sable (sequential)
Phase 5: GO-TO-MARKET          → Talon + Kira + Nyx
Phase 6: CHALLENGE ROUND       → "Why will this fail?" — all agents
Phase 7: FINAL DELIVERY        → Structured cards + stakeholder one-pager
Phase 8: POST-MORTEM           → Retro saved for future briefs
```

**3 user checkpoints** where you're consulted with options before proceeding. Say "auto-approve" to let the team decide.

Sources: Apple DRI, Amazon Working Backwards, GV Sprint, Netflix Informed Captain, Stripe Write-First, Bridgewater Radical Transparency, Tetlock Superforecasting.

## Office Visualization

The Forge includes a pixel art office rendered in HTML Canvas:

- **6 department rooms** with distinct floor textures (carpet, wood, linoleum, concrete)
- **Thick walls with 3D depth**, doors between rooms, central hallway
- **Props**: bookshelves, laptops, coffee mugs, whiteboards, server racks, vending machines
- **Chibi character sprites** with distinct hairstyles, outfits, and accessories
- **Event-driven animation**: agents walk to coffee, chat with each other, gather for meetings
- **Cozy modern retro aesthetic** inspired by Stardew Valley and Earthbound

Start the office preview:
```bash
python3 -m http.server 8765 -d assets
# Then open http://localhost:8765/office-live.html
```

## Project Structure

```
the-forge/
├── SKILL.md                           # Main orchestration brain
├── PLAN.md                            # Progress tracker
├── README.md                          # This file
├── TEAM.md                            # Detailed agent profiles
├── forge-state.json                   # Live roster + project history
├── references/
│   ├── agent-design-guide.md          # How to create agents
│   ├── collaboration-protocol.md      # v2.1 multi-agent workflow
│   └── pixel-office-spec.md           # Visual spec
├── assets/
│   ├── office-template.html           # Pixel art office (template)
│   └── office-live.html               # Hydrated live version
├── docs/
│   └── superpowers/specs/             # Design specs
└── .claude/
    └── launch.json                    # Dev server config
```

## Commands

| Command | What It Does |
|---------|-------------|
| `hire a [role]` | Design and add a new agent to the team |
| `fire [name]` | Remove an agent from the roster |
| `recommend hires` | Team analyzes capability gaps |
| `team roster` | Show all agents and departments |
| `show the office` | Render the pixel art visualization |
| `[any product brief]` | Full 8-phase team analysis |
| `meeting room: [topic]` | Force a cross-agent debate |

## Built With

- **Claude Code** — skill execution engine
- **HTML Canvas** — procedural pixel art rendering
- **Python HTTP server** — local preview
- **Claude Preview MCP** — live visualization

## Credits

Built by **Elden Studios** with Claude Code.

---

*"Give a project brief. Watch the team argue. Get better answers."*
