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


if __name__ == "__main__":
    unittest.main()
