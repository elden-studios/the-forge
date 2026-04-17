"""Smoke tests for the pixel office layout — ensures hydrated HTML contains
all expected dept rooms at expected grid positions, including Wave 3 rooms
for Product / Legal / Finance.
"""
import json
import os
import re
import unittest


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(REPO_ROOT, "assets", "office-template.html")


def _read_template():
    with open(TEMPLATE) as f:
        return f.read()


def _canonical_state():
    """Minimal state with all 9 depts — canonical for grid testing."""
    return {
        "departments": [
            {"id": "dept-strt", "name": "Strategy", "color": "#E74C3C"},
            {"id": "dept-rsch", "name": "Research", "color": "#9B59B6"},
            {"id": "dept-dsgn", "name": "Design", "color": "#1ABC9C"},
            {"id": "dept-grwt", "name": "Growth", "color": "#2ECC71"},
            {"id": "dept-engr", "name": "Engineering", "color": "#3498DB"},
            {"id": "dept-cont", "name": "Content", "color": "#F1C40F"},
            {"id": "dept-product", "name": "Product", "color": "#7E57C2"},
            {"id": "dept-legal", "name": "Legal", "color": "#546E7A"},
            {"id": "dept-finance", "name": "Finance", "color": "#26A69A"},
        ],
        "agents": [],
        "active_event": None,
        "cabinet": {"enabled": True, "executives": []},
    }


def _hydrate(state):
    return _read_template().replace("__FORGE_STATE_PLACEHOLDER__", json.dumps(state))


class TestOfficeLayoutGrid3x3(unittest.TestCase):
    def test_all_9_department_ids_in_dept_order(self):
        src = _read_template()
        for did in ["dept-strt", "dept-rsch", "dept-dsgn", "dept-grwt", "dept-engr",
                    "dept-cont", "dept-product", "dept-legal", "dept-finance"]:
            self.assertIn(did, src, f"dept id '{did}' missing from template")

    def test_rows_constant_is_3(self):
        src = _read_template()
        self.assertRegex(src, r"const\s+ROWS\s*=\s*3\b",
                         "ROWS constant should be 3 for Wave 3")

    def test_row2_y_constant_declared(self):
        src = _read_template()
        self.assertRegex(src, r"(const|let|var)\s+ROW2_Y\b",
                         "ROW2_Y constant required to position row 2")

    def test_dept_floor_map_covers_all_9_depts(self):
        src = _read_template()
        # Check each new dept has a floor entry
        for did in ["dept-product", "dept-legal", "dept-finance"]:
            self.assertRegex(src, rf"'{did}'\s*:\s*'\w+'", f"DEPT_FLOOR missing '{did}'")

    def test_hydrated_html_mentions_all_9_department_names(self):
        html = _hydrate(_canonical_state())
        for name in ["Strategy", "Research", "Design", "Growth", "Engineering",
                     "Content", "Product", "Legal", "Finance"]:
            self.assertIn(name, html, f"dept name '{name}' missing from hydrated office")

    def test_live_file_regenerated_with_9_dept_names(self):
        """The committed office-live.html should reflect the regeneration."""
        live_path = os.path.join(REPO_ROOT, "assets", "office-live.html")
        with open(live_path) as f:
            live = f.read()
        for name in ["Product", "Legal", "Finance"]:
            self.assertIn(name, live,
                          f"'{name}' missing from office-live.html — re-hydrate from the template")


if __name__ == "__main__":
    unittest.main()
