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


if __name__ == "__main__":
    unittest.main()
