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


if __name__ == "__main__":
    unittest.main()
