# tests/test_decisions_orchestrator.py
"""Tests for the Decision Log schema primitives and reversibility logic."""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from decisions_orchestrator import (  # noqa: E402
    DECISION_STATUSES,
    REVERSIBILITY,
    new_decision_id,
    compute_review_at,
)


class TestDecisionId(unittest.TestCase):
    def test_new_id_has_expected_prefix(self):
        did = new_decision_id()
        self.assertTrue(did.startswith("dec-"), f"got: {did}")

    def test_new_id_matches_format(self):
        did = new_decision_id()
        self.assertRegex(did, r"^dec-[0-9a-f]{8}$")

    def test_new_id_is_unique_across_calls(self):
        ids = {new_decision_id() for _ in range(50)}
        self.assertEqual(len(ids), 50)


class TestEnums(unittest.TestCase):
    def test_decision_statuses_contains_four_values(self):
        self.assertEqual(
            DECISION_STATUSES,
            frozenset({"open", "reviewed", "reversed", "committed"}),
        )

    def test_reversibility_contains_two_values(self):
        self.assertEqual(
            REVERSIBILITY,
            frozenset({"type_1", "type_2"}),
        )


class TestComputeReviewAt(unittest.TestCase):
    """compute_review_at(decided_at_iso, reversibility) -> review_at ISO string"""

    def test_type_1_default_is_90_days(self):
        review = compute_review_at("2026-01-01T00:00:00Z", "type_1")
        self.assertEqual(review, "2026-04-01T00:00:00Z")

    def test_type_2_default_is_30_days(self):
        review = compute_review_at("2026-01-01T00:00:00Z", "type_2")
        self.assertEqual(review, "2026-01-31T00:00:00Z")

    def test_type_1_across_year_boundary(self):
        review = compute_review_at("2025-11-15T00:00:00Z", "type_1")
        self.assertEqual(review, "2026-02-13T00:00:00Z")

    def test_accepts_fractional_seconds(self):
        review = compute_review_at("2026-01-01T12:30:45.123Z", "type_1")
        self.assertTrue(review.startswith("2026-04-01"))

    def test_rejects_unknown_reversibility(self):
        with self.assertRaises(ValueError) as ctx:
            compute_review_at("2026-01-01T00:00:00Z", "type_3")
        self.assertIn("reversibility", str(ctx.exception).lower())

    def test_rejects_malformed_decided_at(self):
        with self.assertRaises(ValueError):
            compute_review_at("last tuesday", "type_1")


if __name__ == "__main__":
    unittest.main()
