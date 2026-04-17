"""Smoke tests for the Cabinet block on the Mission Control tab."""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD = os.path.join(REPO_ROOT, "assets", "dashboard.html")


class TestCabinetBlockPresence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_cabinet_block_css_class_defined(self):
        self.assertRegex(self.src, r"\.cabinet-block\s*\{", "CSS class .cabinet-block missing")

    def test_cabinet_block_dom_element_present(self):
        self.assertRegex(self.src, r'id="cabinet-block"', "DOM element id=cabinet-block missing")

    def test_cabinet_empty_state_defined(self):
        self.assertRegex(self.src, r'id="cabinet-empty"', "empty-state container missing")

    def test_render_cabinet_block_function_defined(self):
        self.assertRegex(self.src, r"function\s+renderCabinetBlock|renderCabinetBlock\s*=\s*function|const\s+renderCabinetBlock\s*=")

    def test_fetch_decisions_function_defined(self):
        self.assertRegex(self.src, r"function\s+fetchDecisions|fetchDecisions\s*=\s*function|const\s+fetchDecisions\s*=")

    def test_forge_decisions_fetch_url(self):
        self.assertRegex(self.src, r"forge-decisions\.json", "forge-decisions.json fetch URL missing")

    def test_five_lens_keys_referenced(self):
        for lens in ["strategic_kernel", "product_shape", "build_class", "economic_shape", "market_bet"]:
            self.assertIn(lens, self.src, f"lens key '{lens}' not referenced")

    def test_pre_mortem_data_accessed(self):
        self.assertRegex(self.src, r"pre_mortem", "pre_mortem state key not accessed")

    def test_empty_state_text_graceful(self):
        self.assertRegex(self.src, r"(Cabinet Framing hasn't run|no cabinet|cabinet-empty|Cabinet Framing pending|Cabinet hasn't)",
                         "graceful empty state text missing")

    def test_escape_helper_used_for_text_interpolation(self):
        """All user-controlled strings should be HTML-escaped before interpolation
        to prevent XSS — enforce via presence of an esc() helper."""
        self.assertRegex(self.src, r"function\s+esc\s*\(|const\s+esc\s*=", "esc() helper missing for safe interpolation")


class TestPreMortemHeatmap(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_heatmap_css_class_defined(self):
        self.assertRegex(self.src, r"\.heatmap\s*\{|\.heatmap-cell\s*\{|\.heatmap-grid\s*\{",
                         "heatmap CSS class missing")

    def test_heatmap_dom_element_present(self):
        self.assertRegex(self.src, r'id="cabinet-heatmap"', "heatmap DOM container missing")

    def test_heatmap_axis_labels_present(self):
        self.assertRegex(self.src, r"Likelihood", "Likelihood axis label missing")
        self.assertRegex(self.src, r"Impact", "Impact axis label missing")

    def test_heatmap_is_5x5_grid(self):
        self.assertRegex(self.src, r"repeat\(5", "5-column grid template missing")

    def test_heatmap_buckets_js_mirror_defined(self):
        self.assertRegex(self.src, r"function\s+heatmapBuckets|heatmapBuckets\s*=\s*function|const\s+heatmapBuckets\s*=",
                         "heatmapBuckets JS function missing")

    def test_render_heatmap_function_defined(self):
        self.assertRegex(self.src, r"function\s+renderHeatmap|renderHeatmap\s*=\s*function|const\s+renderHeatmap\s*=",
                         "renderHeatmap function missing")

    def test_heatmap_renders_from_cabinet_block(self):
        """renderCabinetBlock should call renderHeatmap (or invoke it inline)."""
        self.assertIn("renderHeatmap", self.src, "renderHeatmap must be called somewhere")

    def test_heatmap_number_is_integer_check(self):
        """JS mirror of Python's isinstance(x, int) check — must use Number.isInteger or similar."""
        self.assertRegex(self.src, r"Number\.isInteger|typeof\s+\w+\s*===\s*['\"]number['\"]",
                         "numeric type check missing in heatmapBuckets")


class TestVerdictFilterIncludesCommitted(unittest.TestCase):
    """C2 regression: verdict filter must include committed/reviewed decisions,
    only excluding reversed ones. Previously filtered on status==='open' only,
    causing the Verdict pane to evaporate when the Cabinet closed a decision."""

    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_verdict_filter_excludes_only_reversed(self):
        self.assertRegex(
            self.src,
            r"status\s*!==\s*['\"]reversed['\"]",
            "verdict filter must exclude status==='reversed' (not status==='open' only)"
        )

    def test_verdict_does_not_exclude_committed_status(self):
        """Make sure we don't see `status === 'open'` as the sole status filter in the verdict selection."""
        # A negative test — the old buggy pattern should not be present for verdict selection
        # Search for renderCabinetBlock function body and look for the filter
        self.assertNotRegex(
            self.src,
            r"currentProject\s*&&\s*d\.status\s*===\s*['\"]open['\"]",
            "buggy verdict filter `status === 'open'` must not remain in renderCabinetBlock"
        )


if __name__ == "__main__":
    unittest.main()
