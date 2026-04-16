"""Tests for URL → (quality_score, source_type) grading."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_quality import (  # noqa: E402
    grade_url,
    load_overrides,
    merge_rules,
    DEFAULT_RULES,
)

FIXTURE = os.path.join(os.path.dirname(__file__), 'fixtures', 'quality-overrides.json')


class TestGradeDefaultRules(unittest.TestCase):
    def test_saudi_government_domain_tier_5(self):
        score, stype = grade_url("https://mewa.gov.sa/annual-report-2024")
        self.assertEqual(score, 5)
        self.assertEqual(stype, "primary_government")

    def test_sec_gov_tier_5(self):
        score, stype = grade_url("https://www.sec.gov/Archives/edgar/data/...")
        self.assertEqual(score, 5)

    def test_annual_report_path_tier_4(self):
        score, stype = grade_url("https://company.com/annual-report/2024.pdf")
        self.assertEqual(score, 4)
        self.assertEqual(stype, "primary_company")

    def test_pricing_page_tier_4(self):
        score, stype = grade_url("https://stripe.com/pricing")
        self.assertEqual(score, 4)

    def test_mckinsey_tier_3(self):
        score, stype = grade_url("https://www.mckinsey.com/insights/...")
        self.assertEqual(score, 3)
        self.assertEqual(stype, "analyst")

    def test_wamda_tier_3(self):
        score, stype = grade_url("https://www.wamda.com/2024/...")
        self.assertEqual(score, 3)
        self.assertEqual(stype, "reputable_media")

    def test_app_store_tier_2(self):
        score, stype = grade_url("https://apps.apple.com/sa/app/pawable/id123")
        self.assertEqual(score, 2)
        self.assertEqual(stype, "user_reviews")

    def test_reddit_tier_2(self):
        score, stype = grade_url("https://reddit.com/r/saudiarabia/comments/...")
        self.assertEqual(score, 2)
        self.assertEqual(stype, "community")

    def test_medium_tier_1(self):
        score, stype = grade_url("https://medium.com/@someone/article")
        self.assertEqual(score, 1)
        self.assertEqual(stype, "blog")

    def test_unknown_domain_defaults_to_tier_2_unknown(self):
        score, stype = grade_url("https://random-site-nobody-has-heard-of.io/x")
        self.assertEqual(score, 2)
        self.assertEqual(stype, "unknown")


class TestRegexAnchoring(unittest.TestCase):
    def test_ir_subdomain_does_not_match_arbitrary_substring(self):
        # 'fair.apple.com' contains 'ir' as part of 'fair' — must not match tier-4
        score, stype = grade_url("https://fair.apple.com/path")
        self.assertNotEqual(score, 4, f"unexpectedly graded as {stype} tier-{score}")

    def test_hair_subdomain_does_not_match(self):
        score, stype = grade_url("https://hair.example.com")
        self.assertNotEqual(score, 4)

    def test_real_ir_subdomain_still_matches(self):
        # 'ir.apple.com' is a real IR page — must keep matching tier-4
        score, stype = grade_url("https://ir.apple.com/annual")
        self.assertEqual(score, 4)
        self.assertEqual(stype, "primary_company")

    def test_not_reddit_dot_com_does_not_match_reddit(self):
        score, stype = grade_url("https://not-reddit.com/foo")
        self.assertNotEqual(stype, "community", "anchor missing on reddit pattern — matched not-reddit.com")


class TestOverrides(unittest.TestCase):
    def test_load_overrides_reads_file(self):
        rules = load_overrides(FIXTURE)
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0]["score"], 4)

    def test_load_overrides_missing_file_returns_empty(self):
        rules = load_overrides("/tmp/does-not-exist-12345.json")
        self.assertEqual(rules, [])

    def test_merge_rules_overrides_win_on_match(self):
        merged = merge_rules(DEFAULT_RULES, load_overrides(FIXTURE))
        score, stype = grade_url("https://westlaw.com/some-case", rules=merged)
        self.assertEqual(score, 4)
        self.assertEqual(stype, "primary_company")

    def test_load_overrides_malformed_json_returns_empty(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ not valid json ]")
            path = f.name
        try:
            self.assertEqual(load_overrides(path), [])
        finally:
            os.unlink(path)

    def test_load_overrides_missing_rules_key_returns_empty(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"not_rules": []}')
            path = f.name
        try:
            self.assertEqual(load_overrides(path), [])
        finally:
            os.unlink(path)

    def test_load_overrides_non_list_rules_returns_empty(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"rules": "not a list"}')
            path = f.name
        try:
            self.assertEqual(load_overrides(path), [])
        finally:
            os.unlink(path)

    def test_load_overrides_skips_rules_missing_required_keys(self):
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"rules": [{"pattern": "x", "score": 3}, {"pattern": "y", "score": 3, "type": "blog"}]}')
            path = f.name
        try:
            rules = load_overrides(path)
            self.assertEqual(len(rules), 1)
            self.assertEqual(rules[0]["pattern"], "y")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
