# Evidence Pipes v1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn every `[FACT]` an agent emits into a linkable, timestamped, graded, reproducible, cached, conflict-aware Evidence object — with 4 research agents running in parallel via `superpowers:dispatching-parallel-agents`.

**Architecture:** Pure-function modules (quality / freshness / cache / conflict) feed an orchestration layer that dispatches evidence-agent subagents in parallel, fans their Evidence in, persists to `forge-evidence.json`, and renders a Sources Appendix. The reasoning agents (Ren, Sable, Atlas, Kira, Flint synthesis) stay sequential — parallelism is at the I/O boundary.

**Tech Stack:** Python 3.9+ stdlib only (no new deps), unittest, JSON, regex URL grading. WebSearch tool (phase 1 pipes). Chrome MCP (phase 2, scaffolded but deferred). HTML/Canvas for the dashboard Sources tab. Markdown for the Sources Appendix export.

**Spec:** `docs/superpowers/specs/2026-04-16-evidence-pipes-v1-design.md`

---

## File Map

**New files:**
- `tools/evidence_schema.py` — Evidence object dataclass, constants, ID generator
- `tools/evidence_quality.py` — URL → (score, source_type) regex rules + JSON override merge + Flint override logging
- `tools/evidence_freshness.py` — per-source-type stale/refetch band logic
- `tools/evidence_cache.py` — content-addressed cache, TTL, LRU eviction
- `tools/evidence_conflict.py` — topic clustering, numeric divergence detection, scope>tier>recency resolution
- `tools/evidence_orchestrator.py` — sub-brief generation, fan-in merge, conflict reporting
- `tools/evidence_appendix.py` — Markdown + compact-terminal rendering of the Sources Appendix
- `tests/test_evidence_schema.py`
- `tests/test_evidence_quality.py`
- `tests/test_evidence_freshness.py`
- `tests/test_evidence_cache.py`
- `tests/test_evidence_conflict.py`
- `tests/test_evidence_orchestrator.py`
- `tests/test_evidence_appendix.py`
- `tests/fixtures/websearch-responses/saudi-pet-market.json` — canned WebSearch return
- `tests/fixtures/websearch-responses/empty-results.json`
- `tests/fixtures/quality-overrides.json` — test fixture for user override file
- `references/evidence-pipes-spec.md` — canonical in-repo spec reference
- `forge-evidence.json` — project root, initialized empty
- `evidence-quality-overrides.json` — project root, initialized empty
- `assets/.forge-cache/.gitkeep` — preserves empty cache dir in git

**Modified files:**
- `tools/validator.py` — add `validate_evidence()` + extend `validate_project()` + `--cache-stats` flag
- `tests/test_validator.py` — add `TestValidateEvidence` class (+20 tests) + extend smoke test
- `forge-state.json` — add `evidence_pipes: { enabled: true }` block
- `forge-tasks.json` — add `evidence_dispatch` subfield on tasks (tracks subagent status)
- `SKILL.md` — rewrite Phase 2 section, add "Evidence Pipes" section, update Output Format + Quality Standards
- `references/collaboration-protocol.md` — bump to v3.1, rewrite Phase 2, add Standing Rules 7-9
- `assets/dashboard.html` — add Evidence block to Mission Control tab (tab 1), add new Sources tab (tab 5)
- `assets/office-template.html` — add pulsing `[!]` bubble animation variant for evidence agents during dispatch
- `.gitignore` — add `assets/.forge-cache/` (but keep `.gitkeep`)

**File responsibilities:**
- Each `evidence_*.py` module is a **pure function** library (no I/O except cache module's filesystem reads/writes). Testable standalone.
- `evidence_orchestrator.py` is the only module with side effects on `forge-evidence.json`.
- `validator.py` stays stdlib-only. No new dependencies anywhere in the plan.

---

## Execution Notes

- **TDD is mandatory.** Every production file is preceded by a failing test. Red → Green → Refactor per `superpowers:test-driven-development`.
- **Commit cadence:** one commit per task. Task = one module or one coherent batch of changes. Each commit runs `python3 -m unittest discover tests -v` green before landing.
- **Code review gate:** after Task 6 (foundation complete) and after Task 14 (end-to-end working) invoke `superpowers:requesting-code-review`. Address Critical/Important before proceeding.
- **Real-file smoke test:** must stay green across every task. If a task would break it (e.g., validator rule tightens before data catches up), update both in the same commit.
- **Phase 2 deferrals:** Chrome MCP pipes are scaffolded in the orchestrator but stubbed. The dispatch shape accepts a `queried_via` value of `"ChromeMCP"`; the subagent prompt says "use WebSearch only in v1." Flipping to Chrome MCP later is a prompt change plus a fixture set.

---

## Task 1: Evidence schema module — ID + dataclass + constants

**Files:**
- Create: `tools/evidence_schema.py`
- Test: `tests/test_evidence_schema.py`

Foundation: the Evidence dataclass and allowed-value enums. All other modules import from here.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_evidence_schema.py
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd "/Users/lbazerbashi/Elden Studios/the-forge" && python3 -m unittest tests.test_evidence_schema -v`
Expected: `ImportError: No module named 'evidence_schema'`

- [ ] **Step 3: Write minimal implementation**

```python
# tools/evidence_schema.py
"""Evidence object schema — dataclass, allowed-value enums, ID generator.

This module is the foundation for all evidence handling. Pure data, no I/O.
"""
from dataclasses import asdict, dataclass, field
from typing import List
import uuid


SOURCE_TYPES = frozenset({
    "primary_government",
    "primary_company",
    "analyst",
    "reputable_media",
    "user_reviews",
    "community",
    "blog",
    "unknown",  # default when no rule matches
})

SIGNAL_TAGS = frozenset({"FACT", "INFERENCE", "HYPOTHESIS", "OPINION"})


def new_evidence_id():
    """Generate a fresh evidence ID like 'ev-7f2a3c'."""
    return f"ev-{uuid.uuid4().hex[:6]}"


@dataclass
class Evidence:
    id: str
    claim: str
    source_url: str
    source_title: str
    source_type: str
    quality_score: int
    retrieved_at: str  # ISO 8601 UTC
    retrieved_by: List[str]
    queried_via: str
    excerpt: str
    confidence: float
    signal_tag: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_evidence_schema -v`
Expected: all 5 tests pass

- [ ] **Step 5: Verify no regression on existing tests**

Run: `python3 -m unittest discover tests -v`
Expected: all existing + new tests pass (26 + 5 = 31)

- [ ] **Step 6: Commit**

```bash
cd "/Users/lbazerbashi/Elden Studios/the-forge"
git add tools/evidence_schema.py tests/test_evidence_schema.py
git commit -m "$(cat <<'EOF'
Evidence schema — dataclass, enums, ID generator

Foundation module. Pure data, no I/O. Defines Evidence dataclass,
SOURCE_TYPES (8 tiers including 'unknown' default), SIGNAL_TAGS
(FACT/INFERENCE/HYPOTHESIS/OPINION), and new_evidence_id() yielding
'ev-<6 hex>'.

All subsequent evidence modules import from here.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 2: Evidence quality grading — regex rules + override merge

**Files:**
- Create: `tools/evidence_quality.py`
- Create: `tests/test_evidence_quality.py`
- Create: `tests/fixtures/quality-overrides.json`

Pure function: URL → (score, source_type). Ships with default rule table; merges optional `evidence-quality-overrides.json` on top at load time.

- [ ] **Step 1: Create the fixture file**

```json
// tests/fixtures/quality-overrides.json
{
  "rules": [
    {"pattern": "westlaw\\.com", "score": 4, "type": "primary_company"},
    {"pattern": "my-internal-wiki\\.corp", "score": 3, "type": "analyst"}
  ]
}
```

- [ ] **Step 2: Write the failing tests**

```python
# tests/test_evidence_quality.py
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_evidence_quality -v`
Expected: `ImportError: No module named 'evidence_quality'`

- [ ] **Step 4: Write minimal implementation**

```python
# tools/evidence_quality.py
"""URL → (quality_score, source_type) grading.

Rule-based first: regex patterns on URL match a tier 1-5 score and source_type.
Unknown URLs default to (2, 'unknown') — conservative: not trusted, not worst.
Supports user-provided overrides via a JSON file.
"""
import json
import os
import re


# (pattern, score, source_type) — order matters: first match wins
DEFAULT_RULES = [
    # Tier 5 — primary government / regulatory
    (r"\.gov\.sa(/|$)|\.gov(/|$)|mewa\.|sama\.|mcit\.|stats\.gov\.sa", 5, "primary_government"),
    (r"sec\.gov|esma\.europa\.eu", 5, "primary_government"),

    # Tier 4 — primary company
    (r"/10-?k/|/10-?q/|/annual-?report/|/earnings/|ir\.[a-z]+\.com", 4, "primary_company"),
    (r"\.com/pricing(/|$)|/pricing(/|$)", 4, "primary_company"),

    # Tier 3 — analyst / reputable media
    (r"mckinsey\.com|bcg\.com|bain\.com|gartner\.com|forrester\.com", 3, "analyst"),
    (r"ft\.com|reuters\.com|bloomberg\.com|wsj\.com|wamda\.com|arabnews\.com", 3, "reputable_media"),

    # Tier 2 — user-generated / community
    (r"play\.google\.com/store|apps\.apple\.com", 2, "user_reviews"),
    (r"reddit\.com|producthunt\.com|news\.ycombinator\.com", 2, "community"),

    # Tier 1 — blog / low signal
    (r"medium\.com|substack\.com|\.blog(/|$)", 1, "blog"),
]


def load_overrides(path):
    """Read a user overrides JSON file. Returns list of rule dicts. Missing → []."""
    if not os.path.isfile(path):
        return []
    with open(path) as f:
        data = json.load(f)
    return data.get("rules", [])


def merge_rules(defaults, overrides):
    """Prepend user overrides so they win on match.

    overrides: list of {pattern, score, type} dicts
    defaults: list of (pattern, score, type) tuples
    returns: list of (pattern, score, type) tuples
    """
    converted = [(o["pattern"], o["score"], o["type"]) for o in overrides]
    return converted + defaults


def grade_url(url, rules=None):
    """Return (quality_score, source_type) for a URL. Defaults to (2, 'unknown')."""
    if rules is None:
        rules = DEFAULT_RULES
    for pattern, score, stype in rules:
        if re.search(pattern, url, re.IGNORECASE):
            return (score, stype)
    return (2, "unknown")
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_evidence_quality -v`
Expected: all 13 tests pass

- [ ] **Step 6: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: 26 + 5 + 13 = 44 tests pass

- [ ] **Step 7: Commit**

```bash
git add tools/evidence_quality.py tests/test_evidence_quality.py tests/fixtures/quality-overrides.json
git commit -m "$(cat <<'EOF'
Evidence quality grading — regex rules + user overrides

URL → (score 1-5, source_type). Rule-based (regex), pure function.
9 default rule patterns cover the 5-tier taxonomy. Unknown URLs
default to (2, 'unknown') — conservative default.

User extension: drop an evidence-quality-overrides.json at project
root with {rules: [{pattern, score, type}, ...]}. Overrides win on
match via merge_rules() prepending.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: Evidence freshness module — per-source-type bands

**Files:**
- Create: `tools/evidence_freshness.py`
- Create: `tests/test_evidence_freshness.py`

Pure function: given a `source_type` and a `retrieved_at` timestamp, classify as `fresh` / `stale` / `refetch`. Reference instant is passed in (never `datetime.now()` inside the library — keeps it testable).

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_evidence_freshness.py
"""Tests for per-source-type freshness classification."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_freshness import (  # noqa: E402
    FRESHNESS_RULES,
    classify_freshness,
    days_between,
)


class TestClassifyFreshness(unittest.TestCase):
    def test_gov_source_5_days_old_is_fresh(self):
        status = classify_freshness(
            source_type="primary_government",
            retrieved_at="2026-04-11T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "fresh")

    def test_gov_source_200_days_old_is_stale(self):
        status = classify_freshness(
            source_type="primary_government",
            retrieved_at="2025-09-28T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "stale")

    def test_gov_source_3_years_old_is_refetch(self):
        status = classify_freshness(
            source_type="primary_government",
            retrieved_at="2023-04-16T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "refetch")

    def test_user_reviews_40_days_old_is_stale(self):
        # user_reviews stale at 30, refetch at 180
        status = classify_freshness(
            source_type="user_reviews",
            retrieved_at="2026-03-07T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "stale")

    def test_user_reviews_200_days_old_is_refetch(self):
        status = classify_freshness(
            source_type="user_reviews",
            retrieved_at="2025-09-28T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "refetch")

    def test_unknown_source_type_treated_as_blog_defaults(self):
        # blog thresholds: stale=90, refetch=365
        status = classify_freshness(
            source_type="made-up-type",
            retrieved_at="2026-04-15T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",
        )
        self.assertEqual(status, "fresh")

    def test_boundary_exactly_on_stale_is_stale(self):
        # stale threshold INCLUSIVE (>= stale_days)
        # blog stale=90 → day 90 is stale, day 89 is fresh
        status = classify_freshness(
            source_type="blog",
            retrieved_at="2026-01-16T00:00:00Z",
            now_iso="2026-04-16T00:00:00Z",  # 90 days
        )
        self.assertEqual(status, "stale")

    def test_all_source_types_in_rules_table(self):
        for stype in [
            "primary_government", "primary_company",
            "analyst", "reputable_media",
            "user_reviews", "community", "blog",
        ]:
            self.assertIn(stype, FRESHNESS_RULES)


class TestDaysBetween(unittest.TestCase):
    def test_zero_days(self):
        self.assertEqual(days_between("2026-04-16T00:00:00Z", "2026-04-16T00:00:00Z"), 0)

    def test_one_day(self):
        self.assertEqual(days_between("2026-04-15T00:00:00Z", "2026-04-16T00:00:00Z"), 1)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_evidence_freshness -v`
Expected: `ImportError: No module named 'evidence_freshness'`

- [ ] **Step 3: Write minimal implementation**

```python
# tools/evidence_freshness.py
"""Per-source-type freshness classification.

Fresh vs. Stale vs. Refetch is a function of (source_type, age_in_days).
Thresholds per spec:
  primary_government / reputable_media:  180 / 730
  primary_company:                        90 / 365
  analyst:                                365 / 1095
  user_reviews / community:                30 / 180
  blog:                                    90 / 365
  (unknown source_type falls back to blog)

Pure function. Caller provides 'now' as ISO 8601 — keeps this testable
without patching datetime.
"""
from datetime import datetime


FRESHNESS_RULES = {
    "primary_government":    {"stale": 180, "refetch": 730},
    "primary_company":       {"stale": 90,  "refetch": 365},
    "analyst":               {"stale": 365, "refetch": 1095},
    "reputable_media":       {"stale": 180, "refetch": 730},
    "user_reviews":          {"stale": 30,  "refetch": 180},
    "community":             {"stale": 30,  "refetch": 180},
    "blog":                  {"stale": 90,  "refetch": 365},
}

_DEFAULT = FRESHNESS_RULES["blog"]


def _parse(iso):
    return datetime.strptime(iso.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")


def days_between(earlier_iso, later_iso):
    return (_parse(later_iso) - _parse(earlier_iso)).days


def classify_freshness(source_type, retrieved_at, now_iso):
    """Return 'fresh', 'stale', or 'refetch'."""
    bands = FRESHNESS_RULES.get(source_type, _DEFAULT)
    age = days_between(retrieved_at, now_iso)
    if age >= bands["refetch"]:
        return "refetch"
    if age >= bands["stale"]:
        return "stale"
    return "fresh"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_evidence_freshness -v`
Expected: all 10 tests pass

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add tools/evidence_freshness.py tests/test_evidence_freshness.py
git commit -m "$(cat <<'EOF'
Evidence freshness — per-source-type stale/refetch bands

Classifies (source_type, retrieved_at, now) into 'fresh', 'stale',
'refetch'. Caller provides 'now' as ISO 8601 — no datetime patching
in tests.

Bands per spec: gov 180/730, company 90/365, analyst 365/1095,
media 180/730, reviews/community 30/180, blog 90/365.
Unknown source types fall back to blog thresholds.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Evidence cache — content-addressed, TTL, LRU

**Files:**
- Create: `tools/evidence_cache.py`
- Create: `tests/test_evidence_cache.py`
- Create: `assets/.forge-cache/.gitkeep`
- Modify: `.gitignore`

File-backed cache in `assets/.forge-cache/`. Key = sha256 of normalized query + URL. TTL driven by the top-tier source in the cached entry. Soft 50 MB cap with LRU eviction.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_evidence_cache.py
"""Tests for the content-addressed evidence cache."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone

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
        # Create 3 cache entries with different mtimes for LRU
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
        # Force mtimes: alpha oldest, gamma newest
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_evidence_cache -v`
Expected: `ImportError: No module named 'evidence_cache'`

- [ ] **Step 3: Write minimal implementation**

```python
# tools/evidence_cache.py
"""Content-addressed evidence cache.

Keys: sha256(normalized_query + '|' + url). Entries stored as <key>.json
in a caller-supplied cache directory (typically assets/.forge-cache/).
Reads auto-increment 'hits'. LRU eviction by mtime.
"""
import hashlib
import json
import os
import re


def normalize_query(q):
    """Lowercase, strip punctuation, collapse whitespace."""
    q = q.lower()
    q = re.sub(r"[^\w\s]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q


def make_key(query, url):
    payload = normalize_query(query) + "|" + (url or "")
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:24]


def _path(cache_dir, key):
    return os.path.join(cache_dir, f"{key}.json")


def read_cache(cache_dir, key):
    """Return the cache entry (dict) or None. Auto-increments 'hits'."""
    p = _path(cache_dir, key)
    if not os.path.isfile(p):
        return None
    with open(p) as f:
        entry = json.load(f)
    entry["hits"] = entry.get("hits", 0) + 1
    with open(p, "w") as f:
        json.dump(entry, f)
    return entry


def write_cache(cache_dir, key, entry):
    os.makedirs(cache_dir, exist_ok=True)
    with open(_path(cache_dir, key), "w") as f:
        json.dump(entry, f)


def cache_stats(cache_dir):
    if not os.path.isdir(cache_dir):
        return {"entries": 0, "size_bytes": 0}
    total = 0
    count = 0
    for f in os.listdir(cache_dir):
        if f.endswith(".json"):
            count += 1
            total += os.path.getsize(os.path.join(cache_dir, f))
    return {"entries": count, "size_bytes": total}


def evict_lru(cache_dir, keep):
    """Keep the N most-recently-used entries, delete the rest. Returns evicted keys."""
    files = [
        (f[:-5], os.path.getmtime(os.path.join(cache_dir, f)))
        for f in os.listdir(cache_dir) if f.endswith(".json")
    ]
    files.sort(key=lambda x: x[1])  # oldest first
    to_evict = files[:-keep] if len(files) > keep else []
    evicted_keys = []
    for key, _ in to_evict:
        os.remove(os.path.join(cache_dir, f"{key}.json"))
        evicted_keys.append(key)
    return evicted_keys
```

- [ ] **Step 4: Create the gitkeep + update .gitignore**

Run:

```bash
cd "/Users/lbazerbashi/Elden Studios/the-forge"
mkdir -p assets/.forge-cache
touch assets/.forge-cache/.gitkeep
```

Then edit `.gitignore` — append these lines:

```
# Evidence cache (user-local, gitignored)
assets/.forge-cache/*
!assets/.forge-cache/.gitkeep
```

(If `.gitignore` doesn't exist, create it with those 3 lines.)

- [ ] **Step 5: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_evidence_cache -v`
Expected: all 8 tests pass

- [ ] **Step 6: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add tools/evidence_cache.py tests/test_evidence_cache.py assets/.forge-cache/.gitkeep .gitignore
git commit -m "$(cat <<'EOF'
Evidence cache — content-addressed, LRU

File-backed cache at assets/.forge-cache/. sha256(normalized_query|url)
→ <key>.json entry. Reads auto-increment 'hits'. cache_stats()
reports entry count + byte size. evict_lru(keep=N) prunes by mtime.

Cache dir gitignored except for .gitkeep — shipped structure, no
shipped contents.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 5: Conflict detection — clustering, numeric divergence, scope>tier>recency resolution

**Files:**
- Create: `tools/evidence_conflict.py`
- Create: `tests/test_evidence_conflict.py`

Pure function: `detect_conflicts(evidence_list)` returns list of conflict objects. `resolve(conflict)` picks a winner by scope > tier > recency.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_evidence_conflict.py
"""Tests for conflict detection and resolution."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from evidence_conflict import (  # noqa: E402
    cluster_by_keywords,
    extract_numbers,
    detect_conflicts,
    resolve,
)


def _ev(id_, claim, source_type, retrieved_at, quality_score, excerpt=None, scope="global"):
    return {
        "id": id_, "claim": claim, "source_type": source_type,
        "quality_score": quality_score, "retrieved_at": retrieved_at,
        "excerpt": excerpt or claim, "scope": scope,
        "source_url": "", "source_title": "", "retrieved_by": [],
        "queried_via": "", "confidence": 0.8, "signal_tag": "FACT",
    }


class TestExtractNumbers(unittest.TestCase):
    def test_extracts_dollar_amounts(self):
        self.assertIn(340.0, extract_numbers("market size is $340M"))
        self.assertIn(510.0, extract_numbers("est $510M TAM"))

    def test_extracts_percentages(self):
        self.assertIn(14.0, extract_numbers("grew 14% YoY"))
        self.assertIn(18.0, extract_numbers("18% growth rate"))


class TestCluster(unittest.TestCase):
    def test_claims_sharing_keywords_cluster(self):
        items = [
            _ev("a", "Saudi pet market size 340M", "primary_government", "2026-01-01T00:00:00Z", 5),
            _ev("b", "Saudi pet market size 510M", "analyst", "2025-06-01T00:00:00Z", 3),
            _ev("c", "Unrelated topic about coffee", "blog", "2026-01-01T00:00:00Z", 1),
        ]
        clusters = cluster_by_keywords(items)
        # a and b cluster together; c alone
        self.assertEqual(len(clusters), 2)


class TestDetectConflicts(unittest.TestCase):
    def test_20pct_numeric_divergence_flags_conflict(self):
        items = [
            _ev("a", "Saudi pet market is $340M in 2024",
                "primary_government", "2026-01-01T00:00:00Z", 5),
            _ev("b", "Saudi pet market at $510M by 2024",
                "analyst", "2025-06-01T00:00:00Z", 3),
        ]
        conflicts = detect_conflicts(items)
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(set(conflicts[0]["evidence_ids"]), {"a", "b"})

    def test_5pct_divergence_is_not_a_conflict(self):
        items = [
            _ev("a", "Saudi pet market $340M", "primary_government", "2026-01-01T00:00:00Z", 5),
            _ev("b", "Saudi pet market $350M", "analyst", "2025-06-01T00:00:00Z", 3),
        ]
        self.assertEqual(detect_conflicts(items), [])

    def test_no_numeric_content_no_conflict(self):
        items = [
            _ev("a", "Saudi vets use WhatsApp", "analyst", "2026-01-01T00:00:00Z", 3),
            _ev("b", "Saudi vets prefer SMS", "analyst", "2026-01-01T00:00:00Z", 3),
        ]
        # No numeric divergence → rule-based v1 does not flag
        self.assertEqual(detect_conflicts(items), [])


class TestResolve(unittest.TestCase):
    def test_scope_beats_tier(self):
        # Saudi-scoped tier-3 vs global tier-5 → Saudi wins
        saudi = _ev("saudi", "x", "analyst", "2026-01-01T00:00:00Z", 3, scope="saudi")
        global_gov = _ev("global", "x", "primary_government", "2026-04-01T00:00:00Z", 5, scope="global")
        winner, rule = resolve({"items": [saudi, global_gov]}, brief_scope="saudi")
        self.assertEqual(winner["id"], "saudi")
        self.assertEqual(rule, "scope")

    def test_tier_beats_recency_within_same_scope(self):
        old_gov = _ev("old", "x", "primary_government", "2024-01-01T00:00:00Z", 5, scope="global")
        new_blog = _ev("new", "x", "blog", "2026-04-01T00:00:00Z", 1, scope="global")
        winner, rule = resolve({"items": [old_gov, new_blog]}, brief_scope="global")
        self.assertEqual(winner["id"], "old")
        self.assertEqual(rule, "tier")

    def test_recency_wins_within_same_scope_and_tier(self):
        older = _ev("older", "x", "analyst", "2024-01-01T00:00:00Z", 3, scope="global")
        newer = _ev("newer", "x", "analyst", "2026-04-01T00:00:00Z", 3, scope="global")
        winner, rule = resolve({"items": [older, newer]}, brief_scope="global")
        self.assertEqual(winner["id"], "newer")
        self.assertEqual(rule, "recency")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_evidence_conflict -v`
Expected: `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
# tools/evidence_conflict.py
"""Conflict detection and resolution.

v1: rule-based, deterministic.
- cluster_by_keywords: group by shared content tokens (overlap >= 0.4)
- extract_numbers: pull $ / % / bare numerics from excerpts
- detect_conflicts: within a cluster, if numeric claims diverge > 20%, flag
- resolve: pick winner by scope > tier > recency
"""
import re
from datetime import datetime


_STOPWORDS = frozenset({
    "the", "a", "an", "of", "in", "is", "and", "or", "to", "for", "on",
    "at", "by", "with", "as", "by", "from", "it", "its", "that", "this",
})


def _tokens(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return {w for w in words if w not in _STOPWORDS and len(w) > 2}


def cluster_by_keywords(items, overlap_threshold=0.4):
    """Group items whose content-word sets overlap >= threshold (Jaccard)."""
    clusters = []
    for it in items:
        placed = False
        it_tokens = _tokens(it["excerpt"])
        for cluster in clusters:
            ref_tokens = _tokens(cluster[0]["excerpt"])
            union = it_tokens | ref_tokens
            if not union:
                continue
            jaccard = len(it_tokens & ref_tokens) / len(union)
            if jaccard >= overlap_threshold:
                cluster.append(it)
                placed = True
                break
        if not placed:
            clusters.append([it])
    return clusters


def extract_numbers(text):
    """Return a list of floats extracted from $, %, or bare numbers."""
    nums = []
    for m in re.findall(r"\$?(\d+(?:\.\d+)?)\s*[MBK%]?", text):
        try:
            nums.append(float(m))
        except ValueError:
            pass
    return nums


def detect_conflicts(items, divergence=0.2):
    """Return list of {cluster, evidence_ids, divergence}."""
    conflicts = []
    for cluster in cluster_by_keywords(items):
        if len(cluster) < 2:
            continue
        nums_per_item = [(it, extract_numbers(it["excerpt"])) for it in cluster]
        nums_per_item = [(it, n) for it, n in nums_per_item if n]
        if len(nums_per_item) < 2:
            continue
        max_num = max(max(n) for _, n in nums_per_item)
        min_num = min(min(n) for _, n in nums_per_item)
        if max_num == 0:
            continue
        if (max_num - min_num) / max_num > divergence:
            conflicts.append({
                "evidence_ids": [it["id"] for it, _ in nums_per_item],
                "items": [it for it, _ in nums_per_item],
                "divergence": (max_num - min_num) / max_num,
            })
    return conflicts


def _matches_brief_scope(item, brief_scope):
    return item.get("scope", "global") == brief_scope


def resolve(conflict, brief_scope="global"):
    """Pick winner from conflict.items by scope > tier > recency.

    Returns (winner_item, rule_name).
    """
    items = conflict["items"]

    # 1. Scope: items matching the brief's scope win
    scoped = [it for it in items if _matches_brief_scope(it, brief_scope)]
    others = [it for it in items if not _matches_brief_scope(it, brief_scope)]
    if scoped and others:
        # Scope rule fires only when it actually separates items
        if len(scoped) == 1:
            return scoped[0], "scope"
        items = scoped  # tie among scoped → continue to tier

    # 2. Tier
    max_tier = max(it["quality_score"] for it in items)
    top_tier = [it for it in items if it["quality_score"] == max_tier]
    if len(top_tier) == 1:
        return top_tier[0], "tier"
    items = top_tier

    # 3. Recency
    def _at(it):
        return datetime.strptime(it["retrieved_at"].replace("Z", "+0000"),
                                  "%Y-%m-%dT%H:%M:%S%z")
    newest = max(items, key=_at)
    return newest, "recency"
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_evidence_conflict -v`
Expected: all tests pass

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add tools/evidence_conflict.py tests/test_evidence_conflict.py
git commit -m "$(cat <<'EOF'
Evidence conflict — detection + scope>tier>recency resolution

Rule-based conflict detection v1:
- Cluster Evidence by content-token Jaccard overlap (>= 0.4)
- Extract $, %, bare numerics from excerpts
- If numeric claims within a cluster diverge > 20%, flag conflict

Resolution precedence: scope > tier > recency. Brief-scoped items
beat global even if global is newer/higher-tier. Ties cascade to
next rule. Semantic (non-numeric) conflict detection deferred to v2.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: Extend validator — validate_evidence() + --cache-stats

**Files:**
- Modify: `tools/validator.py`
- Modify: `tests/test_validator.py`

Adds `validate_evidence(evidence_doc, state)` with full rule coverage. Extends `validate_project()` to load `forge-evidence.json` when present. Adds `--cache-stats` CLI flag. **Code review gate fires after this task.**

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_validator.py` a new class:

```python
class TestValidateEvidence(unittest.TestCase):
    """validate_evidence(doc, state) -> (ok, errors)"""

    def _doc(self, evidence=None, index=None):
        return {
            "evidence": evidence or [],
            "project_evidence_index": index or {},
        }

    def _state(self, agent_ids=("agent-vexx",)):
        return {
            "agents": [{"id": a, "name": a, "status": "active"} for a in agent_ids]
        }

    def _ev(self, **kwargs):
        base = {
            "id": "ev-abc123", "claim": "c", "source_url": "https://a.com",
            "source_title": "t", "source_type": "primary_government",
            "quality_score": 5, "retrieved_at": "2026-04-16T00:00:00Z",
            "retrieved_by": ["agent-vexx"], "queried_via": "WebSearch",
            "excerpt": "e", "confidence": 0.8, "signal_tag": "FACT",
        }
        base.update(kwargs)
        return base

    def test_empty_doc_passes(self):
        from validator import validate_evidence
        ok, errors = validate_evidence(self._doc(), self._state())
        self.assertTrue(ok, errors)

    def test_index_references_missing_evidence_fails(self):
        from validator import validate_evidence
        doc = self._doc(index={"proj-001": ["ev-ghost"]})
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("ev-ghost" in e for e in errors), errors)

    def test_retrieved_by_references_missing_agent_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(retrieved_by=["agent-ghost"])])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("agent-ghost" in e for e in errors), errors)

    def test_quality_score_out_of_range_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(quality_score=9)])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("quality_score" in e for e in errors), errors)

    def test_confidence_out_of_range_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(confidence=2.0)])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)

    def test_bad_signal_tag_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(signal_tag="MAYBE")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)

    def test_bad_source_type_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(source_type="made-up")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)

    def test_malformed_retrieved_at_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(retrieved_at="last tuesday")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)

    def test_malformed_source_url_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(source_url="not a url")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)

    def test_local_scheme_url_allowed(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(source_url="local://cache/xyz.html")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertTrue(ok, errors)

    def test_duplicate_evidence_ids_fails(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(id="ev-dup"), self._ev(id="ev-dup")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("ev-dup" in e and "duplicate" in e.lower() for e in errors), errors)

    def test_validate_project_loads_evidence_file_when_present(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                json.dump({
                    "company": {"name": "T", "founded": "2026-01-01"},
                    "departments": [], "agents": [],
                }, f)
            with open(os.path.join(tmp, "forge-evidence.json"), "w") as f:
                json.dump({"evidence": [], "project_evidence_index": {}}, f)
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, errors)

    def test_validate_project_catches_malformed_evidence_json(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                json.dump({
                    "company": {"name": "T", "founded": "2026-01-01"},
                    "departments": [], "agents": [],
                }, f)
            with open(os.path.join(tmp, "forge-evidence.json"), "w") as f:
                f.write("{ broken ]")
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("forge-evidence.json" in e and "json" in e.lower() for e in errors),
                errors,
            )


class TestCacheStatsCli(unittest.TestCase):
    def test_cache_stats_flag_exits_zero_and_prints_stats(self):
        from validator import main
        buf = io.StringIO()
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "assets", ".forge-cache"))
            # Write a fake cache entry
            with open(os.path.join(tmp, "assets", ".forge-cache", "abc.json"), "w") as f:
                f.write('{"key":"abc","query":"q","results":[],"fetched_at":"2026-04-16T00:00:00Z","hits":0}')
            with redirect_stdout(buf):
                rc = main(["--cache-stats", tmp])
            self.assertEqual(rc, 0)
            self.assertIn("entries", buf.getvalue().lower())
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_validator.TestValidateEvidence -v`
Expected: `ImportError: cannot import name 'validate_evidence'`

- [ ] **Step 3: Write minimal implementation**

Modify `tools/validator.py`. Add near the existing imports:

```python
from urllib.parse import urlparse
```

Add new function near other validators (after `validate_tasks`):

```python
def validate_evidence(evidence_doc, state):
    """Validate forge-evidence.json against forge-state.json.

    Returns (ok, errors).
    """
    from evidence_schema import SOURCE_TYPES, SIGNAL_TAGS  # imported here to avoid cycle

    errors = []
    items = evidence_doc.get("evidence", [])
    index = evidence_doc.get("project_evidence_index", {})
    agent_ids = {a["id"] for a in state.get("agents", [])}

    # Every ID unique
    seen = {}
    for it in items:
        eid = it.get("id", "(unnamed)")
        if eid in seen:
            errors.append(f"Evidence duplicate id: {eid}")
        seen[eid] = True

    valid_ids = set(seen.keys())

    # Index references point to real evidence
    for proj, ids in index.items():
        for ref in ids:
            if ref not in valid_ids:
                errors.append(
                    f"project_evidence_index[{proj}] references non-existent Evidence: {ref}"
                )

    # Per-item field validation
    for it in items:
        eid = it.get("id", "(unnamed)")
        for agent in it.get("retrieved_by", []) or []:
            if agent not in agent_ids:
                errors.append(f"Evidence {eid} retrieved_by references non-existent agent: {agent}")
        q = it.get("quality_score")
        if not isinstance(q, int) or q < 1 or q > 5:
            errors.append(f"Evidence {eid} quality_score out of range: {q}")
        c = it.get("confidence")
        if not isinstance(c, (int, float)) or c < 0 or c > 1:
            errors.append(f"Evidence {eid} confidence out of range: {c}")
        if it.get("source_type") not in SOURCE_TYPES:
            errors.append(f"Evidence {eid} invalid source_type: {it.get('source_type')}")
        if it.get("signal_tag") not in SIGNAL_TAGS:
            errors.append(f"Evidence {eid} invalid signal_tag: {it.get('signal_tag')}")
        url = it.get("source_url", "")
        if url.startswith("local://"):
            pass
        else:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"Evidence {eid} invalid source_url: {url}")
        ts = it.get("retrieved_at", "")
        try:
            json.loads(json.dumps(ts))  # ensure it's a string
            # strict ISO 8601 UTC parse
            from datetime import datetime
            datetime.strptime(ts.replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")
        except (ValueError, TypeError):
            errors.append(f"Evidence {eid} malformed retrieved_at: {ts}")

    return (len(errors) == 0, errors)
```

Modify `validate_project()` — add after the tasks block:

```python
    ev_path = os.path.join(project_dir, "forge-evidence.json")
    if os.path.isfile(ev_path):
        try:
            with open(ev_path) as f:
                evidence_doc = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"forge-evidence.json is not valid json: {e}")
            return (False, errors)
        errors.extend(validate_evidence(evidence_doc, state)[1])
```

Modify `main(argv)` — add `--cache-stats` handling at the top:

```python
def main(argv):
    if argv and argv[0] == "--cache-stats":
        from evidence_cache import cache_stats
        project_dir = argv[1] if len(argv) > 1 else os.getcwd()
        stats = cache_stats(os.path.join(project_dir, "assets", ".forge-cache"))
        print(f"Cache stats: {stats['entries']} entries, {stats['size_bytes']} bytes")
        return 0
    project_dir = argv[0] if argv else os.getcwd()
    ok, errors = validate_project(project_dir)
    if ok:
        print(f"OK — {project_dir} passed all validation checks")
        return 0
    print(f"FAIL — {len(errors)} validation error(s) in {project_dir}:")
    for i, e in enumerate(errors, 1):
        print(f"  {i}. {e}")
    return 1
```

Also at the top of `tools/validator.py`, ensure `sys.path` includes its own dir so the inline `from evidence_schema import ...` works when invoked from anywhere:

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

(Place this right after the existing `import sys`.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_validator -v`
Expected: all 26 + 13 new = 39 tests pass

- [ ] **Step 5: Initialize the real forge-evidence.json**

Run:

```bash
cd "/Users/lbazerbashi/Elden Studios/the-forge"
cat > forge-evidence.json <<'EOF'
{
  "evidence": [],
  "project_evidence_index": {}
}
EOF
```

Then verify the real project still validates:

```bash
python3 tools/validator.py
```

Expected: `OK — ... passed all validation checks`

- [ ] **Step 6: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass

- [ ] **Step 7: Commit**

```bash
git add tools/validator.py tests/test_validator.py forge-evidence.json
git commit -m "$(cat <<'EOF'
Validator — add validate_evidence() + --cache-stats CLI flag

Extends validator with forge-evidence.json coverage:
- Evidence ID uniqueness
- project_evidence_index refs must exist
- retrieved_by agents must exist
- quality_score in [1,5], confidence in [0,1]
- source_type in allowed enum, signal_tag in allowed enum
- source_url must be valid URL or local:// scheme
- retrieved_at must parse as ISO 8601 UTC

validate_project() auto-loads forge-evidence.json when present and
reports malformed JSON with a readable error (no traceback).

New CLI flag: validator.py --cache-stats [dir] reports cache entry
count and byte size.

Initialized empty forge-evidence.json at project root; real project
validates cleanly.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### 🛑 CODE REVIEW GATE

Foundation complete. Before proceeding to orchestration, invoke `superpowers:requesting-code-review` on commits from Task 1 through Task 6. Address Critical + Important findings before Task 7. Minor findings noted for Task 14's final review.

---

## Task 7: Sub-brief generation + orchestrator skeleton (dry-run, no real calls)

**Files:**
- Create: `tools/evidence_orchestrator.py`
- Create: `tests/test_evidence_orchestrator.py`

Generates per-agent sub-briefs (Flint's job). Accepts subagent returns and produces a unified bundle. **No real WebSearch yet** — fan-in merge and sub-brief shape are the surfaces here.

- [ ] **Step 1: Write the failing tests**

```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_evidence_orchestrator -v`
Expected: `ImportError`

- [ ] **Step 3: Write minimal implementation**

```python
# tools/evidence_orchestrator.py
"""Evidence orchestration — sub-brief generation + fan-in merge.

No real network calls here. Consumes subagent return envelopes and
produces a unified evidence bundle + meta stats.
"""
import re


EVIDENCE_AGENTS = {
    "agent-vexx": {
        "display_name": "Vex",
        "domain": "Market Intelligence",
        "default_preferences": "Prefer analyst reports and primary company filings",
    },
    "agent-nyxx": {
        "display_name": "Nyx",
        "domain": "Saudi Market",
        "default_preferences": "Saudi-specific sources (MEWA, SAMA, MCIT, Wamda) preferred over global",
    },
    "agent-echo": {
        "display_name": "Echo",
        "domain": "User Research",
        "default_preferences": "Prefer direct user signal: App Store, Play Store, Reddit, Product Hunt",
    },
    "agent-taln": {
        "display_name": "Talon",
        "domain": "Growth Architecture",
        "default_preferences": "Prefer competitor pricing pages, ad creatives, landing page teardowns",
    },
}


# Keyword → agent relevance heuristic (matches SKILL.md routing rubric style)
_RELEVANCE_KEYWORDS = {
    "agent-vexx": [
        "competitor", "market", "TAM", "tam", "pricing", "funding",
        "benchmarks", "landscape", "competitive",
    ],
    "agent-nyxx": [
        "saudi", "ksa", "mena", "arabic", "vision 2030", "nafath",
        "absher", "tawakkalna", "mada", "stc pay", "riyadh",
    ],
    "agent-echo": [
        "user", "persona", "interview", "research", "review", "feedback",
        "adoption", "behavior", "pain point", "jobs to be done",
    ],
    "agent-taln": [
        "growth", "aarrr", "funnel", "acquisition", "retention",
        "monetization", "distribution", "seo", "aso", "paid",
        "viral", "channel",
    ],
}


def score_agent_relevance(agent_id, brief):
    """Return 0-3 relevance. 3 = lead agent, 2 = activated, 0-1 = skip."""
    text = brief.lower()
    hits = sum(1 for kw in _RELEVANCE_KEYWORDS.get(agent_id, []) if kw in text)
    if hits >= 3:
        return 3
    if hits >= 1:
        return 2
    return 0


def generate_sub_brief(agent_id, brief, evidence_budget=8, quality_floor=3):
    """Return a sub-brief template string."""
    meta = EVIDENCE_AGENTS[agent_id]
    return f"""AGENT: {meta['display_name']} ({meta['domain']})
ORIGINAL BRIEF: {brief}

YOUR SUB-BRIEF:
Primary question: Evaluate the brief from your domain lens and surface
the evidence a VP would need to defend a decision.

Secondary questions (fill in based on your brain file template):
- What are the 3 most important data points in your domain?
- What's the strongest counter-evidence to the brief's assumptions?
- What gap in your domain can you NOT close with evidence (flag honestly)?

CONSTRAINTS:
- Evidence budget: {evidence_budget} queries max
- Quality floor: {quality_floor} (tier-3 analyst/reputable media or higher)
- {meta['default_preferences']}

RETURN (structured JSON envelope):
- 5-12 Evidence objects (full schema, including id, source_url, source_type,
  quality_score, retrieved_at, retrieved_by, queried_via, excerpt,
  confidence, signal_tag)
- Recommendation (1 paragraph)
- Confidence 0-1 with one-sentence reasoning
- Gaps: list of domain questions you could NOT answer with evidence
"""


def merge_returns(returns):
    """Fan-in merge of N subagent returns.

    Dedupes Evidence by source_url; retrieved_by grows into a list.
    Returns a unified bundle: {evidence, agents, total_queries, avg_quality, recommendations}
    """
    by_url = {}
    agents = []
    total_q = 0
    quality_vals = []
    recommendations = []

    for ret in returns:
        agents.append(ret["agent_id"])
        total_q += ret.get("queried_count", 0)
        if ret.get("quality_avg") is not None:
            quality_vals.append(ret["quality_avg"])
        recommendations.append({
            "agent_id": ret["agent_id"],
            "recommendation": ret.get("recommendation", ""),
            "confidence": ret.get("confidence", 0.0),
        })

        for ev in ret.get("evidence", []):
            url = ev.get("source_url", ev.get("id"))
            if url in by_url:
                # Merge retrieved_by
                existing_by = by_url[url].setdefault("retrieved_by", [])
                for agent in ev.get("retrieved_by", []):
                    if agent not in existing_by:
                        existing_by.append(agent)
            else:
                by_url[url] = dict(ev)

    return {
        "evidence": list(by_url.values()),
        "agents": agents,
        "total_queries": total_q,
        "avg_quality": sum(quality_vals) / len(quality_vals) if quality_vals else 0.0,
        "recommendations": recommendations,
    }
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_evidence_orchestrator -v`
Expected: all 8 tests pass

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add tools/evidence_orchestrator.py tests/test_evidence_orchestrator.py
git commit -m "$(cat <<'EOF'
Evidence orchestrator — sub-brief generation + fan-in merge

Pure-function orchestration surface (no network calls yet):
- EVIDENCE_AGENTS table: the 4 research agents (Vex, Nyx, Echo, Talon)
- score_agent_relevance(): keyword-based 0-3 relevance matching
  SKILL.md routing rubric style
- generate_sub_brief(): fills the spec's sub-brief template with
  per-agent preferences, evidence budget, quality floor, and JSON
  return envelope contract
- merge_returns(): fan-in merge deduping by source_url, growing
  retrieved_by into an array so cross-agent source reuse is visible

Real dispatch shells (WebSearch, superpowers:dispatching-parallel-agents)
wired in Task 8.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Append-to-evidence + signal-tag enforcement helpers

**Files:**
- Modify: `tools/evidence_orchestrator.py`
- Modify: `tests/test_evidence_orchestrator.py`

Adds `append_evidence(project_id, bundle, evidence_path)` — the persistence path that writes merged Evidence into `forge-evidence.json`. Adds `strip_unsupported_claims(text, evidence_ids)` — Standing Rule 7 enforcement.

- [ ] **Step 1: Write failing tests — append to `tests/test_evidence_orchestrator.py`**

```python
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


class TestStripUnsupported(unittest.TestCase):
    def test_fact_with_valid_evidence_id_is_kept(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "Market grew 14% YoY [FACT: ev-abc123]."
        out = strip_unsupported_claims(text, {"ev-abc123"})
        self.assertIn("[FACT: ev-abc123]", out)

    def test_fact_without_evidence_id_is_stripped(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "Market grew 14% YoY [FACT]."
        out = strip_unsupported_claims(text, set())
        self.assertIn("[UNSUPPORTED", out)
        self.assertNotIn("[FACT]", out)

    def test_fact_with_unknown_evidence_id_is_stripped(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "Market grew 14% YoY [FACT: ev-ghost]."
        out = strip_unsupported_claims(text, {"ev-real"})
        self.assertIn("[UNSUPPORTED", out)

    def test_opinion_tags_are_left_alone(self):
        from evidence_orchestrator import strip_unsupported_claims

        text = "The market feels underserved [OPINION]."
        out = strip_unsupported_claims(text, set())
        self.assertEqual(out, text)
```

- [ ] **Step 2: Run tests — verify RED**

Run: `python3 -m unittest tests.test_evidence_orchestrator -v`
Expected: 3 new classes fail with `AttributeError` or `ImportError`

- [ ] **Step 3: Add the two functions to `tools/evidence_orchestrator.py`**

Append:

```python
import json as _json
import re as _re


def append_evidence(project_id, bundle, evidence_path):
    """Persist merged bundle Evidence to forge-evidence.json."""
    with open(evidence_path) as f:
        doc = _json.load(f)

    existing_ids = {e["id"] for e in doc.get("evidence", [])}
    for ev in bundle.get("evidence", []):
        if ev["id"] not in existing_ids:
            doc["evidence"].append(ev)
            existing_ids.add(ev["id"])

    index = doc.setdefault("project_evidence_index", {})
    current = set(index.get(project_id, []))
    current.update(e["id"] for e in bundle.get("evidence", []))
    index[project_id] = sorted(current)

    with open(evidence_path, "w") as f:
        _json.dump(doc, f, indent=2)


# Matches [FACT], [FACT: ev-xxx], [INFERENCE], [INFERENCE: ev-xxx]
_CLAIM_RE = _re.compile(r"\[(FACT|INFERENCE)(?::\s*(ev-[0-9a-f]+))?\]")


def strip_unsupported_claims(text, valid_evidence_ids):
    """Enforce Standing Rule 7: no citation → no claim.

    Replaces any [FACT] / [INFERENCE] without a valid Evidence ID
    with [UNSUPPORTED — dropped by validator]. Leaves [OPINION] and
    [HYPOTHESIS] alone.
    """
    def _sub(m):
        tag, eid = m.group(1), m.group(2)
        if eid and eid in valid_evidence_ids:
            return m.group(0)
        return "[UNSUPPORTED — dropped by validator]"

    return _CLAIM_RE.sub(_sub, text)
```

- [ ] **Step 4: Run tests — verify GREEN**

Run: `python3 -m unittest tests.test_evidence_orchestrator -v`
Expected: all tests pass

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass

- [ ] **Step 6: Commit**

```bash
git add tools/evidence_orchestrator.py tests/test_evidence_orchestrator.py
git commit -m "$(cat <<'EOF'
Orchestrator — append_evidence() + strip_unsupported_claims()

Two protocol-level helpers:

append_evidence(project_id, bundle, path): persists merged Evidence
to forge-evidence.json. Dedupes by Evidence id; project_evidence_index
entries extend rather than replace when the project already has
Evidence. Writes indented JSON for readable diffs.

strip_unsupported_claims(text, valid_ids): enforces Standing Rule 7
mechanically. [FACT] / [INFERENCE] without a valid ev-* ID gets
replaced with [UNSUPPORTED — dropped by validator]. [OPINION] and
[HYPOTHESIS] untouched.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Sources Appendix renderer — compact (terminal) + full (Markdown)

**Files:**
- Create: `tools/evidence_appendix.py`
- Create: `tests/test_evidence_appendix.py`

Renders two formats: compact (for terminal output in SKILL.md responses) and full Markdown (for exports).

- [ ] **Step 1: Write failing tests**

```python
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
        items = [_ev("a", "Source A"), _ev("b", "Source B"), _ev("c", "Source C")]
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
```

- [ ] **Step 2: RED**

Run: `python3 -m unittest tests.test_evidence_appendix -v`
Expected: ImportError

- [ ] **Step 3: Implement**

```python
# tools/evidence_appendix.py
"""Sources Appendix rendering — compact terminal + full Markdown."""
from collections import defaultdict


_TIER_HEADERS = {
    5: "⭐⭐⭐⭐⭐ Primary Government",
    4: "⭐⭐⭐⭐ Primary Company",
    3: "⭐⭐⭐ Analyst / Media",
    2: "⭐⭐ User / Community",
    1: "⭐ Blog / Low Signal",
}


def _group_by_tier(items):
    groups = defaultdict(list)
    for it in items:
        groups[it["quality_score"]].append(it)
    return groups


def render_compact(items):
    """One line per source, grouped by tier. For terminal output."""
    if not items:
        return ""
    groups = _group_by_tier(items)
    lines = []
    for tier in sorted(groups.keys(), reverse=True):
        header = _TIER_HEADERS.get(tier, f"Tier {tier}")
        lines.append(f"{header} ({len(groups[tier])})")
        for it in groups[tier]:
            lines.append(f"  [{it['id']}] {it['source_title']} — {it['source_url']}")
    return "\n".join(lines)


def render_markdown(items):
    """Full Markdown appendix with excerpts and metadata. For exports."""
    if not items:
        return "## Sources Appendix\n\n_No sources cited._\n"
    groups = _group_by_tier(items)
    out = ["## Sources Appendix\n"]
    for tier in sorted(groups.keys(), reverse=True):
        header = _TIER_HEADERS.get(tier, f"Tier {tier}")
        out.append(f"### {header} ({len(groups[tier])})\n")
        for it in groups[tier]:
            date = it["retrieved_at"][:10]
            agents = ", ".join(it.get("retrieved_by", []))
            out.append(f"- **[{it['id']}] {it['source_title']}**")
            out.append(f"  - URL: {it['source_url']}")
            out.append(f"  - Retrieved: {date} by {agents}")
            out.append(f"  - Excerpt: {it['excerpt']!r}")
            out.append("")
    return "\n".join(out)


def _format_elapsed(sec):
    if sec < 60:
        return f"{sec}s"
    m, s = divmod(sec, 60)
    return f"{m}m {s:02d}s"


def render_summary_block(items, total_queries, elapsed_sec, cache_hits, conflicts):
    """The Evidence Summary block that sits above the recommendation."""
    if not items:
        avg = 0.0
    else:
        avg = sum(it["quality_score"] for it in items) / len(items)
    thin = sum(1 for it in items if it["quality_score"] == 1)
    return (
        f"EVIDENCE SUMMARY\n"
        f"  {total_queries} queries across 4 agents   |   {len(items)} sources cited\n"
        f"  Avg quality: {avg:.1f}/5              |   Conflicts: {conflicts}\n"
        f"  ⚠ Thin evidence: {thin}                |   Cache hits: {cache_hits}/{total_queries}\n"
        f"  Elapsed: {_format_elapsed(elapsed_sec)}\n"
    )
```

- [ ] **Step 4: GREEN**

Run: `python3 -m unittest tests.test_evidence_appendix -v`
Expected: all pass

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`

- [ ] **Step 6: Commit**

```bash
git add tools/evidence_appendix.py tests/test_evidence_appendix.py
git commit -m "$(cat <<'EOF'
Sources Appendix renderer — compact + Markdown

Two rendering modes:
- render_compact(): grouped-by-tier, one line per source — for
  terminal output inside SKILL.md responses
- render_markdown(): full appendix with excerpts, retrieval date,
  citing agents — for export / sharing
- render_summary_block(): the EVIDENCE SUMMARY box above the
  recommendation (queries, avg quality, conflicts, cache hit rate,
  elapsed)

All three are pure functions over the canonical Evidence dicts.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: SKILL.md — Phase 2 rewrite + Evidence Pipes section

**Files:**
- Modify: `SKILL.md`
- Modify: `references/collaboration-protocol.md`

Documentation update. No tests required — these are instructions to the orchestrator agent (Claude operating the skill). But the docs must match the code shipped in Tasks 1-9 exactly.

- [ ] **Step 1: Add new section to `SKILL.md`**

Insert the following **before** the existing "Collaboration Protocol" section in `SKILL.md`:

```markdown
---

## Evidence Pipes

When `evidence_pipes.enabled` is `true` in `forge-state.json` (default), Phase 2 (Intelligence) runs in parallel-dispatch mode. The four **evidence agents** — Vex, Nyx, Echo, Talon — fan out as independent subagents, each running real WebSearch (and Chrome MCP in phase 2) against their sub-brief.

### When to dispatch

- Brief has substantive research questions (not a trivial "show office" / "team roster" command)
- At least one evidence agent scores ≥ 2 on the relevance rubric
- `evidence_pipes.enabled` is not explicitly `false` in state
- User didn't say "no evidence" / "skip research" / "just use existing knowledge"

### Dispatch flow

1. Read `forge-state.json` — check `evidence_pipes.enabled` and the 4 evidence agents' status
2. Score each evidence agent's relevance using `evidence_orchestrator.score_agent_relevance()`
3. For each activated agent, generate a sub-brief using `evidence_orchestrator.generate_sub_brief()`
4. Dispatch all activated sub-briefs in parallel via `superpowers:dispatching-parallel-agents`
5. Each subagent must return a structured JSON envelope:
   ```json
   {
     "agent_id": "agent-vexx",
     "evidence": [<Evidence objects with full schema>],
     "recommendation": "<paragraph>",
     "confidence": 0.78,
     "queried_count": 6,
     "quality_avg": 3.8,
     "gaps": ["<question they couldn't answer with evidence>"]
   }
   ```
6. Fan-in: call `evidence_orchestrator.merge_returns()` on the returns list
7. Persist via `evidence_orchestrator.append_evidence(project_id, merged, "forge-evidence.json")`
8. Run `evidence_conflict.detect_conflicts()` on merged Evidence; surface conflicts into the War Room (Phase 3)
9. Before writing the final deliverable, run `evidence_orchestrator.strip_unsupported_claims()` on every agent contribution — any `[FACT]` without a valid Evidence ID gets replaced with `[UNSUPPORTED — dropped by validator]`

### Failure modes

- **Subagent error / timeout:** note `⚠ <Agent> unavailable — proceeding without <domain> data` in the deliverable. Don't fabricate.
- **Malformed Evidence JSON in return:** validator.validate_evidence() catches; re-prompt subagent once, then flag.
- **Saudi-specific query returns zero usable results:** agent falls back to persona-reasoned claims tagged `[OPINION]`, **never** invent `[FACT]`.
- **Total budget exhausted:** stop dispatching, deliver with `⚠ Budget exhausted` note.

### Budgets

- Total queries per brief: 40 (soft), 60 (hard)
- Per-agent queries: 8
- Wall-clock deadline: 4 min for all parallel agents
- Chrome MCP (phase 2): 5 concurrent tabs, 15 pages per brief

### Kill switch

- In `forge-state.json`: `"evidence_pipes": { "enabled": false }` → v3.0 sequential behavior, zero pipe cost
- User phrase: "no evidence" / "skip pipes" / "just use existing knowledge" → skip dispatch for this brief only
```

- [ ] **Step 2: Update the existing "Collaboration Protocol" section in `SKILL.md`**

Find the Phase 2 (Intelligence) description in `SKILL.md`. Replace the sequential-dispatch description with a pointer:

> Phase 2 now runs via parallel dispatch when pipes are enabled. See the "Evidence Pipes" section above. Sequential behavior preserved when `evidence_pipes.enabled: false`.

- [ ] **Step 3: Update the "Output Format" section in `SKILL.md`**

Add two items to the output requirements list:

- When Evidence was gathered, deliverable includes an EVIDENCE SUMMARY block (use `evidence_appendix.render_summary_block`) above the recommendation
- Deliverable ends with a Sources Appendix (use `evidence_appendix.render_compact` for inline, `render_markdown` for export)
- Every `[FACT]` / `[INFERENCE]` must reference a valid Evidence ID or be downgraded to `[OPINION]`

- [ ] **Step 4: Update Quality Standards**

Add this bullet:

> **No citation, no claim.** Every `[FACT]` or `[INFERENCE]` tag must reference a valid Evidence ID. The validator strips non-compliant claims automatically; agents must re-run queries or downgrade the claim to `[OPINION]`.

- [ ] **Step 5: Update `references/collaboration-protocol.md` — v3.0 → v3.1**

Bump the header from `v3.0` to `v3.1`. Add three new Standing Rules:

```markdown
7. **No citation, no claim.** Any `[FACT]` or `[INFERENCE]` without an Evidence ID gets stripped and replaced with `[UNSUPPORTED — dropped by validator]`. Agent must re-run the query or downgrade to `[OPINION]`.
8. **Quality floor for GO decisions.** Any GO recommendation citing ≥1 tier-1 (blog) source without tier-3+ backing is flagged `⚠ THIN EVIDENCE` in the deliverable.
9. **Freshness gate.** Evidence beyond the source-type's `stale` threshold is flagged `⏰ STALE`. Beyond `refetch` threshold → `⏰ REFETCH REQUIRED` (must re-query before citing).
```

Rewrite the Phase 2 section to match the new parallel-dispatch flow (copy from the "Evidence Pipes" section in SKILL.md Step 1 above, and add a reference back to SKILL.md for the authoritative version).

- [ ] **Step 6: Update `forge-state.json`**

Add the flag at the top level:

```json
"evidence_pipes": {
  "enabled": true
}
```

Run: `python3 tools/validator.py`
Expected: `OK — ... passed all validation checks`

- [ ] **Step 7: Run full test suite**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass (no test changes needed; docs-only task).

- [ ] **Step 8: Commit**

```bash
git add SKILL.md references/collaboration-protocol.md forge-state.json
git commit -m "$(cat <<'EOF'
SKILL.md + protocol v3.1 — Evidence Pipes section, Phase 2 rewrite

Doc updates only; no code changes.

SKILL.md:
- NEW 'Evidence Pipes' section: when to dispatch, 9-step flow,
  failure modes, budgets, kill switch
- Phase 2 pointer to new section
- Output Format: EVIDENCE SUMMARY + Sources Appendix required when
  pipes fire
- Quality Standards: 'No citation, no claim.' made explicit

collaboration-protocol.md:
- Bumped v3.0 → v3.1
- Standing Rules 7, 8, 9 added (citation, quality floor, freshness)
- Phase 2 rewritten for parallel dispatch

forge-state.json: evidence_pipes.enabled = true (default).
Real project validates cleanly.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: Dashboard Evidence block on Mission Control tab

**Files:**
- Modify: `assets/dashboard.html`

Add an Evidence metrics block under the phase bar on tab 1. Reads `forge-evidence.json` (the one synced into `assets/`) via fetch.

- [ ] **Step 1: Open `assets/dashboard.html` and find the Mission Control tab container**

Look for the element that holds the phase bar (search for "phase" in the file). The Evidence block goes directly under that.

- [ ] **Step 2: Add the Evidence block HTML**

Insert (adjust class names to match the existing pattern in the file):

```html
<section id="evidence-block" class="evidence-block" style="margin-top: 16px;">
  <div class="evidence-header">
    <span>Evidence</span>
    <span id="evidence-status" style="font-size: 11px; opacity: 0.7;">—</span>
  </div>
  <div class="evidence-metrics" style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;">
    <div class="metric">
      <div class="metric-label">Queries</div>
      <div class="metric-value" id="ev-queries">0 / 40</div>
    </div>
    <div class="metric">
      <div class="metric-label">Sources cited</div>
      <div class="metric-value" id="ev-cited">0</div>
    </div>
    <div class="metric">
      <div class="metric-label">Avg quality</div>
      <div class="metric-value" id="ev-quality">— ★</div>
    </div>
    <div class="metric">
      <div class="metric-label">Cache hit rate</div>
      <div class="metric-value" id="ev-cache">0%</div>
    </div>
  </div>
  <div id="ev-freshness" style="display: flex; gap: 8px; margin-top: 10px; font-size: 11px;">
    <span class="agent-fresh" data-agent="Vex">● Vex</span>
    <span class="agent-fresh" data-agent="Nyx">● Nyx</span>
    <span class="agent-fresh" data-agent="Echo">● Echo</span>
    <span class="agent-fresh" data-agent="Talon">● Talon</span>
  </div>
</section>
```

- [ ] **Step 3: Add the render function**

Find the existing state-refresh interval in the `<script>` block (search for `setInterval` or `fetch('forge`). Add an `fetchEvidence()` function and call it alongside the existing refresh:

```javascript
async function fetchEvidence() {
  try {
    const res = await fetch('forge-evidence.json', { cache: 'no-store' });
    if (!res.ok) return;
    const doc = await res.json();
    renderEvidenceBlock(doc);
  } catch (e) {
    // file may not exist yet — render empty state
    renderEvidenceBlock({ evidence: [], project_evidence_index: {} });
  }
}

function renderEvidenceBlock(doc) {
  const items = doc.evidence || [];
  const total = items.length;
  const avg = total ? (items.reduce((a, x) => a + (x.quality_score || 0), 0) / total) : 0;

  document.getElementById('ev-cited').textContent = total;
  document.getElementById('ev-quality').textContent =
    total ? `${avg.toFixed(1)} ★` : '— ★';

  // Freshness per agent (red if any evidence > 180d, amber > 90d, else green)
  ['Vex','Nyx','Echo','Talon'].forEach(name => {
    const agentId = { Vex:'agent-vexx', Nyx:'agent-nyxx', Echo:'agent-echo', Talon:'agent-taln' }[name];
    const agentItems = items.filter(i => (i.retrieved_by || []).includes(agentId));
    const el = document.querySelector(`.agent-fresh[data-agent="${name}"]`);
    if (!el) return;
    if (!agentItems.length) { el.style.color = '#666'; return; }
    const ages = agentItems.map(i => (Date.now() - new Date(i.retrieved_at).getTime()) / (1000*60*60*24));
    const worst = Math.max(...ages);
    el.style.color = worst > 180 ? '#ff5555' : worst > 90 ? '#ffaa00' : '#55ff88';
  });
}

// Kick off on load + on refresh interval
document.addEventListener('DOMContentLoaded', () => {
  fetchEvidence();
  setInterval(fetchEvidence, 3000);
});
```

- [ ] **Step 4: Open the dashboard and verify visually**

Run: `open "http://localhost:8765/dashboard.html"` (or double-click the desktop launcher after restart)

Expected: Evidence block renders with placeholder values (0 queries, — ★, all agent freshness dots gray since no Evidence exists yet).

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass (no test changes — this is a UI-only task).

- [ ] **Step 6: Commit**

```bash
git add assets/dashboard.html
git commit -m "$(cat <<'EOF'
Dashboard — Evidence block on Mission Control tab

Under the phase bar: 4 metric cards (queries, sources cited, avg
quality, cache hit rate) + a freshness row with a colored dot per
evidence agent.

Dot color: green < 90d worst age, amber 90-180d, red > 180d, gray
if agent has contributed no evidence.

Refreshes every 3s alongside the existing state/tasks polling.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: Dashboard Sources tab (tab 5) — filter, search, export

**Files:**
- Modify: `assets/dashboard.html`

Adds a dedicated Sources tab with an Evidence table, tier/agent/freshness filters, a search box, and Markdown/CSV/JSON export.

- [ ] **Step 1: Add the tab button to the existing tab nav**

Find the tab-nav element in `dashboard.html` (search for tab labels like "Mission Control", "Network"). Add a new button:

```html
<button class="tab-btn" data-tab="sources">Sources</button>
```

- [ ] **Step 2: Add the tab panel markup**

Directly after the last existing tab panel, add:

```html
<section id="tab-sources" class="tab-panel" style="display: none;">
  <div class="sources-toolbar" style="display: flex; gap: 12px; margin-bottom: 12px; flex-wrap: wrap;">
    <input id="src-search" placeholder="Search claim or source title…" style="flex: 1; min-width: 200px; padding: 6px;"/>
    <select id="src-tier"><option value="">All tiers</option><option>5</option><option>4</option><option>3</option><option>2</option><option>1</option></select>
    <select id="src-agent">
      <option value="">All agents</option>
      <option value="agent-vexx">Vex</option>
      <option value="agent-nyxx">Nyx</option>
      <option value="agent-echo">Echo</option>
      <option value="agent-taln">Talon</option>
    </select>
    <select id="src-fresh">
      <option value="">All freshness</option>
      <option value="fresh">Fresh</option>
      <option value="stale">Stale</option>
      <option value="refetch">Refetch</option>
    </select>
    <button id="src-export-md">Export MD</button>
    <button id="src-export-csv">Export CSV</button>
    <button id="src-export-json">Export JSON</button>
  </div>
  <table id="src-table" style="width:100%; border-collapse: collapse;">
    <thead>
      <tr>
        <th>ID</th><th>Claim</th><th>Source</th><th>Tier</th><th>Agent</th><th>Retrieved</th>
      </tr>
    </thead>
    <tbody></tbody>
  </table>
  <div id="src-empty" style="text-align:center; padding: 40px; opacity: 0.6; display: none;">
    No evidence yet. Run a brief with pipes enabled.
  </div>
</section>
```

- [ ] **Step 3: Add the render + filter + export logic**

Append to the `<script>` block:

```javascript
function renderSourcesTab(doc) {
  const items = doc.evidence || [];
  const q = document.getElementById('src-search').value.toLowerCase();
  const tier = document.getElementById('src-tier').value;
  const agent = document.getElementById('src-agent').value;
  const fresh = document.getElementById('src-fresh').value;

  const filtered = items.filter(it => {
    if (q && !((it.claim || '') + (it.source_title || '')).toLowerCase().includes(q)) return false;
    if (tier && String(it.quality_score) !== tier) return false;
    if (agent && !(it.retrieved_by || []).includes(agent)) return false;
    if (fresh && freshnessBucket(it) !== fresh) return false;
    return true;
  });

  const tbody = document.querySelector('#src-table tbody');
  tbody.innerHTML = '';
  filtered.forEach(it => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td style="padding:4px 8px; font-family: monospace;">${it.id}</td>
      <td style="padding:4px 8px;">${it.claim}</td>
      <td style="padding:4px 8px;"><a href="${it.source_url}" target="_blank">${it.source_title}</a></td>
      <td style="padding:4px 8px;">${'⭐'.repeat(it.quality_score || 0)}</td>
      <td style="padding:4px 8px;">${(it.retrieved_by || []).join(', ')}</td>
      <td style="padding:4px 8px;">${(it.retrieved_at || '').slice(0,10)}</td>
    `;
    tbody.appendChild(tr);
  });
  document.getElementById('src-empty').style.display = filtered.length ? 'none' : 'block';
}

function freshnessBucket(it) {
  // Inline copy of freshness rules — kept in sync with evidence_freshness.py
  const rules = {
    primary_government: [180, 730], primary_company: [90, 365],
    analyst: [365, 1095], reputable_media: [180, 730],
    user_reviews: [30, 180], community: [30, 180], blog: [90, 365],
  };
  const [stale, refetch] = rules[it.source_type] || rules.blog;
  const age = (Date.now() - new Date(it.retrieved_at).getTime()) / 86400000;
  if (age >= refetch) return 'refetch';
  if (age >= stale) return 'stale';
  return 'fresh';
}

// Export handlers
function exportMd(items) {
  let md = '# Sources Appendix\n\n';
  items.forEach(it => {
    md += `- **[${it.id}] ${it.source_title}**\n  - ${it.source_url}\n  - Tier ${it.quality_score}, retrieved ${it.retrieved_at} by ${(it.retrieved_by||[]).join(', ')}\n  - Excerpt: ${it.excerpt}\n\n`;
  });
  downloadBlob(md, 'sources-appendix.md', 'text/markdown');
}
function exportCsv(items) {
  const rows = [['id','claim','source_url','source_title','source_type','quality_score','retrieved_at','retrieved_by']];
  items.forEach(it => rows.push([it.id, it.claim, it.source_url, it.source_title, it.source_type, it.quality_score, it.retrieved_at, (it.retrieved_by||[]).join(';')]));
  const csv = rows.map(r => r.map(c => `"${String(c).replace(/"/g,'""')}"`).join(',')).join('\n');
  downloadBlob(csv, 'sources.csv', 'text/csv');
}
function exportJson(items) {
  downloadBlob(JSON.stringify(items, null, 2), 'sources.json', 'application/json');
}
function downloadBlob(data, name, type) {
  const blob = new Blob([data], { type });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click();
}

// Wire up
['src-search','src-tier','src-agent','src-fresh'].forEach(id => {
  document.getElementById(id).addEventListener('input', () => fetchEvidence().then(d => renderSourcesTab(d || {evidence:[]})));
});
document.getElementById('src-export-md').addEventListener('click', async () => exportMd((await (await fetch('forge-evidence.json')).json()).evidence));
document.getElementById('src-export-csv').addEventListener('click', async () => exportCsv((await (await fetch('forge-evidence.json')).json()).evidence));
document.getElementById('src-export-json').addEventListener('click', async () => exportJson((await (await fetch('forge-evidence.json')).json()).evidence));

// Update fetchEvidence to also render Sources tab when it's visible
async function fetchEvidence() {
  try {
    const res = await fetch('forge-evidence.json', { cache: 'no-store' });
    if (!res.ok) return null;
    const doc = await res.json();
    renderEvidenceBlock(doc);
    if (document.getElementById('tab-sources').style.display !== 'none') {
      renderSourcesTab(doc);
    }
    return doc;
  } catch (e) {
    return null;
  }
}
```

Note: the `fetchEvidence` definition above supersedes the Task 11 version. Replace, don't duplicate.

- [ ] **Step 4: Verify visually**

Refresh dashboard. Click the Sources tab. Expected: empty table with filters, "No evidence yet" message.

- [ ] **Step 5: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add assets/dashboard.html
git commit -m "$(cat <<'EOF'
Dashboard — Sources tab with filters, search, export

New tab 5: dedicated Evidence table.
- Search: free-text against claim + source title
- Filter: tier (1-5), agent (4 evidence agents), freshness bucket
- Export: Markdown, CSV, JSON download via Blob + URL.createObjectURL

Freshness buckets (fresh/stale/refetch) computed in JS from the same
per-source-type rules as tools/evidence_freshness.py — kept in sync
intentionally to avoid a round-trip.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: Pixel office — evidence-dispatch animation variant

**Files:**
- Modify: `assets/office-template.html`

Adds a pulsing `[!]` bubble above each evidence agent's desk while their subagent is dispatched, and a subtle green glow on desk when Evidence arrives. Reads `active_event` from state (set by the skill during dispatch).

- [ ] **Step 1: Open `assets/office-template.html` and find the agent rendering loop**

Search for the function that draws agents (likely a `drawAgent(ctx, agent, state)` or similar). Note where the idle-animation branch selects a frame.

- [ ] **Step 2: Add a new event type**

Find the `active_event` handling. Add a case for `"dispatched"`:

```javascript
// In drawAgent or the active_event switch
if (state.active_event && state.active_event.type === 'dispatched'
    && state.active_event.agents && state.active_event.agents.includes(agent.id)) {
  // Pulsing [!] bubble above agent's desk
  const pulse = (Math.sin(Date.now() / 300) + 1) / 2; // 0..1
  ctx.save();
  ctx.globalAlpha = 0.5 + pulse * 0.5;
  ctx.fillStyle = '#ffcc00';
  ctx.fillRect(agent.x + 4, agent.y - 14, 10, 10);
  ctx.fillStyle = '#000';
  ctx.font = '8px monospace';
  ctx.fillText('!', agent.x + 8, agent.y - 6);
  ctx.restore();
}
```

- [ ] **Step 3: Add the "evidence arrived" glow**

```javascript
// In drawAgent — runs once when event is "evidence_arrived"
if (state.active_event && state.active_event.type === 'evidence_arrived'
    && state.active_event.agents && state.active_event.agents.includes(agent.id)) {
  ctx.save();
  ctx.shadowColor = '#55ff88';
  ctx.shadowBlur = 16;
  // re-draw desk outline so glow emanates from it
  ctx.strokeStyle = '#55ff88';
  ctx.strokeRect(agent.deskX, agent.deskY, agent.deskW, agent.deskH);
  ctx.restore();
}
```

- [ ] **Step 4: Propagate to `assets/office-live.html` if it's a copy**

If `office-live.html` is a generated copy of `office-template.html` (check whether they're identical), re-sync:

```bash
cp assets/office-template.html assets/office-live.html
```

Otherwise apply the same changes in both.

- [ ] **Step 5: Manually test by mutating state**

Temporarily edit `assets/forge-state.json` to add:

```json
"active_event": { "type": "dispatched", "agents": ["agent-vexx", "agent-nyxx", "agent-echo", "agent-taln"] }
```

Refresh the office. Expected: pulsing yellow `[!]` bubbles above the 4 evidence agents. Revert the edit after verification.

- [ ] **Step 6: Verify no regression**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass.

- [ ] **Step 7: Commit**

```bash
git add assets/office-template.html assets/office-live.html
git commit -m "$(cat <<'EOF'
Pixel office — evidence dispatch animation variants

Two new active_event types handled in the render loop:

'dispatched' — pulsing yellow [!] bubble above each agent in
active_event.agents. Sin-wave alpha for the pulse.

'evidence_arrived' — brief green shadow glow around the agent's
desk outline, signaling Evidence has been returned and merged.

SKILL.md will set these events during Phase 2 fan-out and fan-in
respectively.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: End-to-end validation — synthetic brief (Saudi expat neobank)

**Files:**
- Create: `docs/superpowers/runs/2026-04-16-neobank-brief-run.md`

This is not a TDD task — it's a real end-to-end exercise. Run the Forge on the synthetic validation brief from the spec. Capture the output. Compare qualitatively to a v3.0 run. **Second code review gate fires after this task.**

- [ ] **Step 1: Start a fresh session in the Forge repo**

(Separate chat session — do not reuse the implementation-plan session. Fresh Claude Code instance in this repo.)

- [ ] **Step 2: Trigger the skill**

User input:

> "Activate The Forge. Brief: I want to launch a neobank targeting Saudi expats remitting to South Asia. Evaluate market, regulatory, user, and growth angles."

- [ ] **Step 3: Verify the flow**

During the run, watch for:
- All 4 evidence agents scored ≥ 2 on relevance (expected: yes; brief touches market/regulatory/user/growth)
- 4 parallel subagents dispatched via `superpowers:dispatching-parallel-agents`
- Each subagent returns 5-12 Evidence objects
- Fan-in merges dedupe cross-agent URL overlaps
- `forge-evidence.json` grows with a `proj-003` index
- Office renders `dispatched` then `evidence_arrived` events
- Dashboard Evidence block fills in with real metrics
- Deliverable ends with EVIDENCE SUMMARY + Sources Appendix (compact)
- All `[FACT]` tags reference valid Evidence IDs

- [ ] **Step 4: Document the run**

Create `docs/superpowers/runs/2026-04-16-neobank-brief-run.md` with:
- Original brief
- Evidence Summary box (literal copy from the deliverable)
- Sources Appendix (compact form)
- Qualitative notes: what was visibly better vs v3.0? What failed or rough edges?
- Measured metrics: query count, elapsed, cache hit rate, quality avg, conflicts found

- [ ] **Step 5: Verify the forge validates cleanly after the run**

Run: `python3 tools/validator.py`
Expected: `OK` (Evidence ingested correctly)

Run: `python3 tools/validator.py --cache-stats`
Expected: cache has entries from the WebSearch queries

- [ ] **Step 6: Run full test suite**

Run: `python3 -m unittest discover tests -v`
Expected: all tests pass, real-file smoke test green

- [ ] **Step 7: Commit the run document**

```bash
git add docs/superpowers/runs/2026-04-16-neobank-brief-run.md forge-evidence.json
git commit -m "$(cat <<'EOF'
Synthetic validation run — Saudi expat neobank brief

First real end-to-end of Evidence Pipes v1. All 4 evidence agents
dispatched, fan-in clean, Evidence persisted to forge-evidence.json,
Sources Appendix rendered.

See docs/superpowers/runs/2026-04-16-neobank-brief-run.md for the
deliverable, metrics, and qualitative comparison against v3.0.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

### 🛑 FINAL CODE REVIEW GATE

Invoke `superpowers:requesting-code-review` on commits from Task 7 through Task 14 (orchestration → end-to-end). Pass the run-document path as part of the review context so the reviewer sees actual output quality, not just code diffs.

Address Critical + Important findings. Minor noted for follow-up.

---

## Task 15: Address review feedback (placeholder — fill per review output)

**Files:** TBD based on review findings.

Follow TDD ceremony for each fix:
1. Write failing test reproducing the flagged issue
2. Verify RED
3. Minimal fix
4. Verify GREEN
5. Verify no regression
6. Commit with review reference in message

Repeat until all Critical + Important findings are closed.

---

## Task 16: Finish the branch — merge/push per superpowers:finishing-a-development-branch

- [ ] Invoke `superpowers:finishing-a-development-branch`
- [ ] Verify all tests green
- [ ] Present the 4 options (merge locally / push PR / keep / discard)
- [ ] Execute user's choice
- [ ] Announce shipping — Evidence Pipes v1 is live

---

## Self-Review Pass

Spec coverage check (spec section → plan task):

| Spec section | Covered by |
|---|---|
| Evidence object schema | Task 1 |
| Source-type taxonomy (grading) | Task 2 |
| Freshness bands | Task 3 |
| Cache (key, TTL, LRU) | Task 4 |
| Conflict detection + resolution | Task 5 |
| Validator extension + `--cache-stats` | Task 6 |
| Sub-brief generation | Task 7 |
| Fan-in merge + dedup | Task 7 |
| `append_evidence` + `strip_unsupported_claims` | Task 8 |
| Sources Appendix renderer | Task 9 |
| SKILL.md Evidence Pipes section | Task 10 |
| collaboration-protocol v3.1 | Task 10 |
| `evidence_pipes.enabled` flag | Task 10 |
| Dashboard Evidence block | Task 11 |
| Dashboard Sources tab | Task 12 |
| Pixel office animation variants | Task 13 |
| Synthetic validation brief | Task 14 |
| Code review gates | After Task 6, after Task 14 |
| Real validation brief (user-supplied) | Task 14 extension (user decides when to run) |

All spec requirements have a task.

Type-consistency check: `Evidence` dataclass field names match across schema (Task 1), quality (Task 2), freshness (Task 3), cache (Task 4), conflict (Task 5), validator (Task 6), orchestrator (Task 7/8), appendix (Task 9). `retrieved_by` is always `List[str]`. `quality_score` is always `int`. `confidence` is always `float`.

No placeholders except Task 15 which is explicitly "fill per review output" — a known unknown by design.
