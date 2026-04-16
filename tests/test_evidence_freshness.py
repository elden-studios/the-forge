# tests/test_evidence_freshness.py
"""Tests for per-source-type freshness classification."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_freshness import (  # noqa: E402
    FRESHNESS_RULES,
    classify_freshness,
    days_between,
)


class TestClassifyFreshness(unittest.TestCase):
    def test_gov_source_5_days_old_is_fresh(self):
        status = classify_freshness(
            source_type="primary_government",
            retrieved_at="2026-04-11T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "fresh")

    def test_gov_source_200_days_old_is_stale(self):
        status = classify_freshness(
            source_type="primary_government",
            retrieved_at="2025-09-28T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "stale")

    def test_gov_source_3_years_old_is_refetch(self):
        status = classify_freshness(
            source_type="primary_government",
            retrieved_at="2023-04-16T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "refetch")

    def test_user_reviews_40_days_old_is_stale(self):
        # user_reviews stale at 30, refetch at 180
        status = classify_freshness(
            source_type="user_reviews",
            retrieved_at="2026-03-07T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "stale")

    def test_user_reviews_200_days_old_is_refetch(self):
        status = classify_freshness(
            source_type="user_reviews",
            retrieved_at="2025-09-28T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "refetch")

    def test_unknown_source_type_treated_as_blog_defaults(self):
        # blog thresholds: stale=90, refetch=365
        status = classify_freshness(
            source_type="made-up-type",
            retrieved_at="2026-04-15T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "fresh")

    def test_boundary_exactly_on_stale_is_stale(self):
        # stale threshold INCLUSIVE (>= stale_days)
        # blog stale=90 → day 90 is stale, day 89 is fresh
        status = classify_freshness(
            source_type="blog",
            retrieved_at="2026-01-16T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",  # 90 days
        )
        self.assertEqual(status, "stale")

    def test_all_source_types_in_rules_table(self):
        for stype in [
            "primary_government", "primary_company",
            "analyst", "reputable_media",
            "user_reviews", "community", "blog",
        ]:
            self.assertIn(stype, FRESHNESS_RULES)


class TestDaysBetween(unittest.TestCase):
    def test_zero_days(self):
        self.assertEqual(days_between("2026-04-16T00:00:00Z", "2026-04-16T00:00:00Z"), 0)

    def test_one_day(self):
        self.assertEqual(days_between("2026-04-15T00:00:00Z", "2026-04-16T00:00:00Z"), 1)


if __name__ == "__main__":
    unittest.main()
