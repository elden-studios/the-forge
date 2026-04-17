"""Tools & Platforms catalog helper — schema validation, gap analysis, cost
breakdown, redundancy detection.

Pure-function library (no network, only file I/O through `load_catalog`). The
catalog shape is a single dict with two top-level keys: `tools` and
`categories`. Each tool declares who uses it (`used_by_agents`), who should
use it (`recommended_for_agents`), monthly cost, status, and optional
alternatives list. Status is one of {active, dormant, unused}.

Consumed by the dashboard Tools tab and by the integration test that validates
the committed `forge-platforms.json`.
"""
import json


STATUSES = frozenset({"active", "dormant", "unused"})

_REQUIRED_FIELDS = ("id", "name", "category_id", "status")
_LIST_FIELDS = ("used_by_agents", "recommended_for_agents", "alternatives")


def load_catalog(path):
    """Load the platforms catalog from disk. Returns dict with 'tools' +
    'categories'. No validation — call validate_catalog() separately.
    """
    with open(path) as f:
        return json.load(f)


def validate_catalog(catalog):
    """Raise ValueError on schema violations.

    Checks:
    - every tool has id, name, category_id, status
    - status in STATUSES
    - category_id references an existing category
    - used_by_agents / recommended_for_agents / alternatives are lists
    - cost_per_month_usd is a non-negative number (int or float, not bool)
    """
    tools = catalog.get("tools", [])
    categories = catalog.get("categories", [])
    cat_ids = {c["id"] for c in categories}

    for tool in tools:
        for field in _REQUIRED_FIELDS:
            if field not in tool:
                raise ValueError(
                    f"tool {tool.get('id', '<?>')} missing required field '{field}'"
                )
        if tool["status"] not in STATUSES:
            raise ValueError(
                f"tool {tool['id']} has unknown status {tool['status']!r} "
                f"(expected one of {sorted(STATUSES)})"
            )
        if tool["category_id"] not in cat_ids:
            raise ValueError(
                f"tool {tool['id']} references unknown category_id "
                f"{tool['category_id']!r}"
            )
        cost = tool.get("cost_per_month_usd", 0)
        # Reject bools (True/False are ints in Python but semantically wrong here)
        if isinstance(cost, bool) or not isinstance(cost, (int, float)):
            raise ValueError(
                f"tool {tool['id']} cost_per_month_usd must be number, got {cost!r}"
            )
        if cost < 0:
            raise ValueError(
                f"tool {tool['id']} cost_per_month_usd must be non-negative"
            )
        for lf in _LIST_FIELDS:
            val = tool.get(lf, [])
            if not isinstance(val, list):
                raise ValueError(
                    f"tool {tool['id']} field {lf!r} must be a list"
                )


def gap_analysis(catalog, agent_id):
    """Return tools where agent is in recommended_for_agents but NOT in
    used_by_agents. Empty list if agent has no gaps (or is unknown).
    """
    out = []
    for tool in catalog.get("tools", []):
        recommended = tool.get("recommended_for_agents", []) or []
        used = tool.get("used_by_agents", []) or []
        if agent_id in recommended and agent_id not in used:
            out.append(tool)
    return out


def cost_breakdown(catalog):
    """Summarize catalog cost.

    Returns:
        {
          'total_active_monthly_usd': sum of active tools' costs,
          'total_dormant_monthly_usd': sum of dormant tools' costs (WASTE),
          'by_category': {cat_id: sum of active costs in category},
          'by_agent': {agent_id: sum over (tool.cost / num_users)
                       for active tools the agent uses},
        }
    """
    total_active = 0.0
    total_dormant = 0.0
    by_category = {}
    by_agent = {}

    for tool in catalog.get("tools", []):
        cost = float(tool.get("cost_per_month_usd", 0) or 0)
        status = tool.get("status")

        if status == "active":
            total_active += cost
            cat = tool.get("category_id")
            if cat:
                by_category[cat] = by_category.get(cat, 0.0) + cost
            users = tool.get("used_by_agents", []) or []
            if users and cost > 0:
                share = cost / len(users)
                for uid in users:
                    by_agent[uid] = by_agent.get(uid, 0.0) + share
        elif status == "dormant":
            total_dormant += cost

    return {
        "total_active_monthly_usd": total_active,
        "total_dormant_monthly_usd": total_dormant,
        "by_category": by_category,
        "by_agent": by_agent,
    }


def find_redundancies(catalog):
    """Detect potential redundancy.

    Two signals:
    - `category_overlap`: 2+ ACTIVE tools in the same category. Surfaced for
      review (not always bad — e.g. Mixpanel + PostHog serve different jobs).
    - `listed_alternative`: Tool A's `alternatives` array contains tool B and
      BOTH are active. Confirmed redundancy.

    Returns list of dicts shaped:
        {"kind": "category_overlap" | "listed_alternative",
         "tools": [id, ...],
         "category_id"?: str,
         "note": str}
    """
    tools = catalog.get("tools", [])
    active = [t for t in tools if t.get("status") == "active"]
    active_ids = {t["id"] for t in active}
    out = []

    # Category overlap
    by_cat = {}
    for t in active:
        by_cat.setdefault(t["category_id"], []).append(t["id"])
    for cat_id, ids in by_cat.items():
        if len(ids) >= 2:
            out.append({
                "kind": "category_overlap",
                "tools": sorted(ids),
                "category_id": cat_id,
                "note": (
                    f"{len(ids)} active tools in category {cat_id} — "
                    f"review for overlap"
                ),
            })

    # Listed alternative — canonicalize pair to dedup
    seen_pairs = set()
    for t in active:
        for alt in t.get("alternatives", []) or []:
            if alt not in active_ids:
                continue
            pair = tuple(sorted((t["id"], alt)))
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            out.append({
                "kind": "listed_alternative",
                "tools": list(pair),
                "note": (
                    f"{pair[0]} lists {pair[1]} as an alternative — "
                    f"both active, confirmed overlap"
                ),
            })

    return out


def tools_by_agent(catalog, agent_id):
    """Return tools where agent is in used_by_agents OR recommended_for_agents.

    Each returned tool dict has an extra key `assignment`:
    - "assigned": agent is in used_by_agents
    - "recommended": agent is in recommended_for_agents only (a gap)
    """
    out = []
    for tool in catalog.get("tools", []):
        used = tool.get("used_by_agents", []) or []
        recommended = tool.get("recommended_for_agents", []) or []
        if agent_id in used:
            copy = dict(tool)
            copy["assignment"] = "assigned"
            out.append(copy)
        elif agent_id in recommended:
            copy = dict(tool)
            copy["assignment"] = "recommended"
            out.append(copy)
    return out
