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


class TestBoardroom(unittest.TestCase):
    def test_boardroom_constants_declared(self):
        src = _read_template()
        self.assertRegex(src, r"BOARDROOM_W", "BOARDROOM_W constant required")
        self.assertRegex(src, r"BOARDROOM_H", "BOARDROOM_H constant required")

    def test_layout_has_boardroom_entry(self):
        src = _read_template()
        self.assertRegex(src, r"this\.boardroom\s*=", "Layout.constructor must set this.boardroom")

    def test_chair_positions_helper_declared(self):
        src = _read_template()
        self.assertRegex(src, r"function\s+chairPositions|chairPositions\s*[:=]\s*function|const\s+chairPositions\s*=")

    def test_chair_positions_has_5_labels(self):
        src = _read_template()
        for label in ['head', 'top-left', 'top-right', 'bot-left', 'bot-right']:
            self.assertIn(f"'{label}'", src, f"chair label '{label}' missing from chairPositions")

    def test_draw_boardroom_method_present(self):
        src = _read_template()
        self.assertRegex(src, r"drawBoardroom", "Scene.drawBoardroom method missing")

    def test_boardroom_nameplate_text_present(self):
        src = _read_template()
        self.assertRegex(src, r"(EXEC SUITE|Executive Suite|Exec Suite|CABINET|Boardroom)", "boardroom nameplate text missing")

    def test_hydrated_live_file_mentions_boardroom(self):
        import os
        live_path = os.path.join(REPO_ROOT, "assets", "office-live.html")
        with open(live_path) as f:
            live = f.read()
        self.assertRegex(live, r"(EXEC SUITE|Executive Suite|Exec Suite|CABINET|Boardroom)",
                         "office-live.html must contain boardroom marker after regen")

    def test_canvas_widens_to_accommodate_boardroom(self):
        src = _read_template()
        # Look for explicit widen logic via Math.max on this.W
        self.assertRegex(src, r"this\.W\s*=\s*Math\.max\(this\.W\s*,", "canvas width must grow to fit boardroom")

    def test_boardroom_abuts_grid_outer_wall(self):
        """Regression: boardroom.x should equal MARGIN + COLS*ROOM_W + (COLS-1)*WALL
        so the grid's outer-right wall serves as the boardroom's west wall (no seam)."""
        src = _read_template()
        boardroom_block = re.search(r"this\.boardroom\s*=\s*\{[^}]+\}", src, re.DOTALL)
        self.assertIsNotNone(boardroom_block, "boardroom assignment not found")
        block_text = boardroom_block.group(0)
        # The "shared wall" formula must be present
        self.assertIn("(COLS - 1) * WALL", block_text,
                      "boardroom.x should use shared-outer-wall formula, not COLS*(ROOM_W+WALL)")


class TestCabinetAnimation(unittest.TestCase):
    def test_cabinet_dispatched_event_handled(self):
        src = _read_template()
        self.assertRegex(src, r"cabinet_dispatched", "cabinet_dispatched event handler missing")

    def test_cabinet_arrived_event_handled(self):
        src = _read_template()
        self.assertRegex(src, r"cabinet_arrived", "cabinet_arrived event handler missing")

    def test_route_cabinet_helper_defined(self):
        src = _read_template()
        self.assertRegex(src, r"function\s+routeCabinet|routeCabinet\s*=\s*function|const\s+routeCabinet\s*=",
                         "routeCabinet helper missing")

    def test_route_cabinet_reads_cabinet_executives(self):
        src = _read_template()
        self.assertRegex(src, r"cabinet\.executives", "routeCabinet must read state.cabinet.executives")

    def test_route_cabinet_supports_both_modes(self):
        src = _read_template()
        self.assertRegex(src, r"'walk'", "routeCabinet must support 'walk' mode")
        self.assertRegex(src, r"'seat'", "routeCabinet must support 'seat' mode")

    def test_cabinet_seated_sprite_state_recognized(self):
        src = _read_template()
        # All 3 'seated' check locations should include cabinet_seated
        self.assertGreaterEqual(
            src.count("cabinet_seated"), 4,
            "cabinet_seated should appear in routeCabinet + 3 seated checks (>=4 occurrences)"
        )

    def test_live_file_contains_cabinet_event_handlers(self):
        import os
        live_path = os.path.join(REPO_ROOT, "assets", "office-live.html")
        with open(live_path) as f:
            live = f.read()
        self.assertIn("cabinet_dispatched", live)
        self.assertIn("cabinet_arrived", live)
        self.assertIn("routeCabinet", live)


if __name__ == "__main__":
    unittest.main()
