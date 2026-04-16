"""Cross-module consistency invariants.

These tests pin contracts that span multiple modules. If a new source_type
is added to the schema, these tests force the engineer to also update the
freshness band table and the quality grading rules — preventing silent drift.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_schema import SOURCE_TYPES  # noqa: E402
from evidence_freshness import FRESHNESS_RULES  # noqa: E402
from evidence_quality import DEFAULT_RULES  # noqa: E402


class TestSourceTypeConsistency(unittest.TestCase):
    def test_every_freshness_rule_key_is_a_known_source_type(self):
        """FRESHNESS_RULES keys must be a subset of SOURCE_TYPES."""
        for stype in FRESHNESS_RULES.keys():
            self.assertIn(
                stype, SOURCE_TYPES,
                f"FRESHNESS_RULES has key '{stype}' but SOURCE_TYPES doesn't",
            )

    def test_every_non_unknown_source_type_has_freshness_band(self):
        """Every source_type other than 'unknown' must have a freshness band.

        'unknown' is the default-fallback case and explicitly doesn't need
        a band (it falls back to blog bands via FRESHNESS_RULES.get default).
        """
        missing = [
            s for s in SOURCE_TYPES
            if s != "unknown" and s not in FRESHNESS_RULES
        ]
        self.assertEqual(
            missing, [],
            f"SOURCE_TYPES values without FRESHNESS_RULES bands: {missing}",
        )

    def test_every_quality_rule_source_type_is_a_known_source_type(self):
        """DEFAULT_RULES (pattern, score, type) tuples must use known types."""
        for pattern, score, stype in DEFAULT_RULES:
            self.assertIn(
                stype, SOURCE_TYPES,
                f"quality rule '{pattern}' emits unknown source_type '{stype}'",
            )

    def test_quality_scores_are_all_in_valid_range(self):
        for pattern, score, stype in DEFAULT_RULES:
            self.assertIsInstance(score, int)
            self.assertGreaterEqual(score, 1)
            self.assertLessEqual(score, 5)


if __name__ == "__main__":
    unittest.main()
