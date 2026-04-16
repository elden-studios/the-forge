# tools/evidence_freshness.py
"""Per-source-type freshness classification.

Fresh vs. Stale vs. Refetch is a function of (source_type, age_in_days).
Thresholds per spec:
  primary_government / reputable_media:  180 / 730
  primary_company:                        90 / 365
  analyst:                                365 / 1095
  user_reviews / community:                30 / 180
  blog:                                    90 / 365
  (unknown source_type falls back to blog)

Pure function. Caller provides 'now' as ISO 8601 — keeps this testable
without patching datetime.
"""
from datetime import datetime


FRESHNESS_RULES = {
    "primary_government":    {"stale": 180, "refetch": 730},
    "primary_company":       {"stale": 90,  "refetch": 365},
    "analyst":               {"stale": 365, "refetch": 1095},
    "reputable_media":       {"stale": 180, "refetch": 730},
    "user_reviews":          {"stale": 30,  "refetch": 180},
    "community":             {"stale": 30,  "refetch": 180},
    "blog":                  {"stale": 90,  "refetch": 365},
}

_DEFAULT = FRESHNESS_RULES["blog"]


def _parse(iso):
    return datetime.strptime(iso.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")


def days_between(earlier_iso, later_iso):
    return (_parse(later_iso) - _parse(earlier_iso)).days


def classify_freshness(source_type, retrieved_at, now_iso):
    """Return 'fresh', 'stale', or 'refetch'.

    Raises ValueError with a clear message if retrieved_at or now_iso is
    None, empty, or not a parseable ISO 8601 string.
    """
    if not retrieved_at or not isinstance(retrieved_at, str):
        raise ValueError(
            f"retrieved_at must be a non-empty ISO 8601 string, got: {retrieved_at!r}"
        )
    if not now_iso or not isinstance(now_iso, str):
        raise ValueError(
            f"now_iso must be a non-empty ISO 8601 string, got: {now_iso!r}"
        )
    bands = FRESHNESS_RULES.get(source_type, _DEFAULT)
    age = days_between(retrieved_at, now_iso)
    if age >= bands["refetch"]:
        return "refetch"
    if age >= bands["stale"]:
        return "stale"
    return "fresh"
