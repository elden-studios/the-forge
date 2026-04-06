# The Forge — Progress & Resume Guide

## Current Status: FULLY OPERATIONAL — v1.0 Published

**GitHub:** https://github.com/elden-studios/the-forge
**Last session:** 2026-04-07

## What's Built

### Core System
- **SKILL.md** — Orchestration brain
- **references/collaboration-protocol.md** — v2.1 elite multi-agent workflow (8 phases, 3 checkpoints, Red Team, confidence scoring, Eisenhower matrix, post-mortems)
- **references/agent-design-guide.md** — Agent creation spec
- **references/pixel-office-spec.md** — Visual spec

### Team: 9 Agents, 6 Departments
| Agent | Title | Department |
|-------|-------|------------|
| Flint | Chief Ideation Architect | Strategy |
| Vex | Market Intelligence Lead | Research |
| Nyx | Saudi Market Strategist (routing lead on Saudi briefs) | Research |
| Echo | User Research Lead | Research |
| Ren | UX Alchemist | Design |
| Sable | Brand Alchemist | Design |
| Talon | Growth Architect | Growth |
| Atlas | Technical Architect | Engineering |
| Kira | Content Architect | Content |

### Office Visualization
- High-fidelity pixel art: 6 rooms (2x3 grid) + central hallway + break room
- Distinct floor textures per department (carpet, wood, linoleum, concrete)
- Thick walls with 3D depth, doors between rooms
- Props: bookshelves, laptops, monitors, whiteboards, server rack, vending machine, water cooler
- Chibi character sprites at CPX=3 with 4-tone shading, clothing folds, expressive eyes
- Event-driven animation: coffee walks, agent conversations, meeting room gatherings
- Walk routing through doors (no wall clipping)
- Desks persist when agents walk

### Collaboration Protocol v2.1
8 phases: Intake & Challenge → Intelligence (parallel) → War Room → Solution Architecture → GTM → Challenge Round → Final Delivery → Post-Mortem
- 3 hard checkpoints (user consulted with options)
- Red Team adversary (Flint argues against consensus)
- Confidence scoring per agent (H/M/L with justification)
- Eisenhower priority matrix for action items
- Versioned briefs (diff tracking on iteration)
- Auto-approve mode
- Office visualization events per phase

### Documentation
- **README.md** — Full project docs with quick start
- **TEAM.md** — Detailed profiles for all 9 agents
- **PLAN.md** — This file

## Completed Projects
| # | Project | Date | Outcome |
|---|---------|------|---------|
| 1 | Digital Signature Product | 2026-04-06 | GO — Saudi-first AI contract platform with Nafath integration |
| 2 | Pet Healthcare Platform | 2026-04-07 | GO (80%) — Scale existing pet ecosystem, clinic land-grab Riyadh, telehealth hook |

## Resume Points (what to do next)

### Immediate Options
1. **New project brief** — give any product idea to the full team
2. **Re-run Pet Platform** with deeper Phase 4 (Atlas architecture) + Phase 5 (Talon growth plan details)
3. **Hire more agents** — e.g., Legal/Compliance Specialist (flagged as gap)
4. **Visual enhancements** — character sprite quality, more environmental detail
5. **Plugin packaging** — convert to Claude Code plugin for marketplace distribution

### Known Issues to Fix
- Character sprites could be more detailed (more pixel-level features)
- Walking agents sometimes clip room boundaries at edge cases
- Office preview requires manual `python3 -m http.server 8765 -d assets`

### Tech Stack
- Preview server: `python3 -m http.server 8765 -d assets`
- Template hydration: `__FORGE_STATE_PLACEHOLDER__` → forge-state.json
- Canvas: CPX=3 characters, 16px tile grid environment
- All rendering: procedural Canvas API, no external images
