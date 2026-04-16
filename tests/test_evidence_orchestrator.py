# tests/test_evidence_orchestrator.py
"""Tests for sub-brief generation and fan-in merge."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_orchestrator import (  # noqa: E402
    EVIDENCE_AGENTS,
    generate_sub_brief,
    score_agent_relevance,
    merge_returns,
)


class TestAgentScoring(unittest.TestCase):
    def test_saudi_brief_scores_nyx_high(self):
        brief = "Launch a neobank for Saudi expats."
        score = score_agent_relevance("agent-nyxx", brief)
        self.assertGreaterEqual(score, 2)

    def test_non_saudi_brief_scores_nyx_low(self):
        brief = "Productivity app for European freelancers."
        score = score_agent_relevance("agent-nyxx", brief)
        self.assertLess(score, 2)

    def test_competitive_brief_scores_vex_high(self):
        brief = "Evaluate competitors for our pet platform."
        score = score_agent_relevance("agent-vexx", brief)
        self.assertGreaterEqual(score, 2)

    def test_neobank_brief_activates_vex(self):
        """Task 14's synthetic brief must activate Vex (score >= 2)."""
        brief = "Launch a mobile-first neobank targeting Saudi expats remitting to South Asia."
        score = score_agent_relevance("agent-vexx", brief)
        self.assertGreaterEqual(score, 2, f"Vex scored {score} — won't activate for fintech brief")

    def test_neobank_brief_activates_talon(self):
        """Growth architect should also activate on a launch brief."""
        brief = "Launch a mobile-first neobank targeting Saudi expats remitting to South Asia. Go-to-market strategy needed."
        score = score_agent_relevance("agent-taln", brief)
        self.assertGreaterEqual(score, 2, f"Talon scored {score} — won't activate for launch brief")


class TestSubBrief(unittest.TestCase):
    def test_sub_brief_contains_required_sections(self):
        out = generate_sub_brief("agent-vexx", "Pet healthcare platform brief.")
        self.assertIn("AGENT: Vex", out)
        self.assertIn("YOUR SUB-BRIEF", out)
        self.assertIn("Evidence budget", out)
        self.assertIn("Quality floor", out)
        self.assertIn("RETURN", out)

    def test_sub_brief_includes_full_original_brief(self):
        brief = "Pet healthcare platform brief with specific context."
        out = generate_sub_brief("agent-vexx", brief)
        self.assertIn(brief, out)


class TestMergeReturns(unittest.TestCase):
    def test_merge_dedupes_by_source_url(self):
        returns = [
            {
                "agent_id": "agent-vexx",
                "evidence": [{"id": "ev-1", "source_url": "https://a.com", "retrieved_by": ["agent-vexx"]}],
                "recommendation": "go",
                "confidence": 0.7,
                "queried_count": 5,
                "quality_avg": 3.5,
            },
            {
                "agent_id": "agent-nyxx",
                "evidence": [{"id": "ev-2", "source_url": "https://a.com", "retrieved_by": ["agent-nyxx"]}],
                "recommendation": "go",
                "confidence": 0.8,
                "queried_count": 3,
                "quality_avg": 4.0,
            },
        ]
        merged = merge_returns(returns)
        # Same URL → merged into one Evidence, retrieved_by array grows
        self.assertEqual(len(merged["evidence"]), 1)
        self.assertEqual(
            set(merged["evidence"][0]["retrieved_by"]),
            {"agent-vexx", "agent-nyxx"},
        )

    def test_merge_reports_totals(self):
        returns = [
            {"agent_id": "agent-vexx", "evidence": [], "recommendation": "", "confidence": 0.7, "queried_count": 5, "quality_avg": 3.5},
            {"agent_id": "agent-nyxx", "evidence": [], "recommendation": "", "confidence": 0.8, "queried_count": 3, "quality_avg": 4.0},
        ]
        merged = merge_returns(returns)
        self.assertEqual(merged["total_queries"], 8)
        self.assertEqual(merged["agents"], ["agent-vexx", "agent-nyxx"])


class TestEvidenceAgentsTable(unittest.TestCase):
    def test_four_evidence_agents_defined(self):
        self.assertEqual(
            set(EVIDENCE_AGENTS.keys()),
            {"agent-vexx", "agent-nyxx", "agent-echo", "agent-taln"},
        )


import json
import tempfile


class TestAppendEvidence(unittest.TestCase):
    def test_appends_to_empty_file(self):
        from evidence_orchestrator import append_evidence

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-evidence.json")
            with open(path, "w") as f:
                json.dump({"evidence": [], "project_evidence_index": {}}, f)

            bundle = {"evidence": [{"id": "ev-1", "source_url": "https://a.com"}]}
            append_evidence("proj-003", bundle, path)

            with open(path) as f:
                doc = json.load(f)
            self.assertEqual(len(doc["evidence"]), 1)
            self.assertEqual(doc["project_evidence_index"]["proj-003"], ["ev-1"])

    def test_existing_project_ids_extend_not_replace(self):
        from evidence_orchestrator import append_evidence

        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-evidence.json")
            with open(path, "w") as f:
                json.dump({
                    "evidence": [{"id": "ev-old"}],
                    "project_evidence_index": {"proj-003": ["ev-old"]},
                }, f)

            bundle = {"evidence": [{"id": "ev-new"}]}
            append_evidence("proj-003", bundle, path)

            with open(path) as f:
                doc = json.load(f)
            self.assertEqual(
                set(doc["project_evidence_index"]["proj-003"]),
                {"ev-old", "ev-new"},
            )

    def test_append_evidence_is_atomic(self):
        """Persistence must survive mid-write failure — tempfile + rename pattern."""
        import glob
        from evidence_orchestrator import append_evidence
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-evidence.json")
            with open(path, "w") as f:
                json.dump({"evidence": [], "project_evidence_index": {}}, f)
            bundle = {"evidence": [{"id": "ev-atom1234", "source_url": "https://a.com"}]}
            append_evidence("proj-atomic", bundle, path)
            # After the write, there should be no leftover .tmp files in the directory
            tmps = glob.glob(os.path.join(tmp, "*.tmp"))
            self.assertEqual(tmps, [], f"stray tmp files after atomic write: {tmps}")
            # And the file should be readable (non-empty, well-formed)
            with open(path) as f:
                doc = json.load(f)
            self.assertEqual(len(doc["evidence"]), 1)


class TestStripUnsupported(unittest.TestCase):
    def test_fact_with_valid_evidence_id_is_kept(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "Market grew 14% YoY [FACT: ev-abc12345]."
        out = strip_unsupported_claims(text, {"ev-abc12345"})
        self.assertIn("[FACT: ev-abc12345]", out)

    def test_fact_without_evidence_id_is_stripped(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "Market grew 14% YoY [FACT]."
        out = strip_unsupported_claims(text, set())
        self.assertIn("[UNSUPPORTED", out)
        self.assertNotIn("[FACT]", out)

    def test_fact_with_unknown_evidence_id_is_stripped(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "Market grew 14% YoY [FACT: ev-ghost123]."
        out = strip_unsupported_claims(text, {"ev-real1234"})
        self.assertIn("[UNSUPPORTED", out)

    def test_opinion_tags_are_left_alone(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "The market feels underserved [OPINION]."
        out = strip_unsupported_claims(text, set())
        self.assertEqual(out, text)


if __name__ == "__main__":
    unittest.main()
