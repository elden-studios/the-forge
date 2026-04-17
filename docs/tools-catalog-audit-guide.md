# Tools & Platforms Catalog — Operator Audit Guide

Sub-project E ships a living data file (`forge-platforms.json`) that inventories every SaaS / platform / API your team uses, who uses it, and what it costs. The dashboard's Tools tab reads this file and surfaces gaps, dormant spend, and redundancies.

The seed catalog is a plausible-but-generic stack. To make the dashboard useful for **your** team, spend 20 minutes auditing it.

---

## 1. Review the seed

Open `forge-platforms.json`. It has two top-level keys:

- `categories`: nine buckets (Design, Research, Engineering, Growth, Content, Legal, Finance, Analytics, Saudi-specific).
- `tools`: the inventory. Each tool declares `id`, `name`, `category_id`, `purpose`, `cost_per_month_usd`, `status`, `used_by_agents`, `recommended_for_agents`, `alternatives`, `vendor_url`, `notes`.

Status enum:

| Status    | Meaning                                                    |
| --------- | ---------------------------------------------------------- |
| `active`  | Paying for it and actively using it                        |
| `dormant` | Paying for it but not actively using — **potential waste** |
| `unused`  | Not subscribed; tracked as a candidate / aspiration        |

---

## 2. Edit to match your real stack

Three common edits:

**a. Add a tool.** Append a new object to `tools`. Pick a unique `id` (`tool-<slug>`), a real `category_id` from the list above, and a realistic cost. Fill `used_by_agents` with the agent ids actually touching it.

```json
{
  "id": "tool-slack",
  "name": "Slack",
  "category_id": "cat-content",
  "purpose": "Team chat, async comms",
  "cost_per_month_usd": 87,
  "status": "active",
  "used_by_agents": ["agent-flnt", "agent-cade", "agent-helx"],
  "recommended_for_agents": ["agent-flnt", "agent-cade", "agent-helx"],
  "alternatives": [],
  "vendor_url": "https://slack.com",
  "notes": "Pro plan, $7.25/user × 12"
}
```

**b. Remove a tool.** Delete the object. If other tools list it in `alternatives`, those references become stale (harmless — just not active-vs-active redundancy signal).

**c. Update cost or status.** Most common maintenance task. Re-check your last invoice monthly.

After any edit, mirror the file:

```bash
cp forge-platforms.json assets/forge-platforms.json
python3 -m unittest tests.test_subproject_e_integration
```

If the integration test still passes, the schema is still valid.

---

## 3. Mark dormant tools

This is where the audit pays for itself. Walk every `status: "active"` tool and ask: **did any agent actually open this in the last 30 days?**

If no, flip to `dormant`. The dashboard's "Dormant Waste" card sums those costs into a single number you can defend in a budget review.

Once you've decided to cancel, either delete the tool or leave it as `dormant` with a `notes` field recording the cancel date.

---

## 4. Run the dashboard

```bash
python3 -m http.server 8000 --directory assets
# open http://localhost:8000/dashboard.html and click Tools
```

You'll see four summary cards, then three sections:

- **Recommendations** — auto-generated. Three kinds:
  - *Consolidate* — two active tools that list each other as alternatives
  - *Dormant spend* — paying for something not actively used
  - *Gap* — an agent is recommended for a tool but not in its `used_by_agents`
- **By Category** — every tool grouped under its category, with status + redundancy badges and user chips.
- **By Agent** — one card per agent showing assigned tools (green chips), gaps (red chips), and allocated monthly spend (shared cost / number of users).

---

## 5. Workflow

| Cadence     | Action                                                              |
| ----------- | ------------------------------------------------------------------- |
| Monthly     | Scan invoices, update `cost_per_month_usd` where prices changed     |
| Quarterly   | Flip unused tools to `dormant`; cancel any that have been dormant 2+ quarters |
| On new hire | Add agent id to `used_by_agents` for every tool they'll touch       |
| On new role | If the catalog now recommends a tool the agent isn't on, it shows as a gap — assign or decline |
| Ad hoc      | Evaluating a new tool? Add it with `status: "unused"` and `recommended_for_agents` set. It shows as a gap until you assign users |

---

## 6. Schema reference

The validator (`tools/platforms_catalog.validate_catalog`) enforces:

- Every tool has `id`, `name`, `category_id`, `status`
- `status` ∈ `{active, dormant, unused}`
- `category_id` references an existing category
- `cost_per_month_usd` is a non-negative number
- `used_by_agents`, `recommended_for_agents`, `alternatives` are lists (possibly empty)

It does NOT enforce:

- Agent ids are real (integration test does — only on `forge-platforms.json`, not arbitrary callers)
- Alternatives reference real tool ids (stale ids silently ignored)
- URLs resolve

Keep `vendor_url` and `notes` honest — they don't affect the dashboard's math, but they're what you'll read six months from now when you've forgotten why you picked this tool.
