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


    def test_routing_override_referencing_unknown_agent_fails(self):
        """routing_overrides[*].lead_agent must reference an existing agent."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-real",
                    "name": "Real",
                    "department_id": "dept-a",
                    "status": "active",
                }
            ],
            "routing_overrides": {
                "saudi_lead": {
                    "trigger_keywords": ["saudi"],
                    "lead_agent": "agent-ghost",
                    "description": "Broken",
                }
            },
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("agent-ghost" in e for e in errors),
            f"Expected routing_overrides error about agent-ghost, got: {errors}",
        )

    def test_routing_override_with_valid_agent_passes(self):
        """routing_overrides pointing to a real agent should pass."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-real",
                    "name": "Real",
                    "department_id": "dept-a",
                    "status": "active",
                }
            ],
            "routing_overrides": {
                "saudi_lead": {"lead_agent": "agent-real"}
            },
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, f"Valid routing override should pass, got: {errors}")

    def test_project_history_agents_involved_referencing_unknown_agent_fails(self):
        """project_history[*].agents_involved must reference existing agents."""
        state = {
            "company": {"name": "Test", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-real",
                    "name": "Real",
                    "department_id": "dept-a",
                    "status": "active",
                }
            ],
            "project_history": [
                {
                    "id": "proj-001",
                    "title": "Old project",
                    "date": "2026-01-01",
                    "agents_involved": ["agent-real", "agent-ghost"],
                    "outcome": "...",
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("agent-ghost" in e for e in errors),
            f"Expected project_history error about agent-ghost, got: {errors}",
        )

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

    def test_invalid_role_value_fails(self):
        """role must be 'executive' or 'ic' if present."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-bad",
                    "name": "Bad",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "manager",
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("role" in e.lower() and "manager" in e for e in errors),
            f"Expected role enum error, got: {errors}",
        )

    def test_role_absent_is_ok(self):
        """role field is optional during v3.1 -> v3.2 migration."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-legacy",
                    "name": "Legacy",
                    "department_id": "dept-a",
                    "status": "active",
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, f"Absent role should pass, got: {errors}")

    def test_reports_to_nonexistent_agent_fails(self):
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-ic",
                    "name": "IC",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "ic",
                    "reports_to": "agent-ghost",
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("reports_to" in e and "agent-ghost" in e for e in errors),
            f"Expected reports_to error, got: {errors}",
        )

    def test_ic_must_report_to_executive(self):
        """reports_to must reference a role:executive agent when the reporter is role:ic."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-exec",
                    "name": "Exec",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "ic",
                },
                {
                    "id": "agent-ic",
                    "name": "IC",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "ic",
                    "reports_to": "agent-exec",
                },
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("reports_to" in e and "executive" in e.lower() for e in errors),
            f"Expected 'must report to executive' error, got: {errors}",
        )

    def test_executive_reports_to_another_executive_is_ok(self):
        """Executives CAN reports_to another executive (for CSO-under-CEO-style)."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-cso",
                    "name": "CSO",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "executive",
                },
                {
                    "id": "agent-cpo",
                    "name": "CPO",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "executive",
                    "reports_to": "agent-cso",
                },
            ],
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, f"Exec-to-exec reports_to should pass, got: {errors}")

    def test_cabinet_executives_must_exist(self):
        """Every id in cabinet.executives must be an existing agent."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-real",
                    "name": "Real",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "executive",
                }
            ],
            "cabinet": {"executives": ["agent-real", "agent-ghost"]},
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("cabinet" in e and "agent-ghost" in e for e in errors),
            f"Expected cabinet executive error, got: {errors}",
        )

    def test_cabinet_executives_must_have_role_executive(self):
        """Every id in cabinet.executives must have role='executive'."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-notexec",
                    "name": "NotExec",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "ic",
                }
            ],
            "cabinet": {"executives": ["agent-notexec"]},
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("cabinet" in e.lower() and "role" in e.lower() for e in errors),
            f"Expected role error for cabinet member, got: {errors}",
        )

    def test_cabinet_block_absent_is_ok(self):
        """cabinet block is optional during v3.1 -> v3.2 migration."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [],
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, f"No cabinet block should pass, got: {errors}")

    def test_cabinet_block_non_dict_fails_cleanly(self):
        """cabinet must be a dict, not a string or list."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [],
            "agents": [],
            "cabinet": "agent-flnt",
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("cabinet" in e.lower() and "dict" in e.lower() for e in errors),
            f"Expected 'cabinet must be a dict' error, got: {errors}",
        )

    def test_cabinet_executives_null_fails_cleanly(self):
        """cabinet.executives: null must not crash — readable error."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [],
            "agents": [],
            "cabinet": {"executives": None},
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("executives" in e.lower() and "list" in e.lower() for e in errors),
            f"Expected 'executives must be a list' error, got: {errors}",
        )

    def test_cabinet_executives_non_list_fails_cleanly(self):
        """cabinet.executives as a string must not crash."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [],
            "agents": [],
            "cabinet": {"executives": "agent-flnt"},
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("executives" in e.lower() and "list" in e.lower() for e in errors),
            f"Expected 'executives must be a list' error, got: {errors}",
        )

    def test_reports_to_non_scalar_fails_cleanly(self):
        """reports_to must be a string (agent id) or null, not a list or dict."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-a",
                    "name": "A",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "ic",
                    "reports_to": ["agent-b"],  # Bad: list instead of string
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("reports_to" in e and "string" in e.lower() for e in errors),
            f"Expected 'reports_to must be a string' error, got: {errors}",
        )

    def test_agent_reports_to_self_fails(self):
        """An agent cannot report to themselves."""
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [
                {
                    "id": "agent-narcissus",
                    "name": "Narcissus",
                    "department_id": "dept-a",
                    "status": "active",
                    "role": "executive",
                    "reports_to": "agent-narcissus",
                }
            ],
        }
        ok, errors = validate_state(state)
        self.assertFalse(ok)
        self.assertTrue(
            any("reports_to" in e and ("itself" in e.lower() or "self" in e.lower()) for e in errors),
            f"Expected 'cannot report to self' error, got: {errors}",
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

    def test_task_handoff_field_referencing_unknown_agent_fails(self):
        """Per-task handoff_from/handoff_to fields must reference existing agents."""
        tasks = {
            "tasks": [
                {
                    "id": "t1",
                    "agent": "agent-real",
                    "status": "done",
                    "handoff_from": "agent-ghost",
                    "handoff_to": "agent-phantom",
                }
            ],
            "handoffs": [],
        }
        state = {"agents": [{"id": "agent-real", "name": "Real", "status": "active"}]}
        ok, errors = validate_tasks(tasks, state)
        self.assertFalse(ok)
        self.assertTrue(
            any("agent-ghost" in e for e in errors),
            f"Expected handoff_from error about agent-ghost, got: {errors}",
        )
        self.assertTrue(
            any("agent-phantom" in e for e in errors),
            f"Expected handoff_to error about agent-phantom, got: {errors}",
        )

    def test_task_null_handoff_fields_are_ok(self):
        """null handoff_from/handoff_to should not trigger errors — means no handoff."""
        tasks = {
            "tasks": [
                {
                    "id": "t1",
                    "agent": "agent-real",
                    "status": "in_progress",
                    "handoff_from": None,
                    "handoff_to": None,
                }
            ],
            "handoffs": [],
        }
        state = {"agents": [{"id": "agent-real", "name": "Real", "status": "active"}]}
        ok, errors = validate_tasks(tasks, state)
        self.assertTrue(ok, f"Null handoff fields should pass, got: {errors}")

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

    def test_malformed_forge_state_json_reports_error_cleanly(self):
        """Malformed JSON in forge-state.json should produce a readable error, not a traceback."""
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                f.write("{ not valid json ]")
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("forge-state.json" in e and "json" in e.lower() for e in errors),
                f"Expected JSON parse error mentioning forge-state.json, got: {errors}",
            )

    def test_malformed_forge_tasks_json_reports_error_cleanly(self):
        """Malformed forge-tasks.json should produce a readable error, not a traceback."""
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
                f.write("{ still not json ]")
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("forge-tasks.json" in e and "json" in e.lower() for e in errors),
                f"Expected JSON parse error mentioning forge-tasks.json, got: {errors}",
            )

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


class TestRealProjectSmoke(unittest.TestCase):
    """Smoke test: the shipped Forge project files must validate cleanly.

    This test detects drift between the validator and the canonical state
    files in the repo. If someone edits forge-state.json or forge-tasks.json
    and introduces a typo, this test catches it in CI.
    """

    def test_real_project_validates_cleanly(self):
        project_root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        # Skip gracefully if the state file isn't here (so this test file
        # remains runnable in isolation)
        if not os.path.isfile(os.path.join(project_root, "forge-state.json")):
            self.skipTest("No forge-state.json in repo root — not a Forge checkout")
        ok, errors = validate_project(project_root)
        self.assertTrue(
            ok,
            f"Real Forge project has integrity errors:\n"
            + "\n".join(f"  - {e}" for e in errors),
        )


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
            "id": "ev-abc12345", "claim": "c", "source_url": "https://a.com",
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
        doc = self._doc(evidence=[self._ev(id="ev-dup12345"), self._ev(id="ev-dup12345")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("ev-dup12345" in e and "duplicate" in e.lower() for e in errors), errors)

    def test_retrieved_by_must_be_a_list(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(retrieved_by="agent-vexx")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        # Must produce ONE clear error, not N char-by-char errors
        rb_errors = [e for e in errors if "retrieved_by" in e]
        self.assertEqual(len(rb_errors), 1, f"expected one error, got: {rb_errors}")
        self.assertIn("list", rb_errors[0].lower())

    def test_retrieved_by_none_produces_clear_error(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(retrieved_by=None)])
        ok, errors = validate_evidence(doc, self._state())
        # None is acceptable — treated as empty (no agents attributed yet)
        # OR produces exactly one clear error. Pin the current contract.
        # Current code does `it.get("retrieved_by", []) or []` so None → empty → OK.
        self.assertTrue(ok, f"None retrieved_by should be treated as empty, got: {errors}")

    def test_missing_id_produces_clear_error(self):
        from validator import validate_evidence
        # Construct evidence dict without the 'id' key
        ev = self._ev()
        ev.pop("id", None)
        doc = self._doc(evidence=[ev])
        ok, errors = validate_evidence(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(
            any("missing" in e.lower() and "id" in e.lower() for e in errors),
            f"expected clear 'missing id' error, got: {errors}",
        )

    def test_retrieved_at_with_fractional_seconds_is_accepted(self):
        from validator import validate_evidence
        doc = self._doc(evidence=[self._ev(retrieved_at="2026-04-16T14:32:00.123Z")])
        ok, errors = validate_evidence(doc, self._state())
        self.assertTrue(ok, f"fractional seconds should be accepted, got: {errors}")

    def test_validate_project_validates_populated_evidence(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "forge-state.json"), "w") as f:
                json.dump({
                    "company": {"name": "T", "founded": "2026-01-01"},
                    "departments": [],
                    "agents": [{"id": "agent-vexx", "name": "Vex", "status": "active"}],
                }, f)
            with open(os.path.join(tmp, "forge-evidence.json"), "w") as f:
                json.dump({
                    "evidence": [self._ev()],
                    "project_evidence_index": {"proj-001": ["ev-abc12345"]},
                }, f)
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, errors)

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
            with open(os.path.join(tmp, "assets", ".forge-cache", "abc.json"), "w") as f:
                f.write('{"key":"abc","query":"q","results":[],"fetched_at":"2026-04-16T00:00:00Z","hits":0}')
            with redirect_stdout(buf):
                rc = main(["--cache-stats", tmp])
            self.assertEqual(rc, 0)
            output = buf.getvalue()
            self.assertIn("entries", output.lower())
            # Pin the actual count so a broken cache_stats() that always
            # prints "0 entries" doesn't silently pass this test.
            self.assertIn("1 entries", output)


class TestCabinetEnabledKillSwitch(unittest.TestCase):
    """cabinet.enabled: false is the canonical v3.2 kill switch.
    cabinet.executives: [] is accepted as an alias for backward compat.
    Both coexist with the existing 'executives list references executives' rule."""

    def test_cabinet_enabled_false_passes(self):
        """cabinet.enabled: false is the canonical kill switch."""
        from validator import validate_state
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [],
            "agents": [],
            "cabinet": {"enabled": False},
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, errors)

    def test_cabinet_enabled_true_with_populated_executives_passes(self):
        """When enabled and executives are listed, they still must be real agents."""
        from validator import validate_state
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [{"id": "dept-a", "name": "A", "color": "#000"}],
            "agents": [{
                "id": "agent-real",
                "name": "Real",
                "department_id": "dept-a",
                "status": "active",
                "role": "executive"
            }],
            "cabinet": {"enabled": True, "executives": ["agent-real"]},
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, errors)

    def test_cabinet_executives_empty_list_alias_passes(self):
        """cabinet.executives: [] (Wave 1 kill switch) still works as alias."""
        from validator import validate_state
        state = {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [],
            "agents": [],
            "cabinet": {"executives": []},
        }
        ok, errors = validate_state(state)
        self.assertTrue(ok, errors)


class TestStandingRule11(unittest.TestCase):
    """Every Cabinet Verdict (cabinet_framing present) must have at least one
    Decision Log entry for the current project."""

    def _write(self, tmp, fname, obj):
        with open(os.path.join(tmp, fname), "w") as f:
            json.dump(obj, f)

    def _state(self):
        return {
            "company": {"name": "T", "founded": "2026-01-01"},
            "departments": [],
            "agents": [{"id": "agent-flnt", "name": "Flint", "status": "active"}],
        }

    def _tasks_with_cabinet(self, project_id):
        return {
            "current_project": project_id,
            "tasks": [],
            "handoffs": [],
            "current_phase": 1,
            "cabinet_framing": {
                "framing_brief": "x",
                "lenses": {
                    "strategic_kernel": "x", "product_shape": "x",
                    "build_class": "x", "economic_shape": "x", "market_bet": "x"
                }
            }
        }

    def test_cabinet_framing_without_any_decision_fails(self):
        """Project with cabinet_framing but no decision in project_decision_index fails."""
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", self._state())
            self._write(tmp, "forge-tasks.json", self._tasks_with_cabinet("proj-test"))
            self._write(tmp, "forge-decisions.json", {
                "decisions": [],
                "project_decision_index": {}
            })
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("Rule 11" in e or "decision" in e.lower() for e in errors),
                f"Expected rule 11 error, got: {errors}"
            )

    def test_cabinet_framing_with_at_least_one_decision_passes(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", self._state())
            self._write(tmp, "forge-tasks.json", self._tasks_with_cabinet("proj-test"))
            self._write(tmp, "forge-decisions.json", {
                "decisions": [{
                    "id": "dec-abc12345",
                    "title": "Test", "context": "", "alternatives_considered": [],
                    "decided_by": "agent-flnt", "dissenting": [], "dissent_reason": "",
                    "decided_at": "2026-04-17T00:00:00Z",
                    "reversibility": "type_1", "review_at": "2026-07-16T00:00:00Z",
                    "project_id": "proj-test", "related_evidence": [],
                    "status": "open"
                }],
                "project_decision_index": {"proj-test": ["dec-abc12345"]}
            })
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, errors)

    def test_no_cabinet_framing_skips_rule_11_check(self):
        """Backward compat: pre-v3.2 projects (no cabinet_framing) don't trigger rule 11."""
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", self._state())
            self._write(tmp, "forge-tasks.json", {
                "tasks": [], "handoffs": [], "current_phase": 0
                # no cabinet_framing, no current_project
            })
            self._write(tmp, "forge-decisions.json", {
                "decisions": [], "project_decision_index": {}
            })
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, errors)

    def test_cabinet_framing_without_current_project_field_skips_check(self):
        """If current_project is not set in tasks, can't enforce rule 11. Backward compat."""
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", self._state())
            tasks = self._tasks_with_cabinet("proj-test")
            del tasks["current_project"]  # no project to correlate decisions with
            self._write(tmp, "forge-tasks.json", tasks)
            self._write(tmp, "forge-decisions.json", {
                "decisions": [],
                "project_decision_index": {}
            })
            ok, errors = validate_project(tmp)
            # Without current_project, we skip the rule 11 check
            self.assertTrue(ok, errors)


class TestV32PortfolioInvariants(unittest.TestCase):
    """Pins the exact v3.2 Cabinet structure to catch future drift."""

    def test_real_project_has_v32_cabinet_structure(self):
        """Real forge-state.json has: 15 agents, 9 depts, 5 execs, 10 ICs, cabinet matches."""
        repo = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        if not os.path.isfile(os.path.join(repo, 'forge-state.json')):
            self.skipTest("No forge-state.json in repo root — not a Forge checkout")
        with open(os.path.join(repo, 'forge-state.json')) as f:
            s = json.load(f)
        self.assertEqual(len(s['agents']), 15, "Expected 15 agents in v3.2 roster")
        self.assertEqual(len(s['departments']), 9, "Expected 9 departments in v3.2")
        execs = [a['id'] for a in s['agents'] if a.get('role') == 'executive']
        ics = [a['id'] for a in s['agents'] if a.get('role') == 'ic']
        self.assertEqual(len(execs), 5, f"Expected 5 executives, got {execs}")
        self.assertEqual(len(ics), 10, f"Expected 10 ICs, got {ics}")
        # Cabinet membership must match the executive set
        self.assertEqual(
            set(s['cabinet']['executives']),
            set(execs),
            "cabinet.executives must contain exactly the agents with role=executive"
        )
        # Every IC must have reports_to pointing to an executive
        execs_set = set(execs)
        for ic in [a for a in s['agents'] if a.get('role') == 'ic']:
            self.assertIn(ic.get('reports_to'), execs_set,
                         f"IC {ic['name']} reports_to {ic.get('reports_to')} which is not an executive")


class TestValidateCabinetFraming(unittest.TestCase):
    """validate_tasks enforces cabinet_framing schema when present."""

    def _state(self):
        return {
            "agents": [
                {"id": "agent-flnt", "name": "Flint", "status": "active"},
            ]
        }

    def _base_tasks(self, cabinet_framing=None):
        return {
            "tasks": [],
            "handoffs": [],
            "current_phase": 0,
            "cabinet_framing": cabinet_framing,
        }

    def test_cabinet_framing_absent_passes(self):
        from validator import validate_tasks
        tasks = {"tasks": [], "handoffs": [], "current_phase": 0}
        ok, errors = validate_tasks(tasks, self._state())
        self.assertTrue(ok, errors)

    def test_cabinet_framing_valid_structure_passes(self):
        from validator import validate_tasks
        cf = {
            "framing_brief": "1-page synthesis",
            "lenses": {
                "strategic_kernel": "Diagnosis...",
                "product_shape": "User is...",
                "build_class": "Greenfield",
                "economic_shape": "Unit econ...",
                "market_bet": "Position as..."
            }
        }
        ok, errors = validate_tasks(self._base_tasks(cabinet_framing=cf), self._state())
        self.assertTrue(ok, errors)

    def test_cabinet_framing_missing_lens_fails(self):
        from validator import validate_tasks
        cf = {
            "framing_brief": "x",
            "lenses": {
                "strategic_kernel": "x",
            }
        }
        ok, errors = validate_tasks(self._base_tasks(cabinet_framing=cf), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("product_shape" in e for e in errors), errors)

    def test_cabinet_framing_extra_lens_key_fails(self):
        from validator import validate_tasks
        cf = {
            "framing_brief": "x",
            "lenses": {
                "strategic_kernel": "x", "product_shape": "x", "build_class": "x",
                "economic_shape": "x", "market_bet": "x",
                "seventh_lens": "oops"
            }
        }
        ok, errors = validate_tasks(self._base_tasks(cabinet_framing=cf), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("seventh_lens" in e for e in errors), errors)

    def test_cabinet_framing_missing_framing_brief_fails(self):
        from validator import validate_tasks
        cf = {
            "lenses": {
                "strategic_kernel": "x", "product_shape": "x",
                "build_class": "x", "economic_shape": "x", "market_bet": "x"
            }
        }
        ok, errors = validate_tasks(self._base_tasks(cabinet_framing=cf), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("framing_brief" in e.lower() for e in errors), errors)

    def test_cabinet_framing_non_dict_fails(self):
        from validator import validate_tasks
        ok, errors = validate_tasks(
            self._base_tasks(cabinet_framing="not a dict"), self._state()
        )
        self.assertFalse(ok)
        self.assertTrue(any("cabinet_framing" in e.lower() for e in errors), errors)


class TestValidatePreMortem(unittest.TestCase):
    """validate_tasks enforces pre_mortem schema when present."""

    def _state(self, agent_ids=("agent-flnt", "agent-lexx")):
        return {
            "agents": [{"id": a, "name": a, "status": "active"} for a in agent_ids]
        }

    def _base_tasks(self, pre_mortem=None):
        return {
            "tasks": [],
            "handoffs": [],
            "current_phase": 0,
            "pre_mortem": pre_mortem,
        }

    def test_pre_mortem_absent_passes(self):
        """Backward compat: forge-tasks without pre_mortem still validates."""
        from validator import validate_tasks
        tasks = {"tasks": [], "handoffs": [], "current_phase": 0}
        ok, errors = validate_tasks(tasks, self._state())
        self.assertTrue(ok, errors)

    def test_pre_mortem_empty_list_passes(self):
        from validator import validate_tasks
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=[]), self._state())
        self.assertTrue(ok, errors)

    def test_pre_mortem_valid_entry_passes(self):
        from validator import validate_tasks
        pm = [{
            "failure_mode": "PDPL non-compliance",
            "likelihood": 4, "impact": 5, "score": 20,
            "owner_agent": "agent-lexx",
            "mitigation_phase": "phase_5_gtm"
        }]
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=pm), self._state())
        self.assertTrue(ok, errors)

    def test_pre_mortem_owner_agent_nonexistent_fails(self):
        from validator import validate_tasks
        pm = [{
            "failure_mode": "x", "likelihood": 3, "impact": 3, "score": 9,
            "owner_agent": "agent-ghost", "mitigation_phase": "phase_5_gtm"
        }]
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=pm), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("agent-ghost" in e for e in errors), errors)

    def test_pre_mortem_likelihood_out_of_range_fails(self):
        from validator import validate_tasks
        pm = [{
            "failure_mode": "x", "likelihood": 7, "impact": 3, "score": 21,
            "owner_agent": "agent-lexx", "mitigation_phase": "phase_5_gtm"
        }]
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=pm), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("likelihood" in e.lower() for e in errors), errors)

    def test_pre_mortem_impact_out_of_range_fails(self):
        from validator import validate_tasks
        pm = [{
            "failure_mode": "x", "likelihood": 3, "impact": 0, "score": 0,
            "owner_agent": "agent-lexx", "mitigation_phase": "phase_5_gtm"
        }]
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=pm), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("impact" in e.lower() for e in errors), errors)

    def test_pre_mortem_invalid_mitigation_phase_fails(self):
        from validator import validate_tasks
        pm = [{
            "failure_mode": "x", "likelihood": 3, "impact": 3, "score": 9,
            "owner_agent": "agent-lexx", "mitigation_phase": "phase_99_yolo"
        }]
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=pm), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("mitigation_phase" in e.lower() for e in errors), errors)

    def test_pre_mortem_missing_failure_mode_fails(self):
        from validator import validate_tasks
        pm = [{
            "likelihood": 3, "impact": 3, "score": 9,
            "owner_agent": "agent-lexx", "mitigation_phase": "phase_5_gtm"
        }]
        ok, errors = validate_tasks(self._base_tasks(pre_mortem=pm), self._state())
        self.assertFalse(ok)
        self.assertTrue(any("failure_mode" in e.lower() for e in errors), errors)


class TestValidateProjectLoadsDecisions(unittest.TestCase):
    def _write(self, tmp, fname, obj):
        with open(os.path.join(tmp, fname), "w") as f:
            json.dump(obj, f)

    def test_validate_project_loads_forge_decisions_when_present(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", {
                "company": {"name": "T", "founded": "2026-01-01"},
                "departments": [],
                "agents": [{"id": "agent-flnt", "name": "Flint", "status": "active"}],
            })
            self._write(tmp, "forge-decisions.json", {
                "decisions": [],
                "project_decision_index": {}
            })
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, errors)

    def test_validate_project_catches_decisions_json_malformed(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", {
                "company": {"name": "T", "founded": "2026-01-01"},
                "departments": [],
                "agents": [],
            })
            with open(os.path.join(tmp, "forge-decisions.json"), "w") as f:
                f.write("{ broken ]")
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(
                any("forge-decisions.json" in e and "json" in e.lower() for e in errors),
                errors,
            )

    def test_validate_project_catches_bad_decision_data(self):
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", {
                "company": {"name": "T", "founded": "2026-01-01"},
                "departments": [],
                "agents": [{"id": "agent-flnt", "name": "Flint", "status": "active"}],
            })
            self._write(tmp, "forge-decisions.json", {
                "decisions": [{
                    "id": "BADID",
                    "title": "bad decision", "context": "",
                    "alternatives_considered": [], "decided_by": "agent-flnt",
                    "dissenting": [], "dissent_reason": "",
                    "decided_at": "2026-04-17T00:00:00Z",
                    "reversibility": "type_1", "review_at": "2026-07-16T00:00:00Z",
                    "project_id": "proj-001", "related_evidence": [],
                    "status": "open"
                }],
                "project_decision_index": {}
            })
            ok, errors = validate_project(tmp)
            self.assertFalse(ok)
            self.assertTrue(any("BADID" in e for e in errors), errors)

    def test_validate_project_passes_when_decisions_absent(self):
        """Projects without a forge-decisions.json still validate (backward compat)."""
        from validator import validate_project
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "forge-state.json", {
                "company": {"name": "T", "founded": "2026-01-01"},
                "departments": [],
                "agents": [],
            })
            ok, errors = validate_project(tmp)
            self.assertTrue(ok, errors)


class TestValidateDecisions(unittest.TestCase):
    """validate_decisions(doc, state, evidence_doc=None) -> (ok, errors)"""

    def _doc(self, decisions=None, index=None):
        return {
            "decisions": decisions or [],
            "project_decision_index": index or {},
        }

    def _state(self, agent_ids=("agent-flnt",)):
        return {
            "agents": [{"id": a, "name": a, "status": "active"} for a in agent_ids]
        }

    def _decision(self, **kwargs):
        base = {
            "id": "dec-abc12345",
            "title": "Test decision",
            "context": "unit test",
            "alternatives_considered": ["A (reject: x)", "B (selected)"],
            "decided_by": "agent-flnt",
            "dissenting": [],
            "dissent_reason": "",
            "decided_at": "2026-04-17T00:00:00Z",
            "reversibility": "type_1",
            "review_at": "2026-07-16T00:00:00Z",
            "project_id": "proj-001",
            "related_evidence": [],
            "status": "open",
        }
        base.update(kwargs)
        return base

    def test_empty_doc_passes(self):
        from validator import validate_decisions
        ok, errors = validate_decisions(self._doc(), self._state())
        self.assertTrue(ok, errors)

    def test_invalid_id_format_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(id="BADID")])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("id" in e.lower() and "BADID" in e for e in errors), errors)

    def test_duplicate_ids_fail(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[
            self._decision(id="dec-aaaabbbb"),
            self._decision(id="dec-aaaabbbb"),
        ])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("duplicate" in e.lower() for e in errors), errors)

    def test_decided_by_nonexistent_agent_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(decided_by="agent-ghost")])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("agent-ghost" in e for e in errors), errors)

    def test_dissenting_nonexistent_agent_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(dissenting=["agent-ghost"])])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("agent-ghost" in e for e in errors), errors)

    def test_bad_reversibility_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(reversibility="maybe")])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("reversibility" in e.lower() for e in errors), errors)

    def test_bad_status_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(status="pending")])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("status" in e.lower() for e in errors), errors)

    def test_malformed_decided_at_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(decided_at="yesterday")])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)

    def test_malformed_review_at_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(review_at="tomorrow")])
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)

    def test_related_evidence_nonexistent_fails(self):
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(related_evidence=["ev-ghost000"])])
        evidence_doc = {"evidence": [], "project_evidence_index": {}}
        ok, errors = validate_decisions(doc, self._state(), evidence_doc)
        self.assertFalse(ok)
        self.assertTrue(any("ev-ghost000" in e for e in errors), errors)

    def test_related_evidence_not_checked_when_evidence_doc_absent(self):
        """If no evidence_doc is provided, skip related_evidence validation."""
        from validator import validate_decisions
        doc = self._doc(decisions=[self._decision(related_evidence=["ev-anyid0001"])])
        ok, errors = validate_decisions(doc, self._state())  # no evidence_doc arg
        self.assertTrue(ok, errors)

    def test_project_decision_index_ref_missing_fails(self):
        from validator import validate_decisions
        doc = self._doc(index={"proj-001": ["dec-ghost000"]})
        ok, errors = validate_decisions(doc, self._state())
        self.assertFalse(ok)
        self.assertTrue(any("dec-ghost000" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
