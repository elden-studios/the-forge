"""The Forge state validator.

Validates forge-state.json and forge-tasks.json for referential integrity,
uniqueness constraints, and completeness rules.

CLI usage:
    python3 tools/validator.py [project_dir]

If no project_dir is given, validates the current working directory.
Exits 0 on success, 1 on validation errors.
"""
import json
import os
import sys


def validate_project(project_dir):
    """Run all validators on a project directory.

    Expects:
      - forge-state.json in project_dir
      - forge-tasks.json in project_dir (optional)
      - references/brains/ directory (optional)

    Returns (ok: bool, errors: list[str]).
    """
    errors = []
    state_path = os.path.join(project_dir, "forge-state.json")
    tasks_path = os.path.join(project_dir, "forge-tasks.json")
    brains_dir = os.path.join(project_dir, "references", "brains")

    if not os.path.isfile(state_path):
        errors.append(f"Missing forge-state.json in {project_dir}")
        return (False, errors)

    try:
        with open(state_path) as f:
            state = json.load(f)
    except json.JSONDecodeError as e:
        errors.append(f"forge-state.json is not valid json: {e}")
        return (False, errors)

    errors.extend(validate_state(state)[1])

    if os.path.isdir(brains_dir):
        errors.extend(validate_brain_files(state, brains_dir)[1])

    if os.path.isfile(tasks_path):
        try:
            with open(tasks_path) as f:
                tasks = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"forge-tasks.json is not valid json: {e}")
            return (False, errors)
        errors.extend(validate_tasks(tasks, state)[1])

    return (len(errors) == 0, errors)


def validate_tasks(tasks, state):
    """Validate forge-tasks dict against forge-state dict.

    Returns (ok: bool, errors: list[str]).
    """
    errors = []
    agent_ids = {a["id"] for a in state.get("agents", [])}

    for task in tasks.get("tasks", []):
        agent_id = task.get("agent")
        if agent_id and agent_id not in agent_ids:
            errors.append(
                f"Task {task.get('id', '(unnamed)')} references "
                f"non-existent agent: {agent_id}"
            )
        for side in ("handoff_from", "handoff_to"):
            ref = task.get(side)
            if ref and ref not in agent_ids:
                errors.append(
                    f"Task {task.get('id', '(unnamed)')} {side} references "
                    f"non-existent agent: {ref}"
                )

    for handoff in tasks.get("handoffs", []):
        for side in ("from", "to"):
            agent_id = handoff.get(side)
            if agent_id and agent_id not in agent_ids:
                errors.append(
                    f"Handoff '{side}' references non-existent agent: {agent_id}"
                )

    phase = tasks.get("current_phase", 0)
    if not isinstance(phase, int) or phase < 0 or phase > 8:
        errors.append(f"Invalid phase number: {phase} (must be 0-8)")

    return (len(errors) == 0, errors)


def validate_brain_files(state, brains_dir):
    """Check that each active agent has a corresponding brain file.

    Brain filename convention: {name.lower()}-brain.md

    Returns (ok: bool, errors: list[str]).
    """
    errors = []
    for agent in state.get("agents", []):
        if agent.get("status") != "active":
            continue
        name = agent.get("name", "")
        expected = f"{name.lower()}-brain.md"
        path = os.path.join(brains_dir, expected)
        if not os.path.isfile(path):
            errors.append(
                f"Missing brain file for active agent {name}: expected {expected}"
            )
    return (len(errors) == 0, errors)


def _check_avatar_uniqueness(active_agents, attr, errors):
    """Append an error for each duplicate avatar attribute value among active agents."""
    seen = {}
    for agent in active_agents:
        value = (agent.get("avatar") or {}).get(attr)
        if not value:
            continue
        if value in seen:
            errors.append(
                f"Duplicate {attr} '{value}' shared by active agents: "
                f"{seen[value]} and {agent.get('name')}"
            )
        else:
            seen[value] = agent.get("name")


def validate_state(state):
    """Validate a forge-state dict.

    Returns (ok: bool, errors: list[str]).
    """
    errors = []
    dept_ids = {d["id"] for d in state.get("departments", [])}
    agent_ids = {a["id"] for a in state.get("agents", [])}
    active_agents = [a for a in state.get("agents", []) if a.get("status") == "active"]

    # Uniqueness checks for avatar attributes among active agents
    _check_avatar_uniqueness(active_agents, "hairstyle", errors)
    _check_avatar_uniqueness(active_agents, "idle_animation", errors)

    for agent in state.get("agents", []):
        name = agent.get("name", agent.get("id"))
        dep = agent.get("department_id")
        if dep and dep not in dept_ids:
            errors.append(
                f"Agent {name} references non-existent department: {dep}"
            )
        links = agent.get("collaboration_links") or {}
        for link_key in ("hands_off_to", "requests_input_from", "debates_with"):
            for target in links.get(link_key, []):
                if target not in agent_ids:
                    errors.append(
                        f"Agent {name} {link_key} references "
                        f"non-existent agent: {target}"
                    )

    for key, override in (state.get("routing_overrides") or {}).items():
        lead = (override or {}).get("lead_agent")
        if lead and lead not in agent_ids:
            errors.append(
                f"routing_overrides.{key}.lead_agent references "
                f"non-existent agent: {lead}"
            )

    for entry in state.get("project_history", []):
        proj_id = entry.get("id", "(unnamed project)")
        for target in entry.get("agents_involved", []):
            if target and target not in agent_ids:
                errors.append(
                    f"project_history {proj_id} agents_involved references "
                    f"non-existent agent: {target}"
                )

    return (len(errors) == 0, errors)


def main(argv):
    """CLI entry point.

    Args:
        argv: list of CLI arguments (without program name). First positional
              argument (optional) is the project directory. Defaults to cwd.

    Returns:
        Exit code: 0 if valid, 1 if validation errors were found.
    """
    project_dir = argv[0] if argv else os.getcwd()
    ok, errors = validate_project(project_dir)
    if ok:
        print(f"OK — {project_dir} passed all validation checks")
        return 0
    print(f"FAIL — {len(errors)} validation error(s) in {project_dir}:")
    for i, e in enumerate(errors, 1):
        print(f"  {i}. {e}")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
