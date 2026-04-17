# tools/evidence_orchestrator.py
"""Evidence orchestration — sub-brief generation + fan-in merge.

No real network calls here. Consumes subagent return envelopes and
produces a unified evidence bundle + meta stats.
"""
import json as _json
import os
import re as _re


# Integrate user-provided quality overrides at module load.
# Users drop an `evidence-quality-overrides.json` at project root (sibling to
# forge-state.json) to extend tier mappings without editing Python. See
# references/evidence-pipes-spec.md.
def _load_project_overrides():
    from evidence_quality import DEFAULT_RULES, load_overrides, merge_rules
    # Walk up from this file to find the project root (contains forge-state.json)
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)  # tools/.. == repo root
    overrides_path = os.path.join(root, "evidence-quality-overrides.json")
    overrides = load_overrides(overrides_path)
    return merge_rules(DEFAULT_RULES, overrides) if overrides else DEFAULT_RULES


PROJECT_QUALITY_RULES = _load_project_overrides()


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
        # Fintech / industry keywords (Task 14 demo readiness)
        "bank", "neobank", "fintech", "industry", "segment", "challenger",
        "incumbent", "remittance", "insurance", "startup",
    ],
    "agent-nyxx": [
        "saudi", "ksa", "mena", "arabic", "vision 2030", "nafath",
        "absher", "tawakkalna", "mada", "stc pay", "riyadh",
        # Additional Saudi/MENA signals
        "expat", "expatriate", "gulf", "gcc", "dubai", "jeddah",
    ],
    "agent-echo": [
        "user", "persona", "interview", "research", "review", "feedback",
        "adoption", "behavior", "pain point", "jobs to be done",
        # Research signals
        "customer", "segment", "cohort", "survey", "usability",
    ],
    "agent-taln": [
        "growth", "aarrr", "funnel", "acquisition", "retention",
        "monetization", "distribution", "seo", "aso", "paid",
        "viral", "channel",
        # Go-to-market & launch signals
        "launch", "gtm", "go-to-market", "onboarding", "conversion",
        "referral", "freemium", "pricing",
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

    Dedupes Evidence by the (source_url, excerpt) tuple — distinct excerpts
    from the same URL are KEPT as separate Evidence (they represent
    different claims). Only genuinely-identical (URL + excerpt) Evidence
    collapse; retrieved_by grows into a list on collapse.

    Returns a unified bundle: {evidence, agents, total_queries, avg_quality, recommendations}
    """
    by_key = {}
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
            # Dedup key: (source_url, excerpt). Fallback to id when URL absent.
            url = ev.get("source_url") or ""
            excerpt = ev.get("excerpt") or ""
            if url or excerpt:
                key = ("url+excerpt", url, excerpt)
            else:
                key = ("id", ev.get("id"))
            if key in by_key:
                existing_by = by_key[key].setdefault("retrieved_by", [])
                for agent in ev.get("retrieved_by", []):
                    if agent not in existing_by:
                        existing_by.append(agent)
            else:
                by_key[key] = dict(ev)

    return {
        "evidence": list(by_key.values()),
        "agents": agents,
        "total_queries": total_q,
        "avg_quality": sum(quality_vals) / len(quality_vals) if quality_vals else 0.0,
        "recommendations": recommendations,
    }


def _atomic_write_json(path, doc):
    """Write JSON atomically (tempfile + os.replace). Shared helper."""
    import tempfile
    dir_ = os.path.dirname(path) or "."
    stem = os.path.basename(path).rsplit(".", 1)[0]
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=f".{stem}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            _json.dump(doc, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise


def append_evidence(project_id, bundle, evidence_path):
    """Persist merged bundle Evidence to forge-evidence.json atomically.

    Uses a tempfile + os.replace pattern so a mid-write interruption
    leaves the original file intact.

    Also mirrors the result to <parent>/assets/<basename> when that
    sibling path exists — the live dashboard reads from assets/ via
    the local http.server, so the mirror prevents split-brain UX
    where the backend writes evidence but the UI shows 0 sources.
    """
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

    _atomic_write_json(evidence_path, doc)

    # Mirror to assets/ sibling if present (dashboard reads from there)
    parent = os.path.dirname(os.path.abspath(evidence_path)) or "."
    assets_dir = os.path.join(parent, "assets")
    if os.path.isdir(assets_dir):
        mirror_path = os.path.join(assets_dir, os.path.basename(evidence_path))
        try:
            _atomic_write_json(mirror_path, doc)
        except OSError:
            # Mirror failure is non-fatal — the primary write succeeded
            pass


# Matches two citation forms used in agent prose:
#   1. Tagged form:  [FACT], [FACT: ev-XXX], [INFERENCE], [INFERENCE: ev-XXX]
#   2. Naked form:   [ev-XXX], [ev-XXX, ev-YYY, ...]
# Both enforce Standing Rule 7: unlinked claims get flagged, not silently accepted.
_TAGGED_CLAIM_RE = _re.compile(r"\[(FACT|INFERENCE)(?::\s*(ev-\w+))?\]")
_NAKED_ID_BRACKET_RE = _re.compile(r"\[(ev-\w+(?:\s*,\s*ev-\w+)*)\]")
_SINGLE_ID_RE = _re.compile(r"ev-\w+")


def strip_unsupported_claims(text, valid_evidence_ids):
    """Enforce Standing Rule 7: no citation → no claim.

    Handles two citation forms in agent prose:

    1. Tagged form `[FACT]` / `[FACT: ev-XXX]` / `[INFERENCE: ev-XXX]`:
       If the tag has no ID or the ID is unknown, the whole tag is replaced with
       '[UNSUPPORTED — dropped by validator]'.

    2. Naked form `[ev-XXX]` or `[ev-XXX, ev-YYY, ...]`:
       Valid IDs survive. Invalid IDs are replaced inline with
       '⚠ <id> unsupported' so the reader can see which specific cite failed.
       If every ID in a single-item bracket is invalid, the bracket becomes
       '[UNSUPPORTED — dropped by validator]' to keep it scannable.

    `[OPINION]` and `[HYPOTHESIS]` are left untouched.
    """
    UNSUPPORTED = "[UNSUPPORTED — dropped by validator]"

    def _tagged(m):
        tag, eid = m.group(1), m.group(2)
        if eid and eid in valid_evidence_ids:
            return m.group(0)
        return UNSUPPORTED

    def _naked(m):
        ids = [i.strip() for i in _SINGLE_ID_RE.findall(m.group(1))]
        # All valid → pass through as-is
        if all(i in valid_evidence_ids for i in ids):
            return m.group(0)
        # All invalid → single UNSUPPORTED marker
        if not any(i in valid_evidence_ids for i in ids):
            return UNSUPPORTED
        # Mixed → rewrite inline, flagging only the bad ones
        rewritten = []
        for i in ids:
            if i in valid_evidence_ids:
                rewritten.append(i)
            else:
                rewritten.append(f"⚠ {i} unsupported")
        return "[" + ", ".join(rewritten) + "]"

    # Apply tagged form first (it's more specific: has FACT/INFERENCE word)
    text = _TAGGED_CLAIM_RE.sub(_tagged, text)
    # Then naked form
    text = _NAKED_ID_BRACKET_RE.sub(_naked, text)
    return text
