# Cabinet Framing — Operator Protocol (v1)

This document is the in-skill reference for running Phase 1.5 Cabinet Framing. For the full design rationale see `docs/superpowers/specs/2026-04-17-v3.2-cabinet-design.md`. Mechanics implemented in Wave 2.

## When Cabinet Framing fires

All of these must be true:
- `forge-state.json` → `cabinet.executives` is present and non-empty
- The user input is a project brief (not "show office" / "team roster" / "hire X" / simple Q&A)
- The user did not say "skip cabinet" / "no framing" / "just use existing knowledge"

## The 5 executives

| Role | Agent | Playbook | Framing question |
|---|---|---|---|
| CSO | Flint | Rumelt (Strategy Kernel) | "What's the real question? Diagnosis?" |
| CPO | Cade | Cagan (Empowered Teams) | "User? Outcome? Non-goals?" |
| CTO | Helix | Fournier (Manager's Path) | "Greenfield/retrofit? Buy/build/partner?" |
| CFO | Prism | Tunguz/Sacks (unit econ) | "Unit econ shape? Break-even scale?" |
| CMO | Dune | Dunford/Moesta (positioning) | "Positioning? Who's the competitor for shelf space?" |

## The ceremony

1. Each exec writes ≤3 sentences answering their lens question
2. Cabinet compiles into a 1-page Framing Brief (`cabinet_framing.framing_brief` in `forge-tasks.json`)
3. Pre-Mortem fires: each exec lists top 2 failure modes (Klein's premortem technique)
4. Cabinet ranks by likelihood × impact (5×5), keeps top 5, assigns mitigation owners
5. Output stored in `forge-tasks.json` → `cabinet_framing` + `pre_mortem` blocks

## Output structure (v3.2 forge-tasks.json)

```json
{
  "cabinet_framing": {
    "framing_brief": "1-page synthesis",
    "lenses": {
      "strategic_kernel": "Flint's answer (3 sentences)",
      "product_shape": "Cade's answer",
      "build_class": "Helix's answer",
      "economic_shape": "Prism's answer",
      "market_bet": "Dune's answer"
    }
  },
  "pre_mortem": [
    {
      "failure_mode": "Saudi PDPL non-compliance forces shutdown at 10K users",
      "likelihood": 4,
      "impact": 5,
      "score": 20,
      "owner_agent": "agent-lexx",
      "mitigation_phase": "phase_5_gtm"
    }
  ]
}
```

## What to produce

- Framing Brief (1 page, written by Flint as CSO)
- Five lens answers (≤3 sentences each)
- Top 5 pre-mortem failure modes with owners
- No generic risk categories — every failure mode is a specific scenario

## Kill switch

- `cabinet.executives` absent or empty → Cabinet Framing disabled, Phase 1.5 skipped
- User phrase "skip cabinet" / "no framing" → skip for this brief only
- Empty roster → trivially no cabinet, skips

*Mechanics of how Flint/Cade/Helix/Prism/Dune actually generate their lens answers is defined in Wave 2 (decisions_orchestrator.py + extended Evidence Pipes dispatch). For Wave 1, operators manually produce these blocks following this structure.*
