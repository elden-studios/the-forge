"""Tests for tools/org_tree.py — pure `get_org_tree(state)` helper.

Covers: empty state, single agent, multi-root tiebreak via cabinet, live state,
tier semantics, orphan detection, rivalry edges (mutual-only, scale detection,
dedup), tree depth, uniqueness.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

from org_tree import get_org_tree  # noqa: E402


def _agent(id_, name="n", role="ic", reports_to=None, department_id="dept-x",
           title="t", rivalries=None):
    a = {
        "id": id_,
        "name": name,
        "role": role,
        "department_id": department_id,
        "title": title,
    }
    if reports_to is not None:
        a["reports_to"] = reports_to
    if rivalries is not None:
        a["rivalries"] = rivalries
    return a


class TestEmptyAndSingle(unittest.TestCase):
    def test_empty_state(self):
        tree = get_org_tree({"agents": []})
        self.assertEqual(tree, {"root": None, "orphans": [], "rivalry_edges": []})

    def test_totally_empty_dict(self):
        tree = get_org_tree({})
        self.assertIsNone(tree["root"])
        self.assertEqual(tree["orphans"], [])
        self.assertEqual(tree["rivalry_edges"], [])

    def test_single_agent_is_root(self):
        state = {"agents": [_agent("agent-a", name="A", role="executive")]}
        tree = get_org_tree(state)
        self.assertIsNotNone(tree["root"])
        self.assertEqual(tree["root"]["id"], "agent-a")
        self.assertEqual(tree["root"]["tier"], 0)
        self.assertEqual(tree["root"]["children"], [])


class TestMultiRootTiebreak(unittest.TestCase):
    def test_uses_cabinet_executives_head_when_multiple_roots(self):
        state = {
            "agents": [
                _agent("agent-a", name="A", role="executive"),
                _agent("agent-b", name="B", role="executive"),
                _agent("agent-c", name="C", role="executive"),
            ],
            "cabinet": {"executives": ["agent-b", "agent-a", "agent-c"]},
        }
        tree = get_org_tree(state)
        self.assertEqual(tree["root"]["id"], "agent-b")

    def test_falls_back_to_first_root_when_no_cabinet(self):
        state = {
            "agents": [
                _agent("agent-a", name="A"),
                _agent("agent-b", name="B"),
            ],
        }
        tree = get_org_tree(state)
        self.assertEqual(tree["root"]["id"], "agent-a")


class TestLiveState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO, "forge-state.json")) as f:
            cls.state = json.load(f)
        cls.tree = get_org_tree(cls.state)

    def test_root_is_flint(self):
        self.assertEqual(self.tree["root"]["id"], "agent-flnt")
        self.assertEqual(self.tree["root"]["tier"], 0)

    def test_tiered_structure(self):
        root = self.tree["root"]
        # Tier 0 = root
        self.assertEqual(root["tier"], 0)
        # Tier 1 = direct children
        tier1_ids = {c["id"] for c in root["children"]}
        # Per spec: 4 execs (Cade, Helix, Prism, Dune) + Lexx (IC reporting directly to CSO)
        self.assertIn("agent-cade", tier1_ids)
        self.assertIn("agent-helx", tier1_ids)
        self.assertIn("agent-prsm", tier1_ids)
        self.assertIn("agent-dune", tier1_ids)
        self.assertIn("agent-lexx", tier1_ids)
        self.assertEqual(len(tier1_ids), 5)
        # All tier-1 nodes at tier 1
        for c in root["children"]:
            self.assertEqual(c["tier"], 1)

    def test_exec_children_are_their_ic_reports(self):
        cade = next(c for c in self.tree["root"]["children"] if c["id"] == "agent-cade")
        cade_ic_ids = {c["id"] for c in cade["children"]}
        # Cade has 6 IC reports per live state
        for expected in ("agent-vexx", "agent-nyxx", "agent-echo", "agent-zeta",
                         "agent-renn", "agent-sabl"):
            self.assertIn(expected, cade_ic_ids, f"{expected} should report to Cade")
        # All at tier 2
        for c in cade["children"]:
            self.assertEqual(c["tier"], 2)

    def test_no_orphans_in_live_state(self):
        self.assertEqual(self.tree["orphans"], [])

    def test_tree_depth_is_three_tiers(self):
        # Flatten and measure max tier
        def flatten(node):
            yield node
            for c in node.get("children", []):
                yield from flatten(c)
        max_tier = max(n["tier"] for n in flatten(self.tree["root"]))
        self.assertEqual(max_tier, 2, "Current state has tiers 0, 1, 2")

    def test_no_duplicate_children(self):
        # Flatten tree and check uniqueness
        seen = set()
        def walk(node):
            self.assertNotIn(node["id"], seen, f"duplicate agent in tree: {node['id']}")
            seen.add(node["id"])
            for c in node.get("children", []):
                walk(c)
        walk(self.tree["root"])
        # All 15 agents should appear exactly once
        self.assertEqual(len(seen), 15)


class TestOrphanDetection(unittest.TestCase):
    def test_orphan_reports_to_missing_id(self):
        state = {
            "agents": [
                _agent("agent-a", name="A", role="executive"),
                _agent("agent-b", name="B", role="ic", reports_to="agent-ghost"),
            ]
        }
        tree = get_org_tree(state)
        orphan_ids = {o["id"] for o in tree["orphans"]}
        self.assertIn("agent-b", orphan_ids)
        # Orphan not in tree
        root = tree["root"]
        self.assertEqual(root["id"], "agent-a")
        self.assertEqual(root["children"], [])


class TestRivalryEdges(unittest.TestCase):
    def test_mutual_rivalry_surfaces(self):
        state = {
            "agents": [
                _agent("agent-a", role="executive", rivalries=["agent-b"]),
                _agent("agent-b", role="executive", rivalries=["agent-a"]),
            ]
        }
        tree = get_org_tree(state)
        self.assertEqual(len(tree["rivalry_edges"]), 1)
        edge = tree["rivalry_edges"][0]
        self.assertEqual({edge["a"], edge["b"]}, {"agent-a", "agent-b"})
        self.assertEqual(edge["scale"], "cabinet")

    def test_one_way_rivalry_not_surfaced(self):
        state = {
            "agents": [
                _agent("agent-a", role="executive", rivalries=["agent-b"]),
                _agent("agent-b", role="executive", rivalries=[]),
            ]
        }
        tree = get_org_tree(state)
        self.assertEqual(tree["rivalry_edges"], [])

    def test_rivalry_scale_ic(self):
        state = {
            "agents": [
                _agent("agent-a", role="ic", rivalries=["agent-b"]),
                _agent("agent-b", role="ic", rivalries=["agent-a"]),
            ]
        }
        tree = get_org_tree(state)
        self.assertEqual(len(tree["rivalry_edges"]), 1)
        self.assertEqual(tree["rivalry_edges"][0]["scale"], "ic")

    def test_rivalry_deduped(self):
        # Even though both agents list each other, only one edge emerges
        state = {
            "agents": [
                _agent("agent-a", role="executive", rivalries=["agent-b"]),
                _agent("agent-b", role="executive", rivalries=["agent-a"]),
                _agent("agent-c", role="ic", rivalries=["agent-d"]),
                _agent("agent-d", role="ic", rivalries=["agent-c"]),
            ]
        }
        tree = get_org_tree(state)
        self.assertEqual(len(tree["rivalry_edges"]), 2)

    def test_live_state_has_no_rivalries(self):
        # Rivalries are empty in current state (per watch-out note)
        with open(os.path.join(REPO, "forge-state.json")) as f:
            state = json.load(f)
        tree = get_org_tree(state)
        self.assertEqual(tree["rivalry_edges"], [])


if __name__ == "__main__":
    unittest.main()
