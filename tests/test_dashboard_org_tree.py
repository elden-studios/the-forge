"""Smoke tests for the Org Tree tab (tab 7) on the dashboard.

Source-text-inspection style, matching the other dashboard tests.
"""
import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DASHBOARD = os.path.join(REPO_ROOT, "assets", "dashboard.html")


class TestOrgTreeTabShell(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_tab_button_present(self):
        self.assertRegex(self.src, r'onclick="switchTab\(\'org-tree\'\)"',
                         "Org Tree tab button onclick missing")

    def test_tab_button_has_id(self):
        self.assertRegex(self.src, r'id="tab-org-tree"', "id=tab-org-tree missing")

    def test_panel_present(self):
        self.assertRegex(self.src, r'id="panel-org-tree"', "panel div id=panel-org-tree missing")

    def test_svg_container_present(self):
        self.assertRegex(self.src, r'id="org-tree-svg"',
                         "svg id=org-tree-svg missing")

    def test_switchtab_array_includes_org_tree(self):
        # Array continues to grow as new tabs ship (e.g. 'tools'); assert the
        # prefix through 'org-tree' is present, trailing entries accepted.
        self.assertRegex(
            self.src,
            r"\['mc'\s*,\s*'network'\s*,\s*'kanban'\s*,\s*'timeline'\s*,\s*'sources'\s*,\s*'decisions'\s*,\s*'org-tree'",
            "switchTab tab-name array must include 'org-tree' (after decisions)"
        )

    def test_switchtab_handler_for_org_tree(self):
        self.assertRegex(self.src, r"id\s*===\s*'org-tree'",
                         "switchTab must handle id=='org-tree'")

    def test_render_org_tree_function_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+renderOrgTree|renderOrgTree\s*=\s*function|const\s+renderOrgTree\s*=",
            "renderOrgTree function missing"
        )

    def test_get_org_tree_js_mirror_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+getOrgTree|getOrgTree\s*=\s*function|const\s+getOrgTree\s*=",
            "getOrgTree JS mirror missing"
        )


class TestOrgTreeCSS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_container_css(self):
        self.assertRegex(self.src, r"\.org-tree-container\s*\{",
                         ".org-tree-container CSS missing")

    def test_node_css(self):
        self.assertRegex(self.src, r"\.org-node\s", ".org-node CSS missing")

    def test_edge_css(self):
        self.assertRegex(self.src, r"\.org-edge\s*\{", ".org-edge CSS missing")

    def test_rivalry_edge_css(self):
        self.assertRegex(self.src, r"\.org-edge\.rivalry\s*\{",
                         ".org-edge.rivalry CSS missing")

    def test_legend_css(self):
        self.assertRegex(self.src, r"\.org-tree-legend\s*\{",
                         ".org-tree-legend CSS missing")


class TestOrgTreeLegend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_legend_text_present(self):
        for label in ("Root (CSO)", "C-Suite", "IC", "Reports to", "Rivalry"):
            self.assertIn(label, self.src, f"legend label '{label}' missing")


class TestOrgTreeLayoutAndEdges(unittest.TestCase):
    """Task 3 — layout algorithm + bezier parent-child edges + rivalry lines."""

    @classmethod
    def setUpClass(cls):
        with open(DASHBOARD) as f:
            cls.src = f.read()

    def test_layout_tree_function_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+layoutTree|layoutTree\s*=\s*function|const\s+layoutTree\s*=",
            "layoutTree helper missing"
        )

    def test_bezier_path_helper_defined(self):
        self.assertRegex(
            self.src,
            r"function\s+bezierPath|bezierPath\s*=\s*function|const\s+bezierPath\s*=",
            "bezierPath helper missing"
        )

    def test_bezier_path_uses_cubic_form(self):
        # A "M ... C ... " cubic Bezier path is what we emit
        self.assertRegex(
            self.src,
            r"`M\s+\$\{[^}]+\}\s+\$\{[^}]+\}\s+C\s+\$\{",
            "bezierPath should emit cubic Bezier (M ... C ...) path string"
        )

    def test_renderer_emits_org_node_groups(self):
        # The SVG node emission uses `<g class="org-node tier-N">`
        self.assertRegex(
            self.src,
            r'<g class="org-node tier-\$\{[^}]+\}"',
            "renderOrgTree should emit <g class='org-node tier-N'> groups"
        )

    def test_renderer_emits_org_edge_paths(self):
        self.assertRegex(
            self.src,
            r'<path class="org-edge"\s+d=',
            "renderOrgTree should emit <path class='org-edge'> for parent-child edges"
        )

    def test_renderer_emits_rivalry_class(self):
        self.assertRegex(
            self.src,
            r'<path class="org-edge rivalry"',
            "renderOrgTree should emit <path class='org-edge rivalry'> for rivalry edges"
        )

    def test_renderer_filters_cross_tier_rivalries(self):
        # Peer-only: skip edges where tiers differ
        self.assertRegex(
            self.src,
            r"na\.tier\s*!==\s*nb\.tier",
            "rivalry edge emission should skip cross-tier pairs"
        )

    def test_dept_strip_in_node(self):
        # 4px colored strip on top of each node
        self.assertRegex(
            self.src,
            r'class="dept-strip"\s+width="160"\s+height="4"',
            "node cards should include a 4px department color strip"
        )


if __name__ == "__main__":
    unittest.main()
