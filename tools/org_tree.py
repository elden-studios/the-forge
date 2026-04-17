"""Org tree helper — builds a tiered hierarchy from a forge-state dict.

Pure-function library. No file/network I/O. Consumed by the dashboard Org Tree
tab and by integration tests.

The org hierarchy is encoded on each agent via `reports_to` (agent id or None)
and `role` ("executive" | "ic"). Root is the agent with no `reports_to`; if
multiple such agents exist, prefer `cabinet.executives[0]` as tiebreak.

See SKILL.md / PLAN.md Sub-project A for the motivation (v3.2 Cabinet two-tier).
"""


def _root_id(agents_by_id, cabinet_execs):
    """Pick the single root agent id from a set of candidates.

    Candidates are agents whose `reports_to` is missing or explicitly None.
    Tiebreak: first id in cabinet.executives that is also a candidate, else the
    first candidate in iteration order. Returns None if there are zero
    candidates.
    """
    candidates = [
        a["id"] for a in agents_by_id.values()
        if a.get("reports_to") is None
    ]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    cand_set = set(candidates)
    for exec_id in cabinet_execs:
        if exec_id in cand_set:
            return exec_id
    return candidates[0]


def _node_view(agent, tier, children):
    """Pack an agent into the small dict shape used in the tree output."""
    return {
        "id": agent["id"],
        "name": agent.get("name", ""),
        "title": agent.get("title", ""),
        "role": agent.get("role", ""),
        "department_id": agent.get("department_id", ""),
        "tier": tier,
        "children": children,
    }


def _build_subtree(agent, tier, children_map, agents_by_id):
    """Recursively build the {id,name,...,children:[...]} tree rooted at `agent`.

    Children are sorted by id for deterministic ordering — keeps the dashboard
    layout stable across renders and tests.
    """
    child_ids = sorted(children_map.get(agent["id"], []))
    children = [
        _build_subtree(agents_by_id[cid], tier + 1, children_map, agents_by_id)
        for cid in child_ids
    ]
    return _node_view(agent, tier, children)


def _rivalry_edges(agents_by_id):
    """Collect mutual-rivalry pairs as a list of {a, b, scale} dicts.

    An edge is emitted only when both agents list each other in their
    `rivalries` array (mutual). Each pair appears at most once; the id pair is
    canonicalized (lower id in `a`) so dedup is straightforward. Scale is
    "cabinet" when both agents have role=executive, else "ic".
    """
    seen = set()
    edges = []
    for a in agents_by_id.values():
        a_id = a["id"]
        for b_id in a.get("rivalries") or []:
            b = agents_by_id.get(b_id)
            if b is None:
                continue
            if a_id not in (b.get("rivalries") or []):
                continue  # one-way — skip
            key = tuple(sorted((a_id, b_id)))
            if key in seen:
                continue
            seen.add(key)
            scale = (
                "cabinet"
                if a.get("role") == "executive" and b.get("role") == "executive"
                else "ic"
            )
            edges.append({"a": key[0], "b": key[1], "scale": scale})
    return edges


def get_org_tree(state):
    """Build the org tree from a state dict.

    Returns a dict shaped like:
    {
        "root": {"id", "name", "title", "role", "department_id",
                 "tier", "children": [...]} | None,
        "orphans": [agent-like-dicts...],   # reports_to points to missing id
        "rivalry_edges": [{"a", "b", "scale"}, ...],  # mutual only, deduped
    }
    """
    agents = (state or {}).get("agents", []) or []
    agents_by_id = {a["id"]: a for a in agents}
    cabinet_execs = ((state or {}).get("cabinet") or {}).get("executives", []) or []

    if not agents_by_id:
        return {"root": None, "orphans": [], "rivalry_edges": []}

    # Classify orphans: reports_to points to an id not in the state.
    orphans = [
        a for a in agents
        if a.get("reports_to") is not None
        and a["reports_to"] not in agents_by_id
    ]
    orphan_ids = {o["id"] for o in orphans}

    # Children map: parent_id -> [child_id, ...]. Skip orphans.
    children_map = {}
    for a in agents:
        if a["id"] in orphan_ids:
            continue
        parent = a.get("reports_to")
        if parent is None:
            continue
        children_map.setdefault(parent, []).append(a["id"])

    root_id = _root_id(agents_by_id, cabinet_execs)
    root = (
        _build_subtree(agents_by_id[root_id], 0, children_map, agents_by_id)
        if root_id is not None
        else None
    )

    return {
        "root": root,
        "orphans": orphans,
        "rivalry_edges": _rivalry_edges(agents_by_id),
    }
