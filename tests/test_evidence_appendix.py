# tests/test_evidence_appendix.py
"""Tests for Sources Appendix rendering."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_appendix import render_compact, render_markdown, render_summary_block


def _ev(id_, title, stype="analyst", score=3):
    return {
        "id": id_, "claim": "claim", "source_url": f"https://{id_}.com",
        "source_title": title, "source_type": stype, "quality_score": score,
        "retrieved_at": "2026-04-16T14:32:00Z", "retrieved_by": ["agent-vexx"],
        "queried_via": "WebSearch", "excerpt": "excerpt text here",
        "confidence": 0.9, "signal_tag": "FACT",
    }


class TestCompact(unittest.TestCase):
    def test_empty_renders_nothing(self):
        self.assertEqual(render_compact([]).strip(), "")

    def test_groups_by_tier(self):
        items = [_ev("a", "Gov Report", "primary_government", 5), _ev("b", "Blog Post", "blog", 1)]
        out = render_compact(items)
        self.assertIn("⭐⭐⭐⭐⭐", out)
        self.assertIn("⭐", out)
        self.assertIn("Gov Report", out)
        self.assertIn("Blog Post", out)

    def test_shows_one_line_per_source(self):
        items = [_ev("ev-aaa", "Source A"), _ev("ev-bbb", "Source B"), _ev("ev-ccc", "Source C")]
        out = render_compact(items)
        lines = [l for l in out.splitlines() if "[ev-" in l]
        self.assertEqual(len(lines), 3)


class TestMarkdown(unittest.TestCase):
    def test_includes_excerpt_and_retrieval_metadata(self):
        items = [_ev("a", "Source A")]
        out = render_markdown(items)
        self.assertIn("excerpt text here", out)
        self.assertIn("agent-vexx", out)
        self.assertIn("2026-04-16", out)

    def test_includes_cited_url(self):
        items = [_ev("a", "Source A")]
        out = render_markdown(items)
        self.assertIn("https://a.com", out)


class TestSummaryBlock(unittest.TestCase):
    def test_reports_totals_and_averages(self):
        items = [_ev("a", "A", score=5), _ev("b", "B", score=3)]
        out = render_summary_block(items, total_queries=23, elapsed_sec=167, cache_hits=6, conflicts=1)
        self.assertIn("23", out)          # queries
        self.assertIn("4.0", out)          # avg quality
        self.assertIn("2m", out)           # elapsed formatted
        self.assertIn("6/23", out)         # cache hits
        self.assertIn("1", out)            # conflicts


if __name__ == "__main__":
    unittest.main()
