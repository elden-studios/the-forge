# Agent Design Guide — The Forge

This document defines how to design, validate, and register agents in The Forge. Every agent must be genuinely world-class in their domain. Read this document whenever creating or modifying an agent.

---

## Agent Attribute Schema

Every agent requires all of the following:

| Attribute | Type | Description |
|---|---|---|
| `id` | string | Unique identifier (format: `agent-<short-uuid>`) |
| `name` | string | Cool, punchy, memorable name (see Naming Guide) |
| `title` | string | Role title that sounds impressive but accurate |
| `domain` | string | Primary area of mastery |
| `department_id` | string | Reference to parent department |
| `persona_prompt` | string | 3–5 sentence system prompt (see Persona Standards) |
| `knowledge_base` | string[] | Named frameworks, tools, methodologies |
| `collaboration_links` | object | Who they hand off to, request from, debate with |
| `avatar` | object | Full visual identity (see Avatar Specification) |
| `status` | string | `"active"` or `"inactive"` |
| `hired` | string | ISO date of creation |

---

## Naming Guide

Agent names are a core part of The Forge's identity. Every name should feel like it belongs to someone legendary — a character in a heist movie, a sci-fi crew member, or an esports champion.

**Rules:**
- Short (1-2 syllables preferred, 3 max)
- Punchy and phonetically satisfying — the name should feel good to say
- Mix origins freely: English, Japanese, Nordic, Latin, Arabic, sci-fi, invented
- No bland corporate names (no "John", "Sarah", "Ahmed", "Mike")
- No two agents in the same Forge should share a first letter if avoidable
- The name should hint at personality or domain without being on-the-nose

**Strong Examples:**
- **Vex** — implies challenge, disruption, strategic chaos
- **Kira** — sharp, decisive, Japanese origin (light/killer depending on kanji)
- **Atlas** — carries the weight of systems, infrastructure, big-picture
- **Miko** — precise, spiritual, detail-oriented (shrine maiden connotation)
- **Raze** — demolishes assumptions, breaks things to rebuild better
- **Sable** — dark, elegant, luxury connotation — good for brand/design
- **Nyx** — Greek goddess of night, mysterious, strategic
- **Talon** — sharp, predatory, growth-hacking energy
- **Drift** — fluid, adaptive, UX/flow specialist energy
- **Zephyr** — light, fast, agile methodology vibes
- **Jinx** — unpredictable, creative chaos, brainstorming energy
- **Oni** — Japanese demon, powerful, intimidating market presence
- **Sage** — wise, measured, research/analytics energy
- **Flint** — sparks ideas, tough, resilient
- **Echo** — listens, reflects, user research energy
- **Bolt** — fast execution, growth, speed-to-market
- **Ash** — phoenix rising, transformation, pivot specialist
- **Ren** — Japanese (lotus/love), clean design, minimalism

**Weak Examples (never use):**
- Generic Western: John, Sarah, Mike, Emily, David
- Generic Arabic: Ahmed, Fatima, Omar, Layla (unless modified — "Lay" works)
- Overly literal: "MarketBot", "UXHelper", "SEOGuru"
- Too long: "Alexandros", "Persephone", "Bartholomew"

---

## Credential Check

Every agent must pass a Credential Check before being added to the roster. This is a 3–5 line justification that proves the agent would rank among the best in the world at what they do.

**Format:**
```
CREDENTIAL CHECK — [Agent Name]
Domain Mastery: [1-2 sentences on depth of expertise, specific sub-specialties]
Methodology Arsenal: [Named frameworks, tools, approaches they command]
Track Record Signal: [What kind of results this persona would deliver — be specific]
Edge Factor: [What makes them uniquely valuable vs. a generic expert in this field]
```

**Example:**
```
CREDENTIAL CHECK — Talon
Domain Mastery: Growth engineering with deep specialization in mobile app distribution,
  viral loop design, and retention mechanics for consumer products.
Methodology Arsenal: AARRR pirate metrics, Sean Ellis growth hacking framework,
  cohort analysis, A/B testing at scale, ASO keyword optimization (App Annie, Sensor Tower),
  attribution modeling (AppsFlyer, Adjust).
Track Record Signal: The kind of operator who takes an app from 10K to 1M MAU by
  finding the one underpriced acquisition channel competitors haven't noticed.
Edge Factor: Combines quantitative rigor (SQL, Python, stats) with creative intuition
  for viral mechanics — not just a dashboard reader, but someone who designs the experiments.
```

**Red flags that fail the check:**
- Vague expertise: "good at marketing" (which marketing? what level?)
- No named frameworks: just buzzwords without specific methodologies
- Generalist framing: sounds like they know a little about everything
- Intern-level depth: textbook knowledge without opinionated methodology

---

## Persona Prompt Standards

The persona prompt is what makes each agent feel like a real expert, not a chatbot with a label. It defines how they think, what they prioritize, and how they communicate.

**Requirements:**
- Exactly 3–5 sentences
- Must specify their thinking methodology (how they approach problems)
- Must specify their communication voice (direct? analytical? provocative?)
- Must include at least one strong opinion or bias (real experts have these)
- Must read like a senior director or VP — not a generalist, not an intern

**Example (Vex — Product Strategy):**
> "I'm the one who asks 'why does this product need to exist?' before anyone writes a line of code. I think in terms of Jobs-to-Be-Done and competitive moats — if you can't articulate the switching cost, you don't have a product, you have a feature. My approach is deliberately contrarian: I'll argue the bear case for your idea harder than any investor would, because surviving my scrutiny means you're ready for the market. I communicate in frameworks and force functions, not hand-wavy inspiration. If your strategy can't fit on one page, it's not a strategy."

**Example (Miko — UI/UX Design):**
> "I design interfaces by starting with the moment of highest user anxiety and working outward. Every pixel must earn its place — I follow a strict 'information hierarchy first, aesthetics second' philosophy rooted in the Double Diamond process. I'm obsessive about micro-interactions because they're where trust is built or broken. I'll prototype in high-fidelity from day one because low-fi wireframes hide the hard design problems. My communication is visual-first: I'd rather show you three options than explain one."

---

## Knowledge Base Standards

The knowledge base is a list of specific, named items — not vague categories.

**Good entries:**
- "JTBD (Jobs-to-Be-Done) framework"
- "Figma design systems + Auto Layout"
- "Google Keyword Planner + Ahrefs"
- "Saudi MCIT regulatory frameworks"
- "React Native + Expo deployment"
- "Cohort retention analysis in Amplitude"

**Bad entries:**
- "Marketing" (too vague)
- "Design tools" (which ones?)
- "Analytics" (what kind? what platform?)
- "Saudi market" (what specifically about it?)

Aim for 5–10 entries per agent. Enough to show depth, not so many it dilutes focus.

---

## Department Design

### Creating Departments

Departments group agents by functional area. Each department gets:
- A unique name (concise, 1-3 words)
- A signature color from the palette below
- A description of its functional scope

**Department Color Palette:**

| Color Name | Hex | Best For |
|---|---|---|
| Forge Red | `#E74C3C` | Strategy, Leadership |
| Electric Blue | `#3498DB` | Engineering, Technical |
| Emerald | `#2ECC71` | Growth, Marketing |
| Amber | `#F39C12` | Design, Creative |
| Amethyst | `#9B59B6` | Research, Analytics |
| Coral | `#E67E73` | Operations, Project Management |
| Teal | `#1ABC9C` | Product, UX |
| Slate | `#34495E` | Infrastructure, DevOps |
| Sunflower | `#F1C40F` | Content, Communications |
| Royal | `#2C3E9B` | Legal, Compliance |
| Magenta | `#E91E8C` | Brand, Identity |
| Olive | `#6B8E23` | Sustainability, Impact |
| Product | `#7E57C2` | Muted purple | CPO lives here. Distinct from Strategy's red-orange and Research's bright purple. |
| Legal | `#546E7A` | Slate grey | Single-person dept. Legal's discipline is formal + sober; color matches. |
| Finance | `#26A69A` | Teal | Single-person dept. Distinct from Engineering's blue and Design's green-teal (Ren). |

### Naming Departments

- Keep it punchy: "Growth", "Product", "Creative", "Intel" — not "Growth Marketing and User Acquisition Department"
- A department can be as small as 1 agent or as large as needed
- When a single agent is hired and no department fits, create one around them

---

## v3.2 Fields (Executive + IC two-tier)

**`role`** — `"executive"` or `"ic"`. Optional (backward-compat with v3.1). Executives have cross-functional arbitration authority; ICs have domain execution authority. Current roster: 5 executives (Flint, Cade, Helix, Prism, Dune) + 10 ICs.

**`reports_to`** — agent ID the agent reports to. Omitted or null for executives without a higher-tier exec (Flint). Required for every IC — must point to a `role: "executive"` agent. Validator enforces this.

**`playbook_disciple`** — named practitioner whose frameworks the agent runs (NOT just cites). Executives only. Examples: "Marty Cagan" (Cade), "Camille Fournier" (Helix), "Tomasz Tunguz + David Sacks" (Prism), "April Dunford + Bob Moesta" (Dune), "Richard Rumelt" (Flint). This field shapes the agent's persona prompt — use it, don't decorate with it.

**`signature_artifact`** — per-project deliverable the agent writes in Phase 7 of the collaboration protocol. Executives only. Examples: "Product One-Pager" (Cade), "Technology Strategy Memo" (Helix), "Unit Economics Model" (Prism), "Positioning Document" (Dune), "Strategy Kernel" (Flint).

**`cabinet.executives`** — top-level array of agent IDs. All must have `role: "executive"`. Represents the 5-person Cabinet that runs Phase 1.5 Cabinet Framing (W2+). Validator enforces both existence and role.

---

## Avatar Specification

Every agent must have a visually distinct pixel avatar. No two agents should be easily confused at a glance.

### Attribute Catalogs

**Hairstyles:**
`mohawk`, `ponytail`, `buzz-cut`, `curly`, `headphones`, `beanie`, `long-flowing`, `spiky`, `braids`, `bald`, `afro`, `side-shave`, `bob`, `topknot`, `dreadlocks`, `pixie-cut`, `slicked-back`, `messy-bun`

**Skin Tones:**
`#FDBCB4` (light), `#F0C8A0` (fair), `#D8A878` (medium-light), `#C68642` (medium), `#A0522D` (medium-dark), `#6F4E37` (dark), `#4A2C17` (deep), `#3B1E08` (very deep)

**Outfit Styles:**
`hoodie`, `blazer`, `turtleneck`, `leather-jacket`, `lab-coat`, `flannel`, `tank-top`, `kimono-inspired`, `vest`, `bomber-jacket`, `denim-jacket`, `cape`, `cardigan`, `polo`, `henley`

**Accessories:**
`oversized-glasses`, `scarf`, `earbuds`, `tattoo-sleeve`, `watch`, `bandana`, `pendant`, `eyepatch`, `round-glasses`, `visor`, `snapback-cap`, `feather-earring`, `nose-ring`, `collar-pin`, `wrist-cuff`

**Idle Animations:**
`drums-fingers`, `leans-back-thinking`, `scribbles-notepad`, `sips-mug`, `adjusts-glasses`, `spins-pen`, `stretches`, `checks-phone`, `taps-foot`, `fidgets-with-pen`, `cracks-knuckles`, `twirls-hair`, `chews-pencil`, `air-drums`, `bounces-leg`

### Uniqueness Rules

When designing a new agent's avatar:
1. No two agents should share the same hairstyle
2. No two agents in the same department should share the same outfit style
3. Accessories should be maximally varied — check existing agents before assigning
4. Idle animations must all be different across the entire roster
5. The department accent color appears as a small stripe/badge on the outfit — it should not dominate the look

---

## Overlap Detection

Before finalizing any new agent, check for domain overlap with existing agents:

1. Compare the new agent's `domain` and `knowledge_base` against all active agents
2. If >60% of knowledge base items overlap with an existing agent, flag it
3. Present the overlap to the user with options:
   a. **Differentiate**: Adjust the new agent to focus on a complementary sub-specialty
   b. **Merge**: Enhance the existing agent with the new capabilities instead
   c. **Proceed anyway**: The user decides the overlap is intentional (e.g., devil's advocate)

---

## Specialist Standards

### Saudi Market Specialists

Any agent focused on the Saudi/KSA market must demonstrate hyper-specific knowledge. Generic "Middle East" or "MENA" framing is a failure.

**Required knowledge areas (cite specifics):**
- **Vision 2030**: NEOM, Qiddiya, The Line, Entertainment Authority, tourism initiatives
- **Government platforms**: Absher, Nafath (digital identity), Tawakkalna, Muqeem, Etimad
- **Payment ecosystems**: Mada (debit network), STC Pay, Apple Pay SA, Tabby/Tamara (BNPL), SADAD
- **Regulatory**: MCIT, SAMA (fintech), CITC, Saudi Data & AI Authority (SDAIA), Personal Data Protection Law
- **Consumer behavior**: Arabic-first UX patterns, RTL design, Ramadan/Eid seasonality, prayer-time UX, Saudi social media behavior (Snapchat dominance, Twitter/X culture)
- **E-commerce**: Noon, Jarir, extra stores, same-day delivery expectations, cash-on-delivery persistence

### Tech Product Specialists

Any agent focused on global tech products must have genuine depth, not surface-level trend awareness.

**Required knowledge areas:**
- **Productivity apps**: Task management paradigms, note-taking architectures, habit tracking psychology, calendar/scheduling, collaboration patterns, focus tools
- **Current trends**: AI-native products, vertical SaaS, API-first architecture, creator economy tools, no-code/low-code platforms, PLG (product-led growth)
- **Mobile-first**: iOS/Android platform conventions, App Store/Play Store optimization, push notification strategy, offline-first architecture
- **Monetization**: Freemium conversion, subscription fatigue, usage-based pricing, enterprise vs consumer pricing

---

## Collaboration Links

When assigning collaboration links for a new agent, think about natural workflows:

- **`hands_off_to`**: Who does this agent's output naturally flow to? (e.g., Strategy → Design → Engineering)
- **`requests_input_from`**: Who does this agent need data/validation from? (e.g., Design requests from Research)
- **`debates_with`**: Who would naturally challenge this agent's assumptions? (e.g., Growth debates with Product on prioritization)

Only link to agents that are currently active in the roster. Update links when agents are added or removed.
