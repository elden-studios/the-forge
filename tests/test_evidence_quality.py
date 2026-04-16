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


if __name__ == "__main__":
    unittest.main()
