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


import json
import tempfile


class TestAppendDecision(unittest.TestCase):
    def test_appends_to_empty_file(self):
        from decisions_orchestrator import append_decision
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-decisions.json")
            with open(path, "w") as f:
                json.dump({"decisions": [], "project_decision_index": {}}, f)

            decision = {
                "id": "dec-00000001",
                "title": "Ship Saudi neobank MVP",
                "context": "Phase 1.5 Cabinet Framing",
                "alternatives_considered": [],
                "decided_by": "agent-cade",
                "dissenting": [],
                "dissent_reason": "",
                "decided_at": "2026-04-17T00:00:00Z",
                "reversibility": "type_1",
                "review_at": "2026-07-16T00:00:00Z",
                "project_id": "proj-test",
                "related_evidence": [],
                "status": "open"
            }
            append_decision("proj-test", decision, path)

            with open(path) as f:
                doc = json.load(f)
            self.assertEqual(len(doc["decisions"]), 1)
            self.assertEqual(doc["project_decision_index"]["proj-test"], ["dec-00000001"])

    def test_existing_project_decisions_extend_not_replace(self):
        from decisions_orchestrator import append_decision
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-decisions.json")
            with open(path, "w") as f:
                json.dump({
                    "decisions": [{"id": "dec-old00000"}],
                    "project_decision_index": {"proj-x": ["dec-old00000"]},
                }, f)
            new_decision = {
                "id": "dec-new00000",
                "title": "t", "context": "c", "alternatives_considered": [],
                "decided_by": "agent-flnt", "dissenting": [], "dissent_reason": "",
                "decided_at": "2026-04-17T00:00:00Z", "reversibility": "type_2",
                "review_at": "2026-05-17T00:00:00Z", "project_id": "proj-x",
                "related_evidence": [], "status": "open"
            }
            append_decision("proj-x", new_decision, path)

            with open(path) as f:
                doc = json.load(f)
            self.assertEqual(
                set(doc["project_decision_index"]["proj-x"]),
                {"dec-old00000", "dec-new00000"},
            )

    def test_append_decision_mirrors_to_assets_when_next_to_root(self):
        """When forge-decisions.json lives next to assets/, mirror atomically."""
        from decisions_orchestrator import append_decision
        with tempfile.TemporaryDirectory() as tmp:
            root_path = os.path.join(tmp, "forge-decisions.json")
            with open(root_path, "w") as f:
                json.dump({"decisions": [], "project_decision_index": {}}, f)
            assets_dir = os.path.join(tmp, "assets")
            os.makedirs(assets_dir)
            mirror_path = os.path.join(assets_dir, "forge-decisions.json")
            with open(mirror_path, "w") as f:
                json.dump({"decisions": [], "project_decision_index": {}}, f)

            decision = {
                "id": "dec-mirror01",
                "title": "Mirror test", "context": "", "alternatives_considered": [],
                "decided_by": "agent-flnt", "dissenting": [], "dissent_reason": "",
                "decided_at": "2026-04-17T00:00:00Z", "reversibility": "type_1",
                "review_at": "2026-07-16T00:00:00Z", "project_id": "proj-mirror",
                "related_evidence": [], "status": "open"
            }
            append_decision("proj-mirror", decision, root_path)

            with open(root_path) as f:
                root_doc = json.load(f)
            with open(mirror_path) as f:
                mirror_doc = json.load(f)
            self.assertEqual(len(root_doc["decisions"]), 1)
            self.assertEqual(len(mirror_doc["decisions"]), 1)
            self.assertEqual(
                root_doc["project_decision_index"],
                mirror_doc["project_decision_index"],
            )

    def test_append_decision_no_mirror_when_assets_missing(self):
        """If no assets/ sibling exists, no mirror is attempted — must not crash."""
        from decisions_orchestrator import append_decision
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-decisions.json")
            with open(path, "w") as f:
                json.dump({"decisions": [], "project_decision_index": {}}, f)
            decision = {
                "id": "dec-solo0001",
                "title": "Solo test", "context": "", "alternatives_considered": [],
                "decided_by": "agent-flnt", "dissenting": [], "dissent_reason": "",
                "decided_at": "2026-04-17T00:00:00Z", "reversibility": "type_2",
                "review_at": "2026-05-17T00:00:00Z", "project_id": "proj-solo",
                "related_evidence": [], "status": "open"
            }
            append_decision("proj-solo", decision, path)
            with open(path) as f:
                doc = json.load(f)
            self.assertEqual(len(doc["decisions"]), 1)

    def test_append_decision_is_atomic(self):
        """Persistence must survive mid-write failure — tempfile + rename pattern."""
        import glob
        from decisions_orchestrator import append_decision
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-decisions.json")
            with open(path, "w") as f:
                json.dump({"decisions": [], "project_decision_index": {}}, f)
            decision = {
                "id": "dec-atomic00",
                "title": "Atomic", "context": "", "alternatives_considered": [],
                "decided_by": "agent-flnt", "dissenting": [], "dissent_reason": "",
                "decided_at": "2026-04-17T00:00:00Z", "reversibility": "type_1",
                "review_at": "2026-07-16T00:00:00Z", "project_id": "proj-atomic",
                "related_evidence": [], "status": "open"
            }
            append_decision("proj-atomic", decision, path)
            tmps = glob.glob(os.path.join(tmp, "*.tmp"))
            self.assertEqual(tmps, [], f"stray tmp files: {tmps}")


class TestReviewDecisionsDue(unittest.TestCase):
    def test_returns_empty_when_none_due(self):
        from decisions_orchestrator import review_decisions_due
        doc = {
            "decisions": [
                {"id": "dec-future001", "status": "open", "review_at": "2027-01-01T00:00:00Z"}
            ],
            "project_decision_index": {}
        }
        due = review_decisions_due(doc, now_iso="2026-04-17T00:00:00Z")
        self.assertEqual(due, [])

    def test_returns_decisions_past_review_at(self):
        from decisions_orchestrator import review_decisions_due
        doc = {
            "decisions": [
                {"id": "dec-due000001", "status": "open", "review_at": "2026-01-01T00:00:00Z"},
                {"id": "dec-future002", "status": "open", "review_at": "2027-01-01T00:00:00Z"},
            ],
            "project_decision_index": {}
        }
        due = review_decisions_due(doc, now_iso="2026-04-17T00:00:00Z")
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]["id"], "dec-due000001")

    def test_skips_already_reviewed_decisions(self):
        """A decision with status != open is not 'due' even if review_at has passed."""
        from decisions_orchestrator import review_decisions_due
        doc = {
            "decisions": [
                {"id": "dec-closed0001", "status": "reviewed", "review_at": "2026-01-01T00:00:00Z"},
                {"id": "dec-committed1", "status": "committed", "review_at": "2026-01-01T00:00:00Z"},
                {"id": "dec-reversed01", "status": "reversed", "review_at": "2026-01-01T00:00:00Z"},
            ],
            "project_decision_index": {}
        }
        due = review_decisions_due(doc, now_iso="2026-04-17T00:00:00Z")
        self.assertEqual(due, [])


class TestCloseDecision(unittest.TestCase):
    def test_transitions_open_to_reviewed(self):
        from decisions_orchestrator import close_decision
        doc = {
            "decisions": [{"id": "dec-abc00001", "status": "open"}],
            "project_decision_index": {}
        }
        close_decision(doc, "dec-abc00001", "reviewed")
        self.assertEqual(doc["decisions"][0]["status"], "reviewed")

    def test_transitions_open_to_committed(self):
        from decisions_orchestrator import close_decision
        doc = {
            "decisions": [{"id": "dec-commit001", "status": "open"}],
            "project_decision_index": {}
        }
        close_decision(doc, "dec-commit001", "committed")
        self.assertEqual(doc["decisions"][0]["status"], "committed")

    def test_rejects_unknown_status(self):
        from decisions_orchestrator import close_decision
        doc = {
            "decisions": [{"id": "dec-abc00002", "status": "open"}],
            "project_decision_index": {}
        }
        with self.assertRaises(ValueError) as ctx:
            close_decision(doc, "dec-abc00002", "maybe")
        self.assertIn("status", str(ctx.exception).lower())

    def test_rejects_nonexistent_decision_id(self):
        from decisions_orchestrator import close_decision
        doc = {"decisions": [], "project_decision_index": {}}
        with self.assertRaises(KeyError) as ctx:
            close_decision(doc, "dec-ghost000", "reviewed")
        self.assertIn("dec-ghost000", str(ctx.exception))


class TestReverseDecision(unittest.TestCase):
    def test_marks_decision_reversed_and_links_successor(self):
        from decisions_orchestrator import reverse_decision
        doc = {
            "decisions": [
                {"id": "dec-orig00001", "status": "open"},
                {"id": "dec-succ00001", "status": "open"},
            ],
            "project_decision_index": {}
        }
        reverse_decision(doc, "dec-orig00001", successor_id="dec-succ00001")
        self.assertEqual(doc["decisions"][0]["status"], "reversed")
        self.assertEqual(doc["decisions"][0].get("reversed_by"), "dec-succ00001")

    def test_rejects_nonexistent_successor(self):
        from decisions_orchestrator import reverse_decision
        doc = {
            "decisions": [{"id": "dec-orig00002", "status": "open"}],
            "project_decision_index": {}
        }
        with self.assertRaises(KeyError) as ctx:
            reverse_decision(doc, "dec-orig00002", successor_id="dec-ghost000")
        self.assertIn("successor", str(ctx.exception).lower())

    def test_rejects_reversing_already_reversed_decision(self):
        from decisions_orchestrator import reverse_decision
        doc = {
            "decisions": [
                {"id": "dec-orig00003", "status": "reversed"},
                {"id": "dec-succ00003", "status": "open"},
            ],
            "project_decision_index": {}
        }
        with self.assertRaises(ValueError) as ctx:
            reverse_decision(doc, "dec-orig00003", successor_id="dec-succ00003")
        self.assertIn("already reversed", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
