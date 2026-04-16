"""Tests for The Forge state validator."""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

# Add tools/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))

from validator import (  # noqa: E402
    main,
    validate_brain_files,
    validate_project,
    validate_state,
    validate_tasks,
)


class TestValidateState(unittest.TestCase):
    """validate_state(state) -> (ok: bool, errors: list[str])"""

    def test_returns_ok_for_minimal_valid_state(self):
        """An empty but structurally valid state should pass validation."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [],
            "agents": [],
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, f"Expected valid, got errors: {errors}")
        self.assertEqual(errors, [])

    def test_agent_references_nonexistent_department_fails(self):
        """An agent whose department_id doesn't match any department must fail."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [
                {"id": "dept-real", "name": "Real", "color": "#000000"}
            ],
            "agents": [
                {
                    "id": "agent-bad",
                    "name": "Bad",
                    "department_id": "dept-missing",
                    "status": "active",
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("dept-missing" in e for e in errors),
            f"Expected error mentioning 'dept-missing', got: {errors}",
        )


    def test_handoff_to_nonexistent_agent_fails(self):
        """An agent's collaboration_links pointing to a non-existent agent must fail."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-one",
                    "name": "One",
                    "department_id": "dept-a",
                    "status": "active",
                    "collaboration_links": {
                        "hands_off_to": ["agent-ghost"],
                        "requests_input_from": [],
                        "debates_with": [],
                    },
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("agent-ghost" in e for e in errors),
            f"Expected error about agent-ghost, got: {errors}",
        )


    def test_duplicate_hairstyle_among_active_agents_fails(self):
        """Two active agents must not share the same hairstyle."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-one",
                    "name": "One",
                    "department_id": "dept-a",
                    "status": "active",
                    "avatar": {"hairstyle": "spiky"},
                },
                {
                    "id": "agent-two",
                    "name": "Two",
                    "department_id": "dept-a",
                    "status": "active",
                    "avatar": {"hairstyle": "spiky"},
                },
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("spiky" in e.lower() or "hairstyle" in e.lower() for e in errors),
            f"Expected hairstyle duplicate error, got: {errors}",
        )

    def test_inactive_agents_can_share_hairstyle(self):
        """Inactive (fired) agents don't trigger uniqueness checks."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-one",
                    "name": "One",
                    "department_id": "dept-a",
                    "status": "active",
                    "avatar": {"hairstyle": "spiky"},
                },
                {
                    "id": "agent-two",
                    "name": "Two",
                    "department_id": "dept-a",
                    "status": "inactive",
                    "avatar": {"hairstyle": "spiky"},
                },
            ],
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, f"Inactive duplicate should pass, got: {errors}")


    def test_duplicate_idle_animation_among_active_agents_fails(self):
        """Idle animations must be unique across active agents."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-one",
                    "name": "One",
                    "department_id": "dept-a",
                    "status": "active",
                    "avatar": {"hairstyle": "spiky", "idle_animation": "sips-mug"},
                },
                {
                    "id": "agent-two",
                    "name": "Two",
                    "department_id": "dept-a",
                    "status": "active",
                    "avatar": {"hairstyle": "bob", "idle_animation": "sips-mug"},
                },
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("sips-mug" in e or "idle_animation" in e.lower() for e in errors),
            f"Expected idle_animation duplicate error, got: {errors}",
        )


class TestValidateBrainFiles(unittest.TestCase):
    """validate_brain_files(state, brains_dir) -> (ok, errors)"""

    def test_missing_brain_file_for_active_agent_fails(self):
        """An active agent without a brain file should fail validation."""
        state = {
            "agents": [
                {"id": "agent-one", "name": "One", "status": "active"},
                {"id": "agent-two", "name": "Two", "status": "active"},
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            # Only create one brain file
            with open(os.path.join(tmp, "one-brain.md"), "w") as f:
                f.write("# One")
            ok, errors = validate_brain_files(state, tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("two-brain.md" in e.lower() or "Two" in e for e in errors),
                f"Expected missing brain file error for Two, got: {errors}",
            )

    def test_all_brain_files_present_passes(self):
        state = {
            "agents": [
                {"id": "agent-one", "name": "One", "status": "active"},
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "one-brain.md"), "w") as f:
                f.write("# One")
            ok, errors = validate_brain_files(state, tmp)
            self.assertTrue(ok, f"Expected pass, got: {errors}")

    def test_inactive_agents_dont_require_brain_file(self):
        state = {
            "agents": [
                {"id": "agent-gone", "name": "Gone", "status": "inactive"},
            ]
        }
        with tempfile.TemporaryDirectory() as tmp:
            ok, errors = validate_brain_files(state, tmp)
            self.assertTrue(ok, f"Inactive should not require brain file, got: {errors}")


class TestValidateTasks(unittest.TestCase):
    """validate_tasks(tasks, state) -> (ok, errors)"""

    def test_empty_tasks_file_passes(self):
        tasks = {"tasks": [], "handoffs": [], "current_phase": 0}
        state = {"agents": []}
        ok, errors = validate_tasks(tasks, state)
        self.assertTrue(ok, f"Expected pass, got: {errors}")

    def test_task_referencing_unknown_agent_fails(self):
        tasks = {
            "tasks": [
                {"id": "t1", "agent": "agent-ghost", "status": "in_progress"},
            ],
            "handoffs": [],
        }
        state = {"agents": [{"id": "agent-real", "name": "Real", "status": "active"}]}
        ok, errors = validate_tasks(tasks, state)
        self.assertFalse(ok)
        self.assertTrue(
            any("agent-ghost" in e for e in errors),
            f"Expected error about agent-ghost, got: {errors}",
        )

    def test_handoff_referencing_unknown_agent_fails(self):
        tasks = {
            "tasks": [],
            "handoffs": [
                {"from": "agent-real", "to": "agent-ghost", "status": "pending"}
            ],
        }
        state = {"agents": [{"id": "agent-real", "name": "Real", "status": "active"}]}
        ok, errors = validate_tasks(tasks, state)
        self.assertFalse(ok)
        self.assertTrue(
            any("agent-ghost" in e for e in errors),
            f"Expected handoff error about agent-ghost, got: {errors}",
        )

    def test_invalid_phase_number_fails(self):
        """current_phase must be 0-8 (0 = no active project, 1-8 = phases)."""
        tasks = {"tasks": [], "handoffs": [], "current_phase": 99}
        state = {"agents": []}
        ok, errors = validate_tasks(tasks, state)
        self.assertFalse(ok)
        self.assertTrue(
            any("phase" in e.lower() for e in errors),
            f"Expected phase error, got: {errors}",
        )


class TestValidateProject(unittest.TestCase):
    """validate_project(project_dir) -> (ok, errors)

    Loads forge-state.json, forge-tasks.json, and references/brains/ from the
    project dir and runs all validators.
    """

    def test_validates_project_with_all_files_ok(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                json.dump(
                    {
                        "company": {"name": "T", "founded": "2026-01-01"},
                        "departments": [],
                        "agents": [],
                    },
                    f,
                )
            with open(os.path.join(tmp, "forge-tasks.json"), "w") as f:
                json.dump(
                    {"tasks": [], "handoffs": [], "current_phase": 0}, f
                )
            os.makedirs(os.path.join(tmp, "references", "brains"))
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, f"Expected pass, got: {errors}")

    def test_detects_missing_forge_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("forge-state.json" in e for e in errors),
                f"Expected missing-file error, got: {errors}",
            )


class TestMain(unittest.TestCase):
    """main(argv) -> int (exit code)

    CLI entry point. Exit 0 on success, 1 on validation errors, 2 on usage errors.
    """

    def test_main_returns_zero_on_valid_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                json.dump(
                    {
                        "company": {"name": "T", "founded": "2026-01-01"},
                        "departments": [],
                        "agents": [],
                    },
                    f,
                )
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([tmp])
            self.assertEqual(rc, 0)
            self.assertIn("OK", buf.getvalue())

    def test_main_returns_one_and_prints_errors_on_invalid_project(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Missing forge-state.json triggers an error
            buf = io.StringIO()
            with redirect_stdout(buf):
                rc = main([tmp])
            self.assertEqual(rc, 1)
            self.assertIn("forge-state.json", buf.getvalue())

    def test_main_defaults_to_cwd_when_no_arg(self):
        """main() with no args should validate the current working directory."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                json.dump(
                    {
                        "company": {"name": "T", "founded": "2026-01-01"},
                        "departments": [],
                        "agents": [],
                    },
                    f,
                )
            try:
                os.chdir(tmp)
                buf = io.StringIO()
                with redirect_stdout(buf):
                    rc = main([])
                self.assertEqual(rc, 0)
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
