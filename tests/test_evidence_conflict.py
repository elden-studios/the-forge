# tests/test_evidence_conflict.py
"""Tests for conflict detection and resolution."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_conflict import (  # noqa: E402
    cluster_by_keywords,
    extract_numbers,
    detect_conflicts,
    resolve,
)


def _ev(id_, claim, source_type, retrieved_at, quality_score, excerpt=None, scope="global"):
    return {
        "id": id_, "claim": claim, "source_type": source_type,
        "quality_score": quality_score, "retrieved_at": retrieved_at,
        "excerpt": excerpt or claim, "scope": scope,
        "source_url": "", "source_title": "", "retrieved_by": [],
        "queried_via": "", "confidence": 0.8, "signal_tag": "FACT",
    }


class TestExtractNumbers(unittest.TestCase):
    def test_extracts_dollar_amounts(self):
        self.assertIn(340.0, extract_numbers("market size is $340M"))
        self.assertIn(510.0, extract_numbers("est $510M TAM"))

    def test_extracts_percentages(self):
        self.assertIn(14.0, extract_numbers("grew 14% YoY"))
        self.assertIn(18.0, extract_numbers("18% growth rate"))


class TestCluster(unittest.TestCase):
    def test_claims_sharing_keywords_cluster(self):
        items = [
            _ev("a", "Saudi pet market size 340M", "primary_government", "2026-01-01T00:00:00Z", 5),
            _ev("b", "Saudi pet market size 510M", "analyst", "2025-06-01T00:00:00Z", 3),
            _ev("c", "Unrelated topic about coffee", "blog", "2026-01-01T00:00:00Z", 1),
        ]
        clusters = cluster_by_keywords(items)
        # a and b cluster together; c alone
        self.assertEqual(len(clusters), 2)


class TestDetectConflicts(unittest.TestCase):
    def test_20pct_numeric_divergence_flags_conflict(self):
        items = [
            _ev("a", "Saudi pet market is $340M in 2024",
                "primary_government", "2026-01-01T00:00:00Z", 5),
            _ev("b", "Saudi pet market at $510M by 2024",
                "analyst", "2025-06-01T00:00:00Z", 3),
        ]
        conflicts = detect_conflicts(items)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(set(conflicts[0]["evidence_ids"]), {"a", "b"})

    def test_5pct_divergence_is_not_a_conflict(self):
        items = [
            _ev("a", "Saudi pet market $340M", "primary_government", "2026-01-01T00:00:00Z", 5),
            _ev("b", "Saudi pet market $350M", "analyst", "2025-06-01T00:00:00Z", 3),
        ]
        self.assertEqual(detect_conflicts(items), [])

    def test_no_numeric_content_no_conflict(self):
        items = [
            _ev("a", "Saudi vets use WhatsApp", "analyst", "2026-01-01T00:00:00Z", 3),
            _ev("b", "Saudi vets prefer SMS", "analyst", "2026-01-01T00:00:00Z", 3),
        ]
        # No numeric divergence → rule-based v1 does not flag
        self.assertEqual(detect_conflicts(items), [])


class TestResolve(unittest.TestCase):
    def test_scope_beats_tier(self):
        # Saudi-scoped tier-3 vs global tier-5 → Saudi wins
        saudi = _ev("saudi", "x", "analyst", "2026-01-01T00:00:00Z", 3, scope="saudi")
        global_gov = _ev("global", "x", "primary_government", "2026-04-01T00:00:00Z", 5, scope="global")
        winner, rule = resolve({"items": [saudi, global_gov]}, brief_scope="saudi")
        self.assertEqual(winner["id"], "saudi")
        self.assertEqual(rule, "scope")

    def test_tier_beats_recency_within_same_scope(self):
        old_gov = _ev("old", "x", "primary_government", "2024-01-01T00:00:00Z", 5, scope="global")
        new_blog = _ev("new", "x", "blog", "2026-04-01T00:00:00Z", 1, scope="global")
        winner, rule = resolve({"items": [old_gov, new_blog]}, brief_scope="global")
        self.assertEqual(winner["id"], "old")
        self.assertEqual(rule, "tier")

    def test_recency_wins_within_same_scope_and_tier(self):
        older = _ev("older", "x", "analyst", "2024-01-01T00:00:00Z", 3, scope="global")
        newer = _ev("newer", "x", "analyst", "2026-04-01T00:00:00Z", 3, scope="global")
        winner, rule = resolve({"items": [older, newer]}, brief_scope="global")
        self.assertEqual(winner["id"], "newer")
        self.assertEqual(rule, "recency")


if __name__ == "__main__":
    unittest.main()
