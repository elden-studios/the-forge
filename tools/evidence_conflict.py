# tools/evidence_conflict.py
"""Conflict detection and resolution.

v1: rule-based, deterministic.
- cluster_by_keywords: group by shared content tokens (overlap >= 0.4)
- extract_numbers: pull $ / % / bare numerics from excerpts
- detect_conflicts: within a cluster, if numeric claims diverge > 20%, flag
- resolve: pick winner by scope > tier > recency
"""
import re
from datetime import datetime


_STOPWORDS = frozenset({
    "the", "a", "an", "of", "in", "is", "and", "or", "to", "for", "on",
    "at", "by", "with", "as", "from", "it", "its", "that", "this",
})


def _tokens(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def cluster_by_keywords(items, overlap_threshold=0.4):
    """Group items whose content-word sets overlap >= threshold (Jaccard).

    Deterministic given any input order: items are sorted by ID before
    clustering, and a new item joins the cluster with the maximum
    Jaccard overlap against ANY of its members (not just the first).
    """
    sorted_items = sorted(items, key=lambda it: it.get("id", ""))
    clusters = []
    for it in sorted_items:
        it_tokens = _tokens(it["excerpt"])
        best_cluster = None
        best_jaccard = 0.0
        for cluster in clusters:
            for member in cluster:
                ref_tokens = _tokens(member["excerpt"])
                union = it_tokens | ref_tokens
                if not union:
                    continue
                jaccard = len(it_tokens & ref_tokens) / len(union)
                if jaccard >= overlap_threshold and jaccard > best_jaccard:
                    best_cluster = cluster
                    best_jaccard = jaccard
        if best_cluster is not None:
            best_cluster.append(it)
        else:
            clusters.append([it])
    return clusters


def extract_numbers(text):
    """Return a list of floats extracted from $/%/unit-suffixed numerics.

    Handles comma thousands separators ('$1,340M' → [1340.0]).
    Excludes bare 4-digit year tokens (19xx/20xx) without a unit suffix
    to prevent 'in 2024' from contaminating the numeric set.
    """
    nums = []
    # Require EITHER a $ prefix, OR a unit suffix (M/B/K/%),
    # OR both. Plain numbers without context are ignored.
    # Pattern: optional $, digits with optional commas, optional decimal, optional unit
    pattern = r"(?:(\$)?([\d,]+(?:\.\d+)?)\s*([MBK%]))|(?:(\$)([\d,]+(?:\.\d+)?))"
    for match in re.finditer(pattern, text):
        # Two alternation branches — only one set of groups fires per match
        dollar_suffix = match.group(1)
        num_suffix = match.group(2)
        unit_suffix = match.group(3)
        dollar_only = match.group(4)
        num_only = match.group(5)

        if num_suffix is not None:
            raw = num_suffix
        elif num_only is not None:
            raw = num_only
        else:
            continue

        try:
            clean = raw.replace(",", "")
            nums.append(float(clean))
        except ValueError:
            pass
    return nums


def detect_conflicts(items, divergence=0.2):
    """Return list of {cluster, evidence_ids, divergence}."""
    conflicts = []
    for cluster in cluster_by_keywords(items):
        if len(cluster) < 2:
            continue
        nums_per_item = [(it, extract_numbers(it["excerpt"])) for it in cluster]
        nums_per_item = [(it, n) for it, n in nums_per_item if n]
        if len(nums_per_item) < 2:
            continue
        max_num = max(max(n) for _, n in nums_per_item)
        min_num = min(min(n) for _, n in nums_per_item)
        if max_num == 0:
            continue
        if (max_num - min_num) / max_num > divergence:
            conflicts.append({
                "evidence_ids": [it["id"] for it, _ in nums_per_item],
                "items": [it for it, _ in nums_per_item],
                "divergence": (max_num - min_num) / max_num,
            })
    return conflicts


def _matches_brief_scope(item, brief_scope):
    return item.get("scope", "global") == brief_scope


def resolve(conflict, brief_scope="global"):
    """Pick winner from conflict.items by scope > tier > recency.

    Returns (winner_item, rule_name).
    """
    items = conflict["items"]

    # 1. Scope: items matching the brief's scope win
    scoped = [it for it in items if _matches_brief_scope(it, brief_scope)]
    others = [it for it in items if not _matches_brief_scope(it, brief_scope)]
    if scoped and others:
        # Scope rule fires only when it actually separates items
        if len(scoped) == 1:
            return scoped[0], "scope"
        items = scoped  # tie among scoped → continue to tier

    # 2. Tier
    max_tier = max(it["quality_score"] for it in items)
    top_tier = [it for it in items if it["quality_score"] == max_tier]
    if len(top_tier) == 1:
        return top_tier[0], "tier"
    items = top_tier

    # 3. Recency
    def _at(it):
        return datetime.strptime(it["retrieved_at"].replace("Z", "+0000"),
                                  "%Y-%m-%dT%H:%M:%S%z")
    newest = max(items, key=_at)
    return newest, "recency"
