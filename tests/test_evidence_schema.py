"""Tests for the Evidence object schema primitives."""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_schema import (  # noqa: E402
    SOURCE_TYPES,
    SIGNAL_TAGS,
    Evidence,
    new_evidence_id,
)


class TestEvidenceId(unittest.TestCase):
    def test_new_id_has_expected_prefix(self):
        eid = new_evidence_id()
        self.assertTrue(eid.startswith("ev-"), f"got: {eid}")

    def test_new_id_is_unique_across_calls(self):
        ids = {new_evidence_id() for _ in range(50)}
        self.assertEqual(len(ids), 50)

    def test_new_id_matches_format(self):
        # ev- followed by 6 lowercase hex characters
        eid = new_evidence_id()
        self.assertRegex(eid, r"^ev-[0-9a-f]{6}$")


class TestEvidenceDataclass(unittest.TestCase):
    def test_evidence_round_trips_through_dict(self):
        e = Evidence(
            id="ev-abc123",
            claim="Saudi pet market grew 14% YoY in 2024",
            source_url="https://mewa.gov.sa/annual-2024",
            source_title="MEWA Annual Report 2024",
            source_type="primary_government",
            quality_score=5,
            retrieved_at="2026-04-16T14:32:00Z",
            retrieved_by=["agent-vexx"],
            queried_via="WebSearch",
            excerpt="Companion animal sector grew 14% YoY in 2024.",
            confidence=0.92,
            signal_tag="FACT",
        )
        d = e.to_dict()
        restored = Evidence.from_dict(d)
        self.assertEqual(e, restored)

    def test_source_types_enum_contains_all_tiers(self):
        for t in [
            "primary_government",
            "primary_company",
            "analyst",
            "reputable_media",
            "user_reviews",
            "community",
            "blog",
            "unknown",
        ]:
            self.assertIn(t, SOURCE_TYPES, f"missing type: {t}")

    def test_signal_tags_enum_contains_all_four(self):
        self.assertEqual(
            SIGNAL_TAGS,
            frozenset({"FACT", "INFERENCE", "HYPOTHESIS", "OPINION"}),
        )


if __name__ == "__main__":
    unittest.main()
