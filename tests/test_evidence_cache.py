# tests/test_evidence_cache.py
"""Tests for the content-addressed evidence cache."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_cache import (  # noqa: E402
    make_key,
    normalize_query,
    read_cache,
    write_cache,
    cache_stats,
    evict_lru,
)


class TestKeyAndNormalize(unittest.TestCase):
    def test_normalize_lowercases_and_collapses_whitespace(self):
        self.assertEqual(
            normalize_query("  Saudi   Pet\nClinics  "),
            "saudi pet clinics",
        )

    def test_normalize_strips_punctuation(self):
        self.assertEqual(
            normalize_query("Saudi pet-clinics?"),
            "saudi pet clinics",
        )

    def test_same_query_different_whitespace_yields_same_key(self):
        k1 = make_key("Saudi pet clinics", "https://a.com")
        k2 = make_key("  Saudi   pet   clinics  ", "https://a.com")
        self.assertEqual(k1, k2)

    def test_different_url_yields_different_key(self):
        k1 = make_key("q", "https://a.com")
        k2 = make_key("q", "https://b.com")
        self.assertNotEqual(k1, k2)


class TestReadWrite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_write_then_read_returns_entry(self):
        key = "test-key-123"
        entry = {"key": key, "query": "q", "results": [], "fetched_at": "2026-04-16T00:00:00Z", "hits": 0}
        write_cache(self.tmp, key, entry)
        got = read_cache(self.tmp, key)
        self.assertEqual(got["query"], "q")

    def test_read_missing_returns_none(self):
        self.assertIsNone(read_cache(self.tmp, "does-not-exist"))

    def test_read_increments_hits(self):
        key = "test-key-abc"
        entry = {"key": key, "query": "q", "results": [], "fetched_at": "2026-04-16T00:00:00Z", "hits": 0}
        write_cache(self.tmp, key, entry)
        read_cache(self.tmp, key)
        read_cache(self.tmp, key)
        got = read_cache(self.tmp, key)
        self.assertEqual(got["hits"], 3)  # 3rd read reports hits incremented 3 times


class TestStatsAndEvict(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        for i, key in enumerate(["alpha", "beta", "gamma"]):
            entry = {"key": key, "query": f"q{i}", "results": [], "fetched_at": "2026-04-16T00:00:00Z", "hits": 0}
            write_cache(self.tmp, key, entry)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_cache_stats_reports_counts(self):
        stats = cache_stats(self.tmp)
        self.assertEqual(stats["entries"], 3)
        self.assertGreater(stats["size_bytes"], 0)

    def test_evict_lru_removes_oldest(self):
        now = datetime.now(timezone.utc).timestamp()
        os.utime(os.path.join(self.tmp, "alpha.json"), (now - 100, now - 100))
        os.utime(os.path.join(self.tmp, "beta.json"), (now - 50, now - 50))
        os.utime(os.path.join(self.tmp, "gamma.json"), (now, now))

        evicted = evict_lru(self.tmp, keep=2)

        self.assertEqual(len(evicted), 1)
        self.assertEqual(evicted[0], "alpha")
        self.assertIsNone(read_cache(self.tmp, "alpha"))
        self.assertIsNotNone(read_cache(self.tmp, "gamma"))


if __name__ == "__main__":
    unittest.main()
