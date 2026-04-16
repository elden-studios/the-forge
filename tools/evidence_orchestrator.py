# tools/evidence_orchestrator.py
"""Evidence orchestration — sub-brief generation + fan-in merge.

No real network calls here. Consumes subagent return envelopes and
produces a unified evidence bundle + meta stats.
"""
import json as _json
import re
import re as _re


EVIDENCE_AGENTS = {
    "agent-vexx": {
        "display_name": "Vex",
        "domain": "Market Intelligence",
        "default_preferences": "Prefer analyst reports and primary company filings",
    },
    "agent-nyxx": {
        "display_name": "Nyx",
        "domain": "Saudi Market",
        "default_preferences": "Saudi-specific sources (MEWA, SAMA, MCIT, Wamda) preferred over global",
    },
    "agent-echo": {
        "display_name": "Echo",
        "domain": "User Research",
        "default_preferences": "Prefer direct user signal: App Store, Play Store, Reddit, Product Hunt",
    },
    "agent-taln": {
        "display_name": "Talon",
        "domain": "Growth Architecture",
        "default_preferences": "Prefer competitor pricing pages, ad creatives, landing page teardowns",
    },
}


# Keyword → agent relevance heuristic (matches SKILL.md routing rubric style)
_RELEVANCE_KEYWORDS = {
    "agent-vexx": [
        "competitor", "market", "TAM", "tam", "pricing", "funding",
        "benchmarks", "landscape", "competitive",
    ],
    "agent-nyxx": [
        "saudi", "ksa", "mena", "arabic", "vision 2030", "nafath",
        "absher", "tawakkalna", "mada", "stc pay", "riyadh",
    ],
    "agent-echo": [
        "user", "persona", "interview", "research", "review", "feedback",
        "adoption", "behavior", "pain point", "jobs to be done",
    ],
    "agent-taln": [
        "growth", "aarrr", "funnel", "acquisition", "retention",
        "monetization", "distribution", "seo", "aso", "paid",
        "viral", "channel",
    ],
}


def score_agent_relevance(agent_id, brief):
    """Return 0-3 relevance. 3 = lead agent, 2 = activated, 0-1 = skip."""
    text = brief.lower()
    hits = sum(1 for kw in _RELEVANCE_KEYWORDS.get(agent_id, []) if kw in text)
    if hits >= 3:
        return 3
    if hits >= 1:
        return 2
    return 0


def generate_sub_brief(agent_id, brief, evidence_budget=8, quality_floor=3):
    """Return a sub-brief template string."""
    meta = EVIDENCE_AGENTS[agent_id]
    return f"""AGENT: {meta['display_name']} ({meta['domain']})
ORIGINAL BRIEF: {brief}

YOUR SUB-BRIEF:
Primary question: Evaluate the brief from your domain lens and surface
the evidence a VP would need to defend a decision.

Secondary questions (fill in based on your brain file template):
- What are the 3 most important data points in your domain?
- What's the strongest counter-evidence to the brief's assumptions?
- What gap in your domain can you NOT close with evidence (flag honestly)?

CONSTRAINTS:
- Evidence budget: {evidence_budget} queries max
- Quality floor: {quality_floor} (tier-3 analyst/reputable media or higher)
- {meta['default_preferences']}

RETURN (structured JSON envelope):
- 5-12 Evidence objects (full schema, including id, source_url, source_type,
  quality_score, retrieved_at, retrieved_by, queried_via, excerpt,
  confidence, signal_tag)
- Recommendation (1 paragraph)
- Confidence 0-1 with one-sentence reasoning
- Gaps: list of domain questions you could NOT answer with evidence
"""


def merge_returns(returns):
    """Fan-in merge of N subagent returns.

    Dedupes Evidence by source_url; retrieved_by grows into a list.
    Returns a unified bundle: {evidence, agents, total_queries, avg_quality, recommendations}
    """
    by_url = {}
    agents = []
    total_q = 0
    quality_vals = []
    recommendations = []

    for ret in returns:
        agents.append(ret["agent_id"])
        total_q += ret.get("queried_count", 0)
        if ret.get("quality_avg") is not None:
            quality_vals.append(ret["quality_avg"])
        recommendations.append({
            "agent_id": ret["agent_id"],
            "recommendation": ret.get("recommendation", ""),
            "confidence": ret.get("confidence", 0.0),
        })

        for ev in ret.get("evidence", []):
            url = ev.get("source_url", ev.get("id"))
            if url in by_url:
                # Merge retrieved_by
                existing_by = by_url[url].setdefault("retrieved_by", [])
                for agent in ev.get("retrieved_by", []):
                    if agent not in existing_by:
                        existing_by.append(agent)
            else:
                by_url[url] = dict(ev)

    return {
        "evidence": list(by_url.values()),
        "agents": agents,
        "total_queries": total_q,
        "avg_quality": sum(quality_vals) / len(quality_vals) if quality_vals else 0.0,
        "recommendations": recommendations,
    }


def append_evidence(project_id, bundle, evidence_path):
    """Persist merged bundle Evidence to forge-evidence.json."""
    with open(evidence_path) as f:
        doc = _json.load(f)

    existing_ids = {e["id"] for e in doc.get("evidence", [])}
    for ev in bundle.get("evidence", []):
        if ev["id"] not in existing_ids:
            doc["evidence"].append(ev)
            existing_ids.add(ev["id"])

    index = doc.setdefault("project_evidence_index", {})
    current = set(index.get(project_id, []))
    current.update(e["id"] for e in bundle.get("evidence", []))
    index[project_id] = sorted(current)

    with open(evidence_path, "w") as f:
        _json.dump(doc, f, indent=2)


# Matches [FACT], [FACT: ev-*], [INFERENCE], [INFERENCE: ev-*]
# id pattern is intentionally broad: real ids are ev-<8hex> but we must
# catch any ev-* string so unknown ids are checked against valid_evidence_ids.
_CLAIM_RE = _re.compile(r"\[(FACT|INFERENCE)(?::\s*(ev-\w+))?\]")


def strip_unsupported_claims(text, valid_evidence_ids):
    """Enforce Standing Rule 7: no citation → no claim.

    Replaces any [FACT] / [INFERENCE] without a valid Evidence ID
    with [UNSUPPORTED — dropped by validator]. Leaves [OPINION] and
    [HYPOTHESIS] alone.
    """
    def _sub(m):
        tag, eid = m.group(1), m.group(2)
        if eid and eid in valid_evidence_ids:
            return m.group(0)
        return "[UNSUPPORTED — dropped by validator]"

    return _CLAIM_RE.sub(_sub, text)
