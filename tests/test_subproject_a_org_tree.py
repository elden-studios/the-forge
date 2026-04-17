"""Integration test for Sub-project A — validates get_org_tree() against the
live forge-state.json committed to main.

Per spec: root is agent-flnt, tier-1 children are the 4 reporting execs
(cade, helx, prsm, dune) plus Lexx (legal IC reporting directly to CSO),
total 15 agents, no orphans.
"""
import json
import os
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "tools"))

from org_tree import get_org_tree  # noqa: E402


class TestSubprojectAOrgTreeLiveState(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(os.path.join(REPO, "forge-state.json")) as f:
            cls.state = json.load(f)
        cls.tree = get_org_tree(cls.state)

    def test_root_is_flint(self):
        self.assertIsNotNone(self.tree["root"])
        self.assertEqual(self.tree["root"]["id"], "agent-flnt")
        self.assertEqual(self.tree["root"]["tier"], 0)

    def test_tier1_is_four_execs_plus_lexx(self):
        tier1_ids = {c["id"] for c in self.tree["root"]["children"]}
        expected = {"agent-cade", "agent-helx", "agent-prsm", "agent-dune", "agent-lexx"}
        self.assertEqual(tier1_ids, expected,
                         "tier-1 must be 4 reporting execs + Lexx (legal IC under CSO)")

    def test_total_node_count_is_fifteen(self):
        def flatten(node):
            yield node
            for c in node.get("children", []):
                yield from flatten(c)
        total = sum(1 for _ in flatten(self.tree["root"]))
        self.assertEqual(total, 15, "all 15 agents should appear in the tree")
        self.assertEqual(total, len(self.state["agents"]),
                         "tree size should equal agent count")

    def test_no_orphans(self):
        self.assertEqual(self.tree["orphans"], [],
                         "live state should have no orphaned agents")


if __name__ == "__main__":
    unittest.main()
