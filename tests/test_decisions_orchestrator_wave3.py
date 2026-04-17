"""Wave 3 additions to the Decision Log library.

Covers upsert semantics on the pure append_decision(doc, decision) entry point,
persistence wrappers (close/reverse_decision_persist), query helpers, and
heatmap bucket logic. Subsequent Wave 3 sub-tasks will extend this file.
"""
import unittest

from tools.decisions_orchestrator import (
    append_decision,
)


class TestAppendDecisionUpsert(unittest.TestCase):
    def _base_doc(self):
        return {"decisions": [], "project_decision_index": {}}

    def _decision(self, **overrides):
        base = {
            "id": "dec-11111111",
            "title": "GO at 75% — Saudi PropTech",
            "context": "Phase 1.5 produced a 5-lens verdict.",
            "alternatives_considered": ["NO-GO", "ITERATE"],
            "decided_by": "agent-cade",
            "dissenting": ["agent-prsm"],
            "dissent_reason": "Unit economics break below SAR 500K",
            "decided_at": "2026-04-17T10:31:24Z",
            "reversibility": "type_1",
            "review_at": "2026-07-16T10:31:24Z",
            "project_id": "proj-simulation",
            "related_evidence": [],
            "status": "open",
        }
        base.update(overrides)
        return base

    def test_append_is_idempotent_on_same_minute(self):
        """Two appends with identical (title, decided_by, project_id) within 60s are a no-op on the second."""
        doc = self._base_doc()
        d1 = self._decision(id="dec-aaaaaaaa", decided_at="2026-04-17T10:31:24Z")
        d2 = self._decision(id="dec-bbbbbbbb", decided_at="2026-04-17T10:31:48Z")  # +24s
        append_decision(doc, d1)
        append_decision(doc, d2)
        self.assertEqual(len(doc["decisions"]), 1, "upsert should dedupe within 60s")
        self.assertEqual(doc["decisions"][0]["id"], "dec-aaaaaaaa", "first write wins")

    def test_append_across_60s_boundary_creates_two(self):
        doc = self._base_doc()
        d1 = self._decision(id="dec-aaaaaaaa", decided_at="2026-04-17T10:31:24Z")
        d2 = self._decision(id="dec-bbbbbbbb", decided_at="2026-04-17T10:32:25Z")  # +61s
        append_decision(doc, d1)
        append_decision(doc, d2)
        self.assertEqual(len(doc["decisions"]), 2)

    def test_append_different_title_creates_two(self):
        doc = self._base_doc()
        d1 = self._decision(id="dec-aaaaaaaa", title="First")
        d2 = self._decision(id="dec-bbbbbbbb", title="Second")
        append_decision(doc, d1)
        append_decision(doc, d2)
        self.assertEqual(len(doc["decisions"]), 2)

    def test_append_different_decider_creates_two(self):
        doc = self._base_doc()
        d1 = self._decision(id="dec-aaaaaaaa", decided_by="agent-cade")
        d2 = self._decision(id="dec-bbbbbbbb", decided_by="agent-helx")
        append_decision(doc, d1)
        append_decision(doc, d2)
        self.assertEqual(len(doc["decisions"]), 2)

    def test_append_different_project_creates_two(self):
        doc = self._base_doc()
        d1 = self._decision(id="dec-aaaaaaaa", project_id="proj-a")
        d2 = self._decision(id="dec-bbbbbbbb", project_id="proj-b")
        append_decision(doc, d1)
        append_decision(doc, d2)
        self.assertEqual(len(doc["decisions"]), 2)

    def test_append_updates_project_decision_index(self):
        """Pure append must also maintain the project_decision_index entry."""
        doc = self._base_doc()
        d = self._decision(id="dec-cccccccc", project_id="proj-zeta")
        append_decision(doc, d)
        self.assertIn("proj-zeta", doc["project_decision_index"])
        self.assertIn("dec-cccccccc", doc["project_decision_index"]["proj-zeta"])

    def test_append_with_existing_id_is_noop(self):
        """Dedup by id (existing W2 behavior preserved at pure layer)."""
        doc = self._base_doc()
        d = self._decision(id="dec-dddddddd")
        append_decision(doc, d)
        append_decision(doc, d)
        self.assertEqual(len(doc["decisions"]), 1)

    def test_append_handles_mixed_tz_awareness_without_crashing(self):
        """Regression: pure append must not crash when the doc has a naive decided_at
        and the incoming decision is tz-aware (or vice versa). Both should be treated
        as UTC for the 60s collapse comparison — matches compute_review_at convention.
        """
        doc = {
            "decisions": [self._decision(id="dec-aaaaaaaa", decided_at="2026-04-17T10:31:24")],  # naive
            "project_decision_index": {"proj-simulation": ["dec-aaaaaaaa"]},
        }
        # Incoming is tz-aware (Z); naive existing is treated as UTC, so delta = 6s → collapse
        d_aware = self._decision(id="dec-bbbbbbbb", decided_at="2026-04-17T10:31:30Z")
        append_decision(doc, d_aware)  # must not raise TypeError
        self.assertEqual(len(doc["decisions"]), 1, "naive+aware within 60s should still collapse (treated as UTC)")
        self.assertEqual(doc["decisions"][0]["id"], "dec-aaaaaaaa", "first-write-wins preserved")

    def test_append_naive_vs_aware_beyond_60s_keeps_both(self):
        """Regression flip-side: naive doc + tz-aware incoming, >60s apart → both stored."""
        doc = {
            "decisions": [self._decision(id="dec-aaaaaaaa", decided_at="2026-04-17T10:31:24")],  # naive
            "project_decision_index": {"proj-simulation": ["dec-aaaaaaaa"]},
        }
        d_aware = self._decision(id="dec-bbbbbbbb", decided_at="2026-04-17T10:33:00Z")  # +96s
        append_decision(doc, d_aware)
        self.assertEqual(len(doc["decisions"]), 2)


if __name__ == "__main__":
    unittest.main()
