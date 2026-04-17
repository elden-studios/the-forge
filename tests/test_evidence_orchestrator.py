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

    def test_distinct_excerpts_from_same_url_are_preserved(self):
        """Two Evidence items sharing a source_url but with different excerpts
        must both survive merge — each represents a different claim from
        the same page. Collapsing them loses the second claim's citation.

        Regression from Task 14: Nyx cited ev-b7e90014 and ev-f8a1c9e6 for
        two different excerpts from the same SAMA rulebook URL. Dedup kept
        ev-b7e90014 and dropped ev-f8a1c9e6, orphaning every later citation
        of ev-f8a1c9e6.
        """
        from evidence_orchestrator import merge_returns
        returns = [
            {
                "agent_id": "agent-nyxx",
                "evidence": [
                    {
                        "id": "ev-nyxfirst",
                        "source_url": "https://sama.gov.sa/rulebook/xyz",
                        "excerpt": "Licensing requires Category A registration.",
                        "retrieved_by": ["agent-nyxx"],
                    },
                    {
                        "id": "ev-nyxsecnd",
                        "source_url": "https://sama.gov.sa/rulebook/xyz",
                        "excerpt": "Transfer caps of SAR 50,000 per month apply.",
                        "retrieved_by": ["agent-nyxx"],
                    },
                ],
                "recommendation": "r",
                "confidence": 0.8,
                "queried_count": 2,
                "quality_avg": 5.0,
            },
        ]
        merged = merge_returns(returns)
        ids = {e["id"] for e in merged["evidence"]}
        self.assertIn("ev-nyxfirst", ids, "first distinct-excerpt Evidence must survive")
        self.assertIn("ev-nyxsecnd", ids, "second distinct-excerpt Evidence must survive")
        self.assertEqual(len(merged["evidence"]), 2)

    def test_identical_excerpt_and_url_across_agents_collapses_and_grows_retrieved_by(self):
        """When two agents cite literally the same (url, excerpt), that's a
        genuine duplicate — collapse to one Evidence, grow retrieved_by."""
        from evidence_orchestrator import merge_returns
        returns = [
            {
                "agent_id": "agent-vexx",
                "evidence": [{
                    "id": "ev-vex12345",
                    "source_url": "https://analyst.com/report",
                    "excerpt": "Market is growing 14% YoY.",
                    "retrieved_by": ["agent-vexx"],
                }],
                "recommendation": "r", "confidence": 0.8, "queried_count": 1, "quality_avg": 3,
            },
            {
                "agent_id": "agent-nyxx",
                "evidence": [{
                    "id": "ev-nyx67890",
                    "source_url": "https://analyst.com/report",
                    "excerpt": "Market is growing 14% YoY.",
                    "retrieved_by": ["agent-nyxx"],
                }],
                "recommendation": "r", "confidence": 0.8, "queried_count": 1, "quality_avg": 3,
            },
        ]
        merged = merge_returns(returns)
        self.assertEqual(len(merged["evidence"]), 1, "genuine duplicates collapse")
        survivor = merged["evidence"][0]
        self.assertEqual(set(survivor["retrieved_by"]), {"agent-vexx", "agent-nyxx"})


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

    def test_append_evidence_mirrors_to_assets_when_next_to_root(self):
        """When forge-evidence.json lives next to an assets/ dir, writes mirror to assets/forge-evidence.json.

        Rationale: the live dashboard is served from assets/ and fetches assets/forge-evidence.json.
        Keeping the two in sync prevents split-brain where the backend writes
        evidence but the UI shows 0 sources.
        """
        from evidence_orchestrator import append_evidence
        with tempfile.TemporaryDirectory() as tmp:
            root_path = os.path.join(tmp, "forge-evidence.json")
            with open(root_path, "w") as f:
                json.dump({"evidence": [], "project_evidence_index": {}}, f)
            # Create a sibling assets/ directory with an existing forge-evidence.json
            assets_dir = os.path.join(tmp, "assets")
            os.makedirs(assets_dir)
            assets_path = os.path.join(assets_dir, "forge-evidence.json")
            with open(assets_path, "w") as f:
                json.dump({"evidence": [], "project_evidence_index": {}}, f)

            bundle = {"evidence": [{"id": "ev-mirror01", "source_url": "https://a.com"}]}
            append_evidence("proj-mirror", bundle, root_path)

            # Both files should reflect the new evidence
            with open(root_path) as f:
                root_doc = json.load(f)
            with open(assets_path) as f:
                assets_doc = json.load(f)
            self.assertEqual(len(root_doc["evidence"]), 1)
            self.assertEqual(len(assets_doc["evidence"]), 1)
            self.assertEqual(
                root_doc["project_evidence_index"],
                assets_doc["project_evidence_index"],
            )

    def test_append_evidence_no_mirror_when_assets_missing(self):
        """If no assets/ sibling exists, no mirror is attempted — must not crash."""
        from evidence_orchestrator import append_evidence
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "forge-evidence.json")
            with open(path, "w") as f:
                json.dump({"evidence": [], "project_evidence_index": {}}, f)
            bundle = {"evidence": [{"id": "ev-solo01", "source_url": "https://a.com"}]}
            # Should not raise even though no assets/ dir exists
            append_evidence("proj-solo", bundle, path)
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

    def test_naked_ev_id_bracket_with_unknown_id_gets_flagged(self):
        """Agent prose uses naked '[ev-X, ev-Y]' — not '[FACT: ev-X]'.

        The enforcement function must catch naked forms too. Unknown
        IDs in a naked bracket get replaced with an inline '⚠ <ID> unsupported'
        marker — the VALID IDs in the same bracket survive.
        """
        from evidence_orchestrator import strip_unsupported_claims
        text = "Market size claim [ev-12345678, ev-ghostzzz] drives the thesis."
        out = strip_unsupported_claims(text, {"ev-12345678"})
        self.assertIn("ev-12345678", out, "valid ID must survive")
        self.assertNotIn("ev-ghostzzz]", out, "invalid ID must be replaced")
        # The survivor is still cited in some form; the unsupported marker appears
        self.assertIn("unsupported", out.lower())

    def test_naked_single_ev_id_bracket_with_unknown_id(self):
        from evidence_orchestrator import strip_unsupported_claims
        text = "Some claim [ev-ghost1234] anchoring the argument."
        out = strip_unsupported_claims(text, {"ev-real12345"})
        # The bracket becomes an UNSUPPORTED marker
        self.assertNotIn("ev-ghost1234]", out)
        self.assertIn("unsupported", out.lower())

    def test_naked_single_ev_id_bracket_with_valid_id_survives(self):
        from evidence_orchestrator import strip_unsupported_claims
        text = "A claim [ev-real5678] backed by evidence."
        out = strip_unsupported_claims(text, {"ev-real5678"})
        self.assertEqual(out, text, "fully-valid bracket must pass through unchanged")

    def test_multi_id_bracket_with_mix_of_valid_and_invalid(self):
        from evidence_orchestrator import strip_unsupported_claims
        text = "Supports the position [ev-valid123, ev-ghost456, ev-valid789]."
        out = strip_unsupported_claims(text, {"ev-valid123", "ev-valid789"})
        # Valid IDs preserved
        self.assertIn("ev-valid123", out)
        self.assertIn("ev-valid789", out)
        # Invalid flagged, not silently surviving
        self.assertNotIn("ev-ghost456,", out)
        self.assertNotIn("ev-ghost456]", out)

    def test_opinion_tag_still_left_alone(self):
        """OPINION with no ev-* ID must still be left untouched."""
        from evidence_orchestrator import strip_unsupported_claims
        text = "In my view [OPINION] the market is ready."
        out = strip_unsupported_claims(text, set())
        self.assertEqual(out, text)

    def test_nyx_deliverable_excerpt_flags_orphan_id(self):
        """Regression from Task 14 deliverable — the exact Nyx prose citing
        ev-f8a1c9e6 which got dedup'd out must produce an UNSUPPORTED marker
        after merge-and-strip."""
        from evidence_orchestrator import strip_unsupported_claims
        text = "Regulatory framing [ev-a3f1c2d7, ev-b7e90014, ev-f8a1c9e6]"
        valid_ids = {"ev-a3f1c2d7", "ev-b7e90014"}  # ev-f8a1c9e6 orphaned
        out = strip_unsupported_claims(text, valid_ids)
        self.assertIn("ev-a3f1c2d7", out)
        self.assertIn("ev-b7e90014", out)
        self.assertNotIn("ev-f8a1c9e6,", out)
        self.assertNotIn("ev-f8a1c9e6]", out)
        self.assertIn("unsupported", out.lower())


class TestProjectQualityOverrides(unittest.TestCase):
    """Confirm that evidence-quality-overrides.json at project root is loaded."""

    def test_project_quality_rules_is_a_list(self):
        from evidence_orchestrator import PROJECT_QUALITY_RULES
        self.assertIsInstance(PROJECT_QUALITY_RULES, list)
        self.assertGreater(len(PROJECT_QUALITY_RULES), 0)


if __name__ == "__main__":
    unittest.main()
