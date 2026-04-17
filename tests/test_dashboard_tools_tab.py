"""Smoke tests for the Tools tab (tab 8) on the dashboard.

Source-text-inspection style, matching the other dashboard tests.
"""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD = os.path.join(REPO_ROOT, "assets", "dashboard.html")


class TestToolsTabShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_tab_button_present(self):
        self.assertRegex(self.src, r'onclick="switchTab\(\'tools\'\)"',
                         "Tools tab button onclick missing")

    def test_tab_button_has_id(self):
        self.assertRegex(self.src, r'id="tab-tools"',
                         "id=tab-tools missing")

    def test_panel_present(self):
        self.assertRegex(self.src, r'id="panel-tools"',
                         "panel div id=panel-tools missing")

    def test_switchtab_array_includes_tools(self):
        # Array continues to grow; assert prefix through 'tools'
        self.assertRegex(
            self.src,
            r"\['mc'\s*,\s*'network'\s*,\s*'kanban'\s*,\s*'timeline'\s*,\s*'sources'\s*,\s*'decisions'\s*,\s*'org-tree'\s*,\s*'tools'",
            "switchTab tab-name array must include 'tools' after 'org-tree'"
        )

    def test_switchtab_handler_for_tools(self):
        self.assertRegex(self.src, r"id\s*===\s*'tools'",
                         "switchTab must handle id=='tools'")


class TestToolsSummaryRow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_summary_row_container(self):
        self.assertRegex(self.src, r'class="tools-summary-row"',
                         "tools-summary-row container missing")

    def test_active_count_card(self):
        self.assertRegex(self.src, r'id="tools-active-count"',
                         "tools-active-count element missing")

    def test_total_cost_card(self):
        self.assertRegex(self.src, r'id="tools-total-cost"',
                         "tools-total-cost element missing")

    def test_dormant_cost_card(self):
        self.assertRegex(self.src, r'id="tools-dormant-cost"',
                         "tools-dormant-cost element missing")

    def test_redundancy_count_card(self):
        self.assertRegex(self.src, r'id="tools-redundancy-count"',
                         "tools-redundancy-count element missing")

    def test_summary_card_warning_class(self):
        # The Dormant Waste card carries the .warning modifier
        self.assertRegex(self.src, r'class="summary-card warning"',
                         ".summary-card.warning missing (for Dormant Waste)")


class TestToolsSections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_recommendations_section_container(self):
        self.assertRegex(self.src, r'id="tools-recommendations"',
                         "tools-recommendations container missing")

    def test_by_category_container(self):
        self.assertRegex(self.src, r'id="tools-by-category"',
                         "tools-by-category container missing")

    def test_by_agent_container(self):
        self.assertRegex(self.src, r'id="tools-by-agent"',
                         "tools-by-agent container missing")


class TestToolsJSMirrors(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_render_tools_tab_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+renderToolsTab|renderToolsTab\s*=\s*function|const\s+renderToolsTab\s*=",
            "renderToolsTab function missing"
        )

    def test_fetch_platforms_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+fetchPlatforms|fetchPlatforms\s*=\s*function|const\s+fetchPlatforms\s*=",
            "fetchPlatforms function missing"
        )

    def test_get_cost_breakdown_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+getCostBreakdown|getCostBreakdown\s*=\s*function|const\s+getCostBreakdown\s*=",
            "getCostBreakdown JS mirror missing"
        )

    def test_get_gap_analysis_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+getGapAnalysis|getGapAnalysis\s*=\s*function|const\s+getGapAnalysis\s*=",
            "getGapAnalysis JS mirror missing"
        )

    def test_get_redundancies_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+getRedundancies|getRedundancies\s*=\s*function|const\s+getRedundancies\s*=",
            "getRedundancies JS mirror missing"
        )

    def test_get_tools_by_agent_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+getToolsByAgent|getToolsByAgent\s*=\s*function|const\s+getToolsByAgent\s*=",
            "getToolsByAgent JS mirror missing"
        )


class TestToolsCSS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_tools_summary_row_css(self):
        self.assertRegex(self.src, r"\.tools-summary-row\s*\{",
                         ".tools-summary-row CSS missing")

    def test_summary_card_css(self):
        self.assertRegex(self.src, r"\.summary-card\s*\{",
                         ".summary-card CSS missing")

    def test_tools_section_css(self):
        self.assertRegex(self.src, r"\.tools-section\s*\{",
                         ".tools-section CSS missing")


if __name__ == "__main__":
    unittest.main()
