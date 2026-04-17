# tools/evidence_appendix.py
"""Sources Appendix rendering — compact terminal + full Markdown."""
from collections import defaultdict


_TIER_HEADERS = {
    5: "⭐⭐⭐⭐⭐ Primary Government",
    4: "⭐⭐⭐⭐ Primary Company",
    3: "⭐⭐⭐ Analyst / Media",
    2: "⭐⭐ User / Community",
    1: "⭐ Blog / Low Signal",
}


def _group_by_tier(items):
    groups = defaultdict(list)
    for it in items:
        groups[it["quality_score"]].append(it)
    return groups


def render_compact(items):
    """One line per source, grouped by tier. For terminal output."""
    if not items:
        return ""
    groups = _group_by_tier(items)
    lines = []
    for tier in sorted(groups.keys(), reverse=True):
        header = _TIER_HEADERS.get(tier, f"Tier {tier}")
        lines.append(f"{header} ({len(groups[tier])})")
        for it in groups[tier]:
            lines.append(f"  [{it['id']}] {it['source_title']} — {it['source_url']}")
    return "\n".join(lines)


def render_markdown(items):
    """Full Markdown appendix with excerpts and metadata. For exports."""
    if not items:
        return "## Sources Appendix\n\n_No sources cited._\n"
    groups = _group_by_tier(items)
    out = ["## Sources Appendix\n"]
    for tier in sorted(groups.keys(), reverse=True):
        header = _TIER_HEADERS.get(tier, f"Tier {tier}")
        out.append(f"### {header} ({len(groups[tier])})\n")
        for it in groups[tier]:
            date = it["retrieved_at"][:10]
            agents = ", ".join(it.get("retrieved_by", []))
            out.append(f"- **[{it['id']}] {it['source_title']}**")
            out.append(f"  - URL: {it['source_url']}")
            out.append(f"  - Retrieved: {date} by {agents}")
            # Render excerpt as a Markdown blockquote — natural for VP/board reading,
            # no Python repr noise. Multi-line excerpts are flattened with spaces.
            excerpt = str(it.get("excerpt", "")).replace("\n", " ")
            out.append(f"  - Excerpt: > {excerpt}")
            out.append("")
    return "\n".join(out)


def _format_elapsed(sec):
    if sec < 60:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    return f"{m}m {s:02d}s"


def render_summary_block(items, total_queries, elapsed_sec, cache_hits, conflicts):
    """The Evidence Summary block that sits above the recommendation."""
    if not items:
        avg = 0.0
    else:
        avg = sum(it["quality_score"] for it in items) / len(items)
    thin = sum(1 for it in items if it["quality_score"] == 1)
    return (
        f"EVIDENCE SUMMARY\n"
        f"  {total_queries} queries across 4 agents   |   {len(items)} sources cited\n"
        f"  Avg quality: {avg:.1f}/5              |   Conflicts: {conflicts}\n"
        f"  ⚠ Thin evidence: {thin}                |   Cache hits: {cache_hits}/{total_queries}\n"
        f"  Elapsed: {_format_elapsed(elapsed_sec)}\n"
    )
