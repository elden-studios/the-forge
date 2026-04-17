"""Integration test for Sub-project E — validates the committed
forge-platforms.json against the live forge-state.json.

Asserts:
- Schema validates
- ≥10 tools across ≥5 categories
- ≥1 intentional gap (demo value)
- ≥1 intentional redundancy
- Total active monthly cost is in a reasonable window
- Every tool's used_by_agents / recommended_for_agents references a real
  agent id from forge-state.json (no orphan agent refs)
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

from platforms_catalog import (  # noqa: E402
    load_catalog,
    validate_catalog,
    gap_analysis,
    cost_breakdown,
    find_redundancies,
)


class TestSubprojectEPlatformsLive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = load_catalog(os.path.join(REPO, "forge-platforms.json"))
        with open(os.path.join(REPO, "forge-state.json")) as f:
            cls.state = json.load(f)
        cls.agent_ids = {a["id"] for a in cls.state["agents"]}

    def test_schema_validates(self):
        validate_catalog(self.catalog)  # must not raise

    def test_has_enough_tools(self):
        tools = self.catalog["tools"]
        self.assertGreaterEqual(
            len(tools), 10,
            f"seed catalog should have at least 10 tools, got {len(tools)}"
        )

    def test_has_enough_categories(self):
        cats = self.catalog["categories"]
        self.assertGreaterEqual(
            len(cats), 5,
            f"seed catalog should have at least 5 categories, got {len(cats)}"
        )

    def test_has_at_least_one_gap(self):
        """At least one agent should have a gap (recommended but not using).
        Makes the dashboard's gap-chip UX meaningful on first load."""
        total_gaps = 0
        for aid in self.agent_ids:
            total_gaps += len(gap_analysis(self.catalog, aid))
        self.assertGreaterEqual(
            total_gaps, 1,
            "seed should have at least 1 intentional gap for demo value"
        )

    def test_has_at_least_one_redundancy(self):
        """At least one redundancy (category_overlap or listed_alternative)
        so the redundancy-detection UX has signal."""
        reds = find_redundancies(self.catalog)
        self.assertGreaterEqual(
            len(reds), 1,
            "seed should have at least 1 intentional redundancy for demo value"
        )

    def test_total_active_cost_in_reasonable_window(self):
        br = cost_breakdown(self.catalog)
        total = br["total_active_monthly_usd"]
        self.assertGreater(
            total, 100,
            f"total active cost ${total}/mo is suspiciously low — seed data?"
        )
        self.assertLess(
            total, 10000,
            f"total active cost ${total}/mo exceeds 10K budget sanity"
        )

    def test_every_used_by_agent_is_a_real_agent(self):
        """No orphan agent references in used_by_agents."""
        for tool in self.catalog["tools"]:
            for aid in tool.get("used_by_agents", []):
                self.assertIn(
                    aid, self.agent_ids,
                    f"tool {tool['id']}.used_by_agents references unknown "
                    f"agent id {aid!r}"
                )

    def test_every_recommended_agent_is_a_real_agent(self):
        """No orphan agent references in recommended_for_agents."""
        for tool in self.catalog["tools"]:
            for aid in tool.get("recommended_for_agents", []):
                self.assertIn(
                    aid, self.agent_ids,
                    f"tool {tool['id']}.recommended_for_agents references "
                    f"unknown agent id {aid!r}"
                )

    def test_assets_mirror_matches_root(self):
        """assets/forge-platforms.json must mirror forge-platforms.json."""
        root = load_catalog(os.path.join(REPO, "forge-platforms.json"))
        mirror = load_catalog(os.path.join(REPO, "assets", "forge-platforms.json"))
        self.assertEqual(root, mirror,
                         "assets/forge-platforms.json drifted from root — "
                         "update both")


if __name__ == "__main__":
    unittest.main()
