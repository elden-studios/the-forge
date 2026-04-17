"""Smoke tests for the Decisions tab (tab 6) on the dashboard."""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD = os.path.join(REPO_ROOT, "assets", "dashboard.html")


class TestDecisionsTabShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_decisions_tab_button_present(self):
        self.assertRegex(self.src, r'onclick="switchTab\(\'decisions\'\)"', "tab button onclick missing")

    def test_decisions_tab_has_id(self):
        self.assertRegex(self.src, r'id="tab-decisions"', "id=tab-decisions missing")

    def test_decisions_panel_present(self):
        self.assertRegex(self.src, r'id="panel-decisions"', "panel div id=panel-decisions missing")

    def test_switchtab_array_includes_decisions(self):
        self.assertRegex(
            self.src,
            r"\['mc'\s*,\s*'network'\s*,\s*'kanban'\s*,\s*'timeline'\s*,\s*'sources'\s*,\s*'decisions'\]",
            "switchTab tab-name array must be extended with 'decisions'"
        )

    def test_switchtab_handler_for_decisions(self):
        self.assertRegex(self.src, r"id\s*===\s*'decisions'", "switchTab must handle id=='decisions'")

    def test_decisions_table_column_headers(self):
        for col in ["Title", "Decider", "Reversibility", "Status", "Review At", "Project"]:
            self.assertIn(col, self.src, f"table column '{col}' missing")

    def test_render_decisions_tab_function_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+renderDecisionsTab|renderDecisionsTab\s*=\s*function|const\s+renderDecisionsTab\s*=",
            "renderDecisionsTab function missing"
        )

    def test_decisions_table_empty_state(self):
        self.assertRegex(self.src, r"No decisions recorded", "empty-state text missing")

    def test_decisions_table_badges_for_reversibility_and_status(self):
        # Reversibility badge classes
        self.assertRegex(self.src, r"\.badge\.type_1", "reversibility type_1 badge CSS missing")
        self.assertRegex(self.src, r"\.badge\.type_2", "reversibility type_2 badge CSS missing")
        # Status badge classes
        self.assertRegex(self.src, r"\.badge\.status-open", "status-open badge CSS missing")


class TestDecisionsFilters(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_search_input_present(self):
        self.assertRegex(self.src, r'id="dec-search"', "search input id=dec-search missing")

    def test_project_filter_present(self):
        self.assertRegex(self.src, r'id="dec-project"', "project filter id=dec-project missing")

    def test_reversibility_filter_present(self):
        self.assertRegex(self.src, r'id="dec-reversibility"', "reversibility filter id=dec-reversibility missing")

    def test_status_filter_present(self):
        self.assertRegex(self.src, r'id="dec-status"', "status filter id=dec-status missing")

    def test_decider_filter_present(self):
        self.assertRegex(self.src, r'id="dec-decider"', "decider filter id=dec-decider missing")

    def test_filter_options_for_reversibility(self):
        """Reversibility should have type_1 / type_2 option values."""
        self.assertRegex(self.src, r'value="type_1"')
        self.assertRegex(self.src, r'value="type_2"')

    def test_filter_options_for_status(self):
        """Status filter should have open/reviewed/committed/reversed options."""
        for s in ["open", "reviewed", "committed", "reversed"]:
            self.assertRegex(self.src, rf'value="{s}"', f"status option '{s}' missing")

    def test_filter_logic_uses_and_combinator(self):
        """The filter chain should AND across all active filters (find the filter lambda)."""
        # Look for a .filter(d => ...) call inside renderDecisionsTab area
        self.assertRegex(self.src, r"\.filter\(\s*\w+\s*=>", "filter lambda missing")

    def test_filter_rerender_on_input_change(self):
        """Filter inputs should re-trigger renderDecisionsTab on input/change events."""
        # Look for addEventListener wiring to any dec-* input
        self.assertRegex(
            self.src,
            r"(dec-search|dec-project|dec-reversibility|dec-status|dec-decider)['\"]\)(\s*\.\s*|\?\.\s*)?(addEventListener|oninput|onchange)",
            "filter re-render event listener missing"
        )

    def test_project_dropdown_populated_dynamically(self):
        """Project options should be derived from unique project_ids in the doc,
        not hardcoded — look for array-of-unique logic."""
        self.assertRegex(self.src, r"new\s+Set|Array\.from\(new\s+Set", "dynamic project deduplication missing")

    def test_search_is_case_insensitive(self):
        """Search logic should lowercase both sides for case-insensitive match."""
        self.assertRegex(self.src, r"\.toLowerCase\(\)", "toLowerCase missing from search filter")


if __name__ == "__main__":
    unittest.main()
