"""Tests for tools/platforms_catalog.py — pure helper functions.

Covers: load, schema validation, gap analysis, cost breakdown (active/dormant
tracked separately, by-category, by-agent shared-cost split), redundancy
detection (category overlap + listed alternative), tools-by-agent tagging.
"""
import json
import os
import sys
import tempfile
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

from platforms_catalog import (  # noqa: E402
    STATUSES,
    load_catalog,
    validate_catalog,
    gap_analysis,
    cost_breakdown,
    find_redundancies,
    tools_by_agent,
)


def _tool(id_, name="n", category_id="cat-x", status="active",
          cost=0, used_by=None, recommended=None, alternatives=None,
          purpose="p", vendor_url="https://x", notes=""):
    return {
        "id": id_,
        "name": name,
        "category_id": category_id,
        "purpose": purpose,
        "cost_per_month_usd": cost,
        "status": status,
        "used_by_agents": list(used_by or []),
        "recommended_for_agents": list(recommended or []),
        "alternatives": list(alternatives or []),
        "vendor_url": vendor_url,
        "notes": notes,
    }


def _cat(id_, name="n", color="#000"):
    return {"id": id_, "name": name, "color": color}


class TestLoadCatalog(unittest.TestCase):
    def test_load_catalog_reads_file(self):
        doc = {"tools": [_tool("tool-a")], "categories": [_cat("cat-x")]}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
            json.dump(doc, f)
            path = f.name
        try:
            loaded = load_catalog(path)
            self.assertEqual(loaded["tools"][0]["id"], "tool-a")
            self.assertEqual(loaded["categories"][0]["id"], "cat-x")
        finally:
            os.unlink(path)


class TestValidate(unittest.TestCase):
    def test_validate_rejects_unknown_status(self):
        doc = {
            "tools": [_tool("tool-a", status="weird")],
            "categories": [_cat("cat-x")],
        }
        with self.assertRaises(ValueError):
            validate_catalog(doc)

    def test_validate_rejects_orphan_category_id(self):
        doc = {
            "tools": [_tool("tool-a", category_id="cat-missing")],
            "categories": [_cat("cat-x")],
        }
        with self.assertRaises(ValueError):
            validate_catalog(doc)

    def test_validate_rejects_negative_cost(self):
        doc = {
            "tools": [_tool("tool-a", cost=-5)],
            "categories": [_cat("cat-x")],
        }
        with self.assertRaises(ValueError):
            validate_catalog(doc)

    def test_validate_accepts_empty_lists(self):
        doc = {
            "tools": [_tool("tool-a", used_by=[], recommended=[], alternatives=[])],
            "categories": [_cat("cat-x")],
        }
        validate_catalog(doc)  # should not raise

    def test_validate_rejects_missing_required_field(self):
        bad = {"id": "tool-b", "name": "n"}  # missing category_id, status
        doc = {"tools": [bad], "categories": [_cat("cat-x")]}
        with self.assertRaises(ValueError):
            validate_catalog(doc)

    def test_validate_accepts_float_cost(self):
        doc = {
            "tools": [_tool("tool-a", cost=12.50)],
            "categories": [_cat("cat-x")],
        }
        validate_catalog(doc)

    def test_validate_rejects_non_list_used_by_agents(self):
        bad = _tool("tool-a")
        bad["used_by_agents"] = "agent-foo"  # string, not list
        doc = {"tools": [bad], "categories": [_cat("cat-x")]}
        with self.assertRaises(ValueError):
            validate_catalog(doc)


class TestGapAnalysis(unittest.TestCase):
    def test_gap_analysis_returns_recommended_not_used(self):
        doc = {
            "tools": [
                _tool("tool-a", recommended=["agent-x"], used_by=[]),
                _tool("tool-b", recommended=["agent-x"], used_by=["agent-x"]),
            ],
            "categories": [_cat("cat-x")],
        }
        gaps = gap_analysis(doc, "agent-x")
        self.assertEqual([t["id"] for t in gaps], ["tool-a"])

    def test_gap_analysis_empty_when_all_covered(self):
        doc = {
            "tools": [
                _tool("tool-a", recommended=["agent-x"], used_by=["agent-x"]),
            ],
            "categories": [_cat("cat-x")],
        }
        self.assertEqual(gap_analysis(doc, "agent-x"), [])

    def test_gap_analysis_unknown_agent_returns_empty(self):
        doc = {
            "tools": [_tool("tool-a", recommended=["agent-x"], used_by=["agent-x"])],
            "categories": [_cat("cat-x")],
        }
        self.assertEqual(gap_analysis(doc, "agent-nope"), [])


class TestCostBreakdown(unittest.TestCase):
    def test_cost_breakdown_total_active(self):
        doc = {
            "tools": [
                _tool("tool-a", cost=10, status="active"),
                _tool("tool-b", cost=20, status="active"),
                _tool("tool-c", cost=999, status="unused"),  # excluded
            ],
            "categories": [_cat("cat-x")],
        }
        br = cost_breakdown(doc)
        self.assertEqual(br["total_active_monthly_usd"], 30)

    def test_cost_breakdown_dormant_tracked_separately(self):
        doc = {
            "tools": [
                _tool("tool-a", cost=10, status="active"),
                _tool("tool-b", cost=50, status="dormant"),
            ],
            "categories": [_cat("cat-x")],
        }
        br = cost_breakdown(doc)
        self.assertEqual(br["total_active_monthly_usd"], 10)
        self.assertEqual(br["total_dormant_monthly_usd"], 50)

    def test_cost_breakdown_by_category(self):
        doc = {
            "tools": [
                _tool("tool-a", category_id="cat-a", cost=10, status="active"),
                _tool("tool-b", category_id="cat-a", cost=15, status="active"),
                _tool("tool-c", category_id="cat-b", cost=20, status="active"),
            ],
            "categories": [_cat("cat-a"), _cat("cat-b")],
        }
        br = cost_breakdown(doc)
        self.assertEqual(br["by_category"]["cat-a"], 25)
        self.assertEqual(br["by_category"]["cat-b"], 20)

    def test_cost_breakdown_by_agent_shared_cost_split(self):
        # $30 tool used by 3 agents = $10 per agent
        doc = {
            "tools": [
                _tool("tool-a", cost=30, status="active",
                      used_by=["a1", "a2", "a3"]),
            ],
            "categories": [_cat("cat-x")],
        }
        br = cost_breakdown(doc)
        self.assertAlmostEqual(br["by_agent"]["a1"], 10.0)
        self.assertAlmostEqual(br["by_agent"]["a2"], 10.0)
        self.assertAlmostEqual(br["by_agent"]["a3"], 10.0)


class TestFindRedundancies(unittest.TestCase):
    def test_find_redundancies_category_overlap(self):
        doc = {
            "tools": [
                _tool("tool-a", category_id="cat-x", status="active"),
                _tool("tool-b", category_id="cat-x", status="active"),
            ],
            "categories": [_cat("cat-x")],
        }
        reds = find_redundancies(doc)
        kinds = {r["kind"] for r in reds}
        self.assertIn("category_overlap", kinds)

    def test_find_redundancies_listed_alternative(self):
        doc = {
            "tools": [
                _tool("tool-a", status="active", alternatives=["tool-b"]),
                _tool("tool-b", status="active"),
            ],
            "categories": [_cat("cat-x")],
        }
        reds = find_redundancies(doc)
        kinds = {r["kind"] for r in reds}
        self.assertIn("listed_alternative", kinds)

    def test_find_redundancies_empty_when_none(self):
        doc = {
            "tools": [
                _tool("tool-a", category_id="cat-x", status="active"),
                _tool("tool-b", category_id="cat-y", status="active"),
            ],
            "categories": [_cat("cat-x"), _cat("cat-y")],
        }
        self.assertEqual(find_redundancies(doc), [])

    def test_find_redundancies_ignores_dormant_category_overlap(self):
        # Dormant tools don't count as active redundancy (they're waste signal
        # elsewhere). Only active-vs-active overlaps surface here.
        doc = {
            "tools": [
                _tool("tool-a", category_id="cat-x", status="active"),
                _tool("tool-b", category_id="cat-x", status="dormant"),
            ],
            "categories": [_cat("cat-x")],
        }
        reds = find_redundancies(doc)
        self.assertEqual([r for r in reds if r["kind"] == "category_overlap"], [])


class TestToolsByAgent(unittest.TestCase):
    def test_tools_by_agent_assigned_vs_recommended_tag(self):
        doc = {
            "tools": [
                _tool("tool-a", used_by=["agent-x"], recommended=["agent-x"]),
                _tool("tool-b", used_by=[], recommended=["agent-x"]),
                _tool("tool-c", used_by=["agent-y"], recommended=["agent-y"]),
            ],
            "categories": [_cat("cat-x")],
        }
        out = tools_by_agent(doc, "agent-x")
        by_id = {t["id"]: t for t in out}
        self.assertIn("tool-a", by_id)
        self.assertIn("tool-b", by_id)
        self.assertNotIn("tool-c", by_id)
        self.assertEqual(by_id["tool-a"]["assignment"], "assigned")
        self.assertEqual(by_id["tool-b"]["assignment"], "recommended")


class TestStatusEnum(unittest.TestCase):
    def test_statuses_frozen(self):
        self.assertEqual(STATUSES, frozenset({"active", "dormant", "unused"}))


if __name__ == "__main__":
    unittest.main()
