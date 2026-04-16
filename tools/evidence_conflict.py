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
    """Group items whose content-word sets overlap >= threshold (Jaccard)."""
    clusters = []
    for it in items:
        placed = False
        it_tokens = _tokens(it["excerpt"])
        for cluster in clusters:
            ref_tokens = _tokens(cluster[0]["excerpt"])
            union = it_tokens | ref_tokens
            if not union:
                continue
            jaccard = len(it_tokens & ref_tokens) / len(union)
            if jaccard >= overlap_threshold:
                cluster.append(it)
                placed = True
                break
        if not placed:
            clusters.append([it])
    return clusters


def extract_numbers(text):
    """Return a list of floats extracted from $, %, or bare numbers."""
    nums = []
    for m in re.findall(r"\$?(\d+(?:\.\d+)?)\s*[MBK%]?", text):
        try:
            nums.append(float(m))
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
