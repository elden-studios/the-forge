"""URL → (quality_score, source_type) grading.

Rule-based first: regex patterns on URL match a tier 1-5 score and source_type.
Unknown URLs default to (2, 'unknown') — conservative: not trusted, not worst.
Supports user-provided overrides via a JSON file.
"""
import json
import os
import re


# (pattern, score, source_type) — order matters: first match wins
DEFAULT_RULES = [
    # Tier 5 — primary government / regulatory
    (r"\.gov\.sa(/|$)|\.gov(/|$)|mewa\.|sama\.|mcit\.|stats\.gov\.sa", 5, "primary_government"),
    (r"sec\.gov|esma\.europa\.eu", 5, "primary_government"),

    # Tier 4 — primary company
    (r"/10-?k/|/10-?q/|/annual-?report/|/earnings/|ir\.[a-z]+\.com", 4, "primary_company"),
    (r"\.com/pricing(/|$)|/pricing(/|$)", 4, "primary_company"),

    # Tier 3 — analyst / reputable media
    (r"mckinsey\.com|bcg\.com|bain\.com|gartner\.com|forrester\.com", 3, "analyst"),
    (r"ft\.com|reuters\.com|bloomberg\.com|wsj\.com|wamda\.com|arabnews\.com", 3, "reputable_media"),

    # Tier 2 — user-generated / community
    (r"play\.google\.com/store|apps\.apple\.com", 2, "user_reviews"),
    (r"reddit\.com|producthunt\.com|news\.ycombinator\.com", 2, "community"),

    # Tier 1 — blog / low signal
    (r"medium\.com|substack\.com|\.blog(/|$)", 1, "blog"),
]


def load_overrides(path):
    """Read a user overrides JSON file. Returns list of rule dicts. Missing → []."""
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("rules", [])


def merge_rules(defaults, overrides):
    """Prepend user overrides so they win on match.

    overrides: list of {pattern, score, type} dicts
    defaults: list of (pattern, score, type) tuples
    returns: list of (pattern, score, type) tuples
    """
    converted = [(o["pattern"], o["score"], o["type"]) for o in overrides]
    return converted + defaults


def grade_url(url, rules=None):
    """Return (quality_score, source_type) for a URL. Defaults to (2, 'unknown')."""
    if rules is None:
        rules = DEFAULT_RULES
    for pattern, score, stype in rules:
        if re.search(pattern, url, re.IGNORECASE):
            return (score, stype)
    return (2, "unknown")
