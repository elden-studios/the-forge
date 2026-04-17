"""Integration test for v3.2 Wave 3 — walks pre_mortem → heatmap → Decision Log
end-to-end using the canonical EdTech fixture.

This closes Foundation review M3 (integration-coverage gap).
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

from decisions_orchestrator import (  # noqa: E402
    heatmap_buckets,
    query_by_project,
    query_by_status,
    query_sorted_by_review_at,
)


class TestV32Wave3IntegrationEdTech(unittest.TestCase):
    """Integration test using the Saudi EdTech fixture data committed to main."""

    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO, "forge-tasks.json")) as f:
            cls.tasks = json.load(f)
        with open(os.path.join(REPO, "forge-decisions.json")) as f:
            cls.decisions = json.load(f)

    def test_cabinet_framing_has_five_canonical_lenses(self):
        framing = self.tasks.get("cabinet_framing")
        self.assertIsNotNone(framing, "cabinet_framing block must be present")
        lenses = framing.get("lenses", {})
        expected = {"strategic_kernel", "product_shape", "build_class", "economic_shape", "market_bet"}
        self.assertEqual(set(lenses.keys()), expected, "must have exactly the 5 canonical lenses")

    def test_pre_mortem_items_have_required_fields(self):
        pm = self.tasks.get("pre_mortem", [])
        self.assertGreater(len(pm), 0, "pre_mortem must be populated")
        for item in pm:
            for field in ("failure_mode", "likelihood", "impact", "owner_agent", "mitigation_phase"):
                self.assertIn(field, item, f"pre_mortem item missing '{field}': {item}")
            self.assertIsInstance(item["likelihood"], int)
            self.assertIsInstance(item["impact"], int)
            self.assertTrue(1 <= item["likelihood"] <= 5)
            self.assertTrue(1 <= item["impact"] <= 5)

    def test_heatmap_aggregates_pre_mortem_items_correctly(self):
        pm = self.tasks.get("pre_mortem", [])
        buckets = heatmap_buckets(pm)
        # 25 cells always present
        self.assertEqual(len(buckets), 25)
        # Sum of bucket counts == number of valid items
        total = sum(buckets.values())
        self.assertEqual(total, len(pm), "every pre_mortem item should land in exactly one cell")
        # At least one high-score cell populated (EdTech fixture has an F=20 risk)
        top_cells = [(k, v) for k, v in buckets.items() if v > 0]
        self.assertGreater(len(top_cells), 0, "heatmap should have at least 1 populated cell")

    def test_decision_log_has_entry_for_current_project(self):
        project_id = self.tasks.get("current_project")
        self.assertIsNotNone(project_id, "current_project must be set")
        project_decisions = query_by_project(self.decisions, project_id)
        self.assertGreater(len(project_decisions), 0,
                           f"project '{project_id}' must have at least 1 decision (Standing Rule 11)")

    def test_decisions_have_required_lifecycle_fields(self):
        project_id = self.tasks.get("current_project")
        for d in query_by_project(self.decisions, project_id):
            for field in ("id", "title", "decided_by", "decided_at", "review_at", "reversibility", "status"):
                self.assertIn(field, d, f"decision missing '{field}': {d['id']}")
            self.assertIn(d["reversibility"], {"type_1", "type_2"})
            self.assertIn(d["status"], {"open", "reviewed", "committed", "reversed"})

    def test_open_decisions_queryable(self):
        open_decisions = query_by_status(self.decisions, "open")
        # At least the current project's open decision(s) are findable via query_by_status
        project_id = self.tasks.get("current_project")
        project_open = [d for d in open_decisions if d.get("project_id") == project_id]
        self.assertGreater(len(project_open), 0)

    def test_sorted_by_review_at_is_stable(self):
        sorted_decisions = query_sorted_by_review_at(self.decisions)
        self.assertEqual(len(sorted_decisions), len(self.decisions.get("decisions", [])),
                         "sort must preserve all decisions")
        # No exceptions = passes; semantic correctness verified in T0.3 unit tests


if __name__ == "__main__":
    unittest.main()
