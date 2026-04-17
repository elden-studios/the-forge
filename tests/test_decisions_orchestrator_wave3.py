"""Wave 3 additions to the Decision Log library.

Covers upsert semantics on the pure append_decision(doc, decision) entry point,
persistence wrappers (close/reverse_decision_persist), query helpers, and
heatmap bucket logic. Subsequent Wave 3 sub-tasks will extend this file.
"""
import json
import os
import tempfile
import unittest

from tools.decisions_orchestrator import (
    append_decision,
    close_decision_persist,
    reverse_decision_persist,
)


def _sample_doc():
    return {
        "decisions": [
            {
                "id": "dec-aaaaaaaa",
                "title": "Original",
                "context": "c",
                "alternatives_considered": [],
                "decided_by": "agent-cade",
                "dissenting": [],
                "dissent_reason": "",
                "decided_at": "2026-04-17T10:00:00Z",
                "reversibility": "type_1",
                "review_at": "2026-07-16T10:00:00Z",
                "project_id": "proj-x",
                "related_evidence": [],
                "status": "open",
            },
            {
                "id": "dec-bbbbbbbb",
                "title": "Successor",
                "context": "c2",
                "alternatives_considered": [],
                "decided_by": "agent-cade",
                "dissenting": [],
                "dissent_reason": "",
                "decided_at": "2026-04-17T11:00:00Z",
                "reversibility": "type_1",
                "review_at": "2026-07-16T11:00:00Z",
                "project_id": "proj-x",
                "related_evidence": [],
                "status": "open",
            },
        ],
        "project_decision_index": {"proj-x": ["dec-aaaaaaaa", "dec-bbbbbbbb"]},
    }


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


class TestCloseDecisionPersist(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "forge-decisions.json")
        self.assets_dir = os.path.join(self.tmpdir, "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        self.mirror_path = os.path.join(self.assets_dir, "forge-decisions.json")
        doc = _sample_doc()
        with open(self.path, "w") as f:
            json.dump(doc, f)
        with open(self.mirror_path, "w") as f:
            json.dump(doc, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_close_default_status_is_committed(self):
        close_decision_persist(self.path, "dec-aaaaaaaa")
        with open(self.path) as f:
            primary = json.load(f)
        self.assertEqual(primary["decisions"][0]["status"], "committed")

    def test_close_updates_primary_and_mirror(self):
        close_decision_persist(self.path, "dec-aaaaaaaa", new_status="reviewed")
        with open(self.path) as f:
            primary = json.load(f)
        with open(self.mirror_path) as f:
            mirror = json.load(f)
        self.assertEqual(primary["decisions"][0]["status"], "reviewed")
        self.assertEqual(mirror["decisions"][0]["status"], "reviewed")

    def test_close_propagates_value_error_on_bad_status(self):
        with self.assertRaises(ValueError):
            close_decision_persist(self.path, "dec-aaaaaaaa", new_status="not-a-real-status")

    def test_close_propagates_key_error_on_missing_decision(self):
        with self.assertRaises(KeyError):
            close_decision_persist(self.path, "dec-does-not-exist")

    def test_close_rejects_terminal_state_transition(self):
        close_decision_persist(self.path, "dec-aaaaaaaa", new_status="committed")
        with self.assertRaises(ValueError):
            close_decision_persist(self.path, "dec-aaaaaaaa", new_status="reviewed")

    def test_close_preserves_primary_on_failure(self):
        """Atomicity: ValueError/KeyError from pure function must leave disk untouched."""
        with open(self.path) as f:
            before = f.read()
        with self.assertRaises(KeyError):
            close_decision_persist(self.path, "dec-does-not-exist")
        with open(self.path) as f:
            after = f.read()
        self.assertEqual(before, after, "primary file mutated on pure-function failure")

    def test_close_without_assets_dir_does_not_crash(self):
        """If the assets/ sibling doesn't exist, persist primary only (no crash)."""
        import shutil
        shutil.rmtree(self.assets_dir, ignore_errors=True)
        close_decision_persist(self.path, "dec-aaaaaaaa", new_status="committed")
        with open(self.path) as f:
            primary = json.load(f)
        self.assertEqual(primary["decisions"][0]["status"], "committed")

    def test_close_new_status_is_keyword_only(self):
        """Regression: new_status must be keyword-only to prevent footgun where
        a third positional arg gets silently interpreted as a status string."""
        with self.assertRaises(TypeError):
            # Positional third arg should fail at function-call layer, before
            # reaching the pure close_decision (which would raise ValueError).
            close_decision_persist(self.path, "dec-aaaaaaaa", "committed")


class TestReverseDecisionPersist(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.path = os.path.join(self.tmpdir, "forge-decisions.json")
        self.assets_dir = os.path.join(self.tmpdir, "assets")
        os.makedirs(self.assets_dir, exist_ok=True)
        self.mirror_path = os.path.join(self.assets_dir, "forge-decisions.json")
        doc = _sample_doc()
        with open(self.path, "w") as f:
            json.dump(doc, f)
        with open(self.mirror_path, "w") as f:
            json.dump(doc, f)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_reverse_sets_status_and_reversed_by(self):
        reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-bbbbbbbb")
        with open(self.path) as f:
            primary = json.load(f)
        self.assertEqual(primary["decisions"][0]["status"], "reversed")
        self.assertEqual(primary["decisions"][0]["reversed_by"], "dec-bbbbbbbb")

    def test_reverse_updates_mirror(self):
        reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-bbbbbbbb")
        with open(self.mirror_path) as f:
            mirror = json.load(f)
        self.assertEqual(mirror["decisions"][0]["status"], "reversed")
        self.assertEqual(mirror["decisions"][0]["reversed_by"], "dec-bbbbbbbb")

    def test_reverse_rejects_self_reference(self):
        with self.assertRaises(ValueError):
            reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-aaaaaaaa")

    def test_reverse_rejects_missing_successor(self):
        with self.assertRaises(KeyError):
            reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-does-not-exist")

    def test_reverse_rejects_already_reversed(self):
        reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-bbbbbbbb")
        with self.assertRaises(ValueError):
            reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-bbbbbbbb")

    def test_reverse_preserves_primary_on_failure(self):
        with open(self.path) as f:
            before = f.read()
        with self.assertRaises(KeyError):
            reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-does-not-exist")
        with open(self.path) as f:
            after = f.read()
        self.assertEqual(before, after)

    def test_reverse_without_assets_dir_does_not_crash(self):
        import shutil
        shutil.rmtree(self.assets_dir, ignore_errors=True)
        reverse_decision_persist(self.path, "dec-aaaaaaaa", successor_id="dec-bbbbbbbb")
        with open(self.path) as f:
            primary = json.load(f)
        self.assertEqual(primary["decisions"][0]["status"], "reversed")


from datetime import datetime, timezone, timedelta

from tools.decisions_orchestrator import (
    query_by_project,
    query_by_status,
    query_due_soon,
    query_sorted_by_review_at,
)


class TestQueryHelpers(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 4, 17, 10, 0, 0, tzinfo=timezone.utc)
        self.doc = {
            "decisions": [
                {"id": "dec-a", "project_id": "proj-1", "status": "open",
                 "review_at": (self.now + timedelta(days=10)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "title": "A", "decided_by": "agent-cade", "reversibility": "type_1"},
                {"id": "dec-b", "project_id": "proj-1", "status": "committed",
                 "review_at": (self.now + timedelta(days=100)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "title": "B", "decided_by": "agent-helx", "reversibility": "type_2"},
                {"id": "dec-c", "project_id": "proj-2", "status": "open",
                 "review_at": (self.now + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "title": "C", "decided_by": "agent-cade", "reversibility": "type_1"},
                {"id": "dec-d", "project_id": "proj-2", "status": "reversed",
                 "review_at": (self.now - timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "title": "D", "decided_by": "agent-flnt", "reversibility": "type_2"},
                {"id": "dec-e", "project_id": "proj-2", "status": "reviewed",
                 "review_at": (self.now + timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "title": "E", "decided_by": "agent-cade", "reversibility": "type_1"},
            ],
            "project_decision_index": {
                "proj-1": ["dec-a", "dec-b"],
                "proj-2": ["dec-c", "dec-d", "dec-e"],
            },
        }

    def test_query_by_project_returns_matching_decisions(self):
        rows = query_by_project(self.doc, "proj-1")
        self.assertEqual([r["id"] for r in rows], ["dec-a", "dec-b"])

    def test_query_by_project_preserves_insertion_order(self):
        rows = query_by_project(self.doc, "proj-2")
        self.assertEqual([r["id"] for r in rows], ["dec-c", "dec-d", "dec-e"])

    def test_query_by_project_unknown_returns_empty(self):
        self.assertEqual(query_by_project(self.doc, "proj-999"), [])

    def test_query_by_status_open(self):
        rows = query_by_status(self.doc, "open")
        self.assertEqual(sorted([r["id"] for r in rows]), ["dec-a", "dec-c"])

    def test_query_by_status_reviewed(self):
        rows = query_by_status(self.doc, "reviewed")
        self.assertEqual([r["id"] for r in rows], ["dec-e"])

    def test_query_by_status_rejects_unknown_status(self):
        with self.assertRaises(ValueError):
            query_by_status(self.doc, "nonsense")

    def test_query_due_soon_default_30d_only_includes_open(self):
        rows = query_due_soon(self.doc, now=self.now, horizon_days=30)
        # open: a(+10d), c(+5d). Reviewed (e), committed (b), reversed (d) excluded regardless of window.
        self.assertEqual(sorted([r["id"] for r in rows]), ["dec-a", "dec-c"])

    def test_query_due_soon_excludes_non_open_even_in_window(self):
        """Reviewed/committed/reversed decisions are excluded even if review_at is near."""
        rows = query_due_soon(self.doc, now=self.now, horizon_days=365)
        # a, c = open & in-window; e = reviewed (excluded); b = committed (excluded); d = reversed (excluded)
        self.assertEqual(sorted([r["id"] for r in rows]), ["dec-a", "dec-c"])

    def test_query_due_soon_includes_overdue_open(self):
        """An open decision with review_at in the past is still 'due'."""
        overdue_doc = {
            "decisions": [
                {"id": "dec-overdue", "project_id": "proj-x", "status": "open",
                 "review_at": (self.now - timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "title": "Overdue", "decided_by": "agent-cade", "reversibility": "type_1"},
            ],
            "project_decision_index": {"proj-x": ["dec-overdue"]},
        }
        rows = query_due_soon(overdue_doc, now=self.now, horizon_days=1)
        self.assertEqual([r["id"] for r in rows], ["dec-overdue"])

    def test_query_due_soon_handles_naive_review_at(self):
        """Naive review_at values should be treated as UTC — matches _to_naive_utc convention."""
        mixed_doc = {
            "decisions": [
                {"id": "dec-naive", "project_id": "proj-x", "status": "open",
                 "review_at": "2026-04-20T10:00:00",  # naive; +3 days at UTC
                 "title": "N", "decided_by": "agent-cade", "reversibility": "type_1"},
            ],
            "project_decision_index": {"proj-x": ["dec-naive"]},
        }
        rows = query_due_soon(mixed_doc, now=self.now, horizon_days=7)
        self.assertEqual([r["id"] for r in rows], ["dec-naive"])

    def test_query_sorted_by_review_at_asc(self):
        rows = query_sorted_by_review_at(self.doc)
        # Ascending: d(-2d), c(+5d), e(+7d), a(+10d), b(+100d)
        self.assertEqual([r["id"] for r in rows], ["dec-d", "dec-c", "dec-e", "dec-a", "dec-b"])

    def test_query_sorted_by_review_at_desc(self):
        rows = query_sorted_by_review_at(self.doc, reverse=True)
        self.assertEqual([r["id"] for r in rows], ["dec-b", "dec-a", "dec-e", "dec-c", "dec-d"])

    def test_query_sorted_missing_review_at_goes_to_end(self):
        """Decisions with missing/malformed review_at sort to end in either direction."""
        doc = {
            "decisions": [
                {"id": "dec-none", "project_id": "p", "status": "open"},  # no review_at
                {"id": "dec-a", "project_id": "p", "status": "open",
                 "review_at": "2026-05-01T00:00:00Z", "title": "", "decided_by": "", "reversibility": "type_1"},
                {"id": "dec-b", "project_id": "p", "status": "open",
                 "review_at": "not-an-iso-date", "title": "", "decided_by": "", "reversibility": "type_1"},
            ],
            "project_decision_index": {"p": ["dec-none", "dec-a", "dec-b"]},
        }
        asc = query_sorted_by_review_at(doc, reverse=False)
        desc = query_sorted_by_review_at(doc, reverse=True)
        # 'dec-a' has a valid review_at; the two invalid entries go to the end in both directions.
        self.assertEqual(asc[0]["id"], "dec-a")
        self.assertEqual(desc[0]["id"], "dec-a")
        # The invalid entries are at the end (their order between themselves is unspecified)
        self.assertEqual(sorted([asc[1]["id"], asc[2]["id"]]), ["dec-b", "dec-none"])


if __name__ == "__main__":
    unittest.main()
