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
    (r"/10-?k/|/10-?q/|/annual-?report/|/earnings/|//ir\.[a-z0-9-]+\.com", 4, "primary_company"),
    (r"\.com/pricing(/|$)|/pricing(/|$)", 4, "primary_company"),

    # Tier 3 — analyst / reputable media
    (r"mckinsey\.com|bcg\.com|bain\.com|gartner\.com|forrester\.com", 3, "analyst"),
    (r"ft\.com|reuters\.com|bloomberg\.com|wsj\.com|wamda\.com|arabnews\.com", 3, "reputable_media"),

    # Tier 2 — user-generated / community
    (r"play\.google\.com/store|apps\.apple\.com", 2, "user_reviews"),
    (r"//(www\.)?reddit\.com|//(www\.)?producthunt\.com|//news\.ycombinator\.com", 2, "community"),

    # Tier 1 — blog / low signal
    (r"medium\.com|substack\.com|\.blog(/|$)", 1, "blog"),
]


def load_overrides(path):
    """Read a user overrides JSON file. Returns list of well-formed rule dicts.

    Returns [] if:
    - the file doesn't exist
    - the JSON is malformed
    - "rules" key is missing or not a list
    Rules missing required keys (pattern, score, type) are silently skipped.
    This keeps a typo in user overrides from crashing the orchestrator.
    """
    if not os.path.isfile(path):
        return []
    try:
        with open(path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        return []
    valid = []
    for r in rules:
        if not isinstance(r, dict):
            continue
        if all(k in r for k in ("pattern", "score", "type")):
            valid.append(r)
    return valid


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
