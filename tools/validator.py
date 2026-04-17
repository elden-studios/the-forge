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
from datetime import datetime
from urllib.parse import urlparse

_TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

from evidence_schema import SOURCE_TYPES, SIGNAL_TAGS  # noqa: E402


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

    ev_path = os.path.join(project_dir, "forge-evidence.json")
    if os.path.isfile(ev_path):
        try:
            with open(ev_path) as f:
                evidence_doc = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"forge-evidence.json is not valid json: {e}")
            return (False, errors)
        errors.extend(validate_evidence(evidence_doc, state)[1])

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


def validate_evidence(evidence_doc, state):
    """Validate forge-evidence.json against forge-state.json.

    Returns (ok, errors).
    """
    errors = []
    items = evidence_doc.get("evidence", [])
    index = evidence_doc.get("project_evidence_index", {})
    agent_ids = {a["id"] for a in state.get("agents", [])}

    # Every evidence item must have a non-empty id, and ids must be unique
    seen = set()
    for idx, it in enumerate(items):
        eid = it.get("id")
        if not eid:
            errors.append(f"Evidence at index {idx} is missing required field: id")
            continue
        if eid in seen:
            errors.append(f"Evidence duplicate id: {eid}")
        seen.add(eid)

    valid_ids = set(seen)

    # Index references point to real evidence
    for proj, ids in index.items():
        for ref in ids:
            if ref not in valid_ids:
                errors.append(
                    f"project_evidence_index[{proj}] references non-existent Evidence: {ref}"
                )

    # Per-item field validation
    for idx, it in enumerate(items):
        eid = it.get("id") or f"(index {idx})"
        # retrieved_by must be a list (or None/missing, treated as empty)
        rb = it.get("retrieved_by")
        if rb is None:
            rb = []
        if not isinstance(rb, list):
            errors.append(f"Evidence {eid} retrieved_by must be a list, got: {type(rb).__name__}")
        else:
            for agent in rb:
                if agent not in agent_ids:
                    errors.append(f"Evidence {eid} retrieved_by references non-existent agent: {agent}")
        q = it.get("quality_score")
        if not isinstance(q, int) or isinstance(q, bool) or q < 1 or q > 5:
            errors.append(f"Evidence {eid} quality_score out of range: {q}")
        c = it.get("confidence")
        if not isinstance(c, (int, float)) or isinstance(c, bool) or c < 0 or c > 1:
            errors.append(f"Evidence {eid} confidence out of range: {c}")
        if it.get("source_type") not in SOURCE_TYPES:
            errors.append(f"Evidence {eid} invalid source_type: {it.get('source_type')}")
        if it.get("signal_tag") not in SIGNAL_TAGS:
            errors.append(f"Evidence {eid} invalid signal_tag: {it.get('signal_tag')}")
        url = it.get("source_url", "") or ""
        if url.startswith("local://"):
            pass
        else:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                errors.append(f"Evidence {eid} invalid source_url: {url}")
        ts = it.get("retrieved_at", "")
        if not isinstance(ts, str) or not ts:
            errors.append(f"Evidence {eid} malformed retrieved_at: {ts}")
        else:
            # Use fromisoformat (Python 3.7+) — accepts fractional seconds.
            # Normalize 'Z' → '+00:00' for consistent handling across real sources
            # (WebSearch, Chrome MCP returns often include fractional seconds).
            try:
                datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except (ValueError, TypeError):
                errors.append(f"Evidence {eid} malformed retrieved_at: {ts}")

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
    # v3.2: map each agent id to its role for reports_to checks
    agent_roles = {a["id"]: a.get("role") for a in state.get("agents", [])}

    # Uniqueness checks for avatar attributes among active agents
    _check_avatar_uniqueness(active_agents, "hairstyle", errors)
    _check_avatar_uniqueness(active_agents, "idle_animation", errors)

    ALLOWED_ROLES = {"executive", "ic"}

    for agent in state.get("agents", []):
        name = agent.get("name", agent.get("id"))
        agent_id = agent.get("id")
        dep = agent.get("department_id")
        if dep and dep not in dept_ids:
            errors.append(
                f"Agent {name} references non-existent department: {dep}"
            )

        # v3.2: role enum check
        if "role" in agent:
            role = agent["role"]
            if role not in ALLOWED_ROLES:
                errors.append(
                    f"Agent {name} role must be 'executive' or 'ic', got: {role}"
                )

        # v3.2: reports_to referential integrity
        reports_to = agent.get("reports_to")
        if reports_to is not None:
            if not isinstance(reports_to, str):
                errors.append(
                    f"Agent {name} reports_to must be a string (agent id), "
                    f"got {type(reports_to).__name__}"
                )
            elif reports_to == agent_id:
                errors.append(
                    f"Agent {name} reports_to cannot reference itself: {reports_to}"
                )
            elif reports_to not in agent_ids:
                errors.append(
                    f"Agent {name} reports_to references non-existent agent: {reports_to}"
                )
            else:
                # If the reporter is an IC, its reports_to MUST be an executive
                if agent.get("role") == "ic":
                    target_role = agent_roles.get(reports_to)
                    if target_role != "executive":
                        errors.append(
                            f"Agent {name} (ic) reports_to must be an executive, "
                            f"got {reports_to} with role {target_role!r}"
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

    # v3.2: cabinet.executives block
    cabinet = state.get("cabinet")
    if cabinet is not None:
        if not isinstance(cabinet, dict):
            errors.append(
                f"cabinet must be a dict, got {type(cabinet).__name__}"
            )
        else:
            if "executives" in cabinet:
                execs = cabinet.get("executives")
                if not isinstance(execs, list):
                    errors.append(
                        f"cabinet.executives must be a list, got {type(execs).__name__}"
                    )
                else:
                    for exec_id in execs:
                        if exec_id not in agent_ids:
                            errors.append(
                                f"cabinet.executives references non-existent agent: {exec_id}"
                            )
                        elif agent_roles.get(exec_id) != "executive":
                            errors.append(
                                f"cabinet.executives member {exec_id} must have role='executive', "
                                f"got {agent_roles.get(exec_id)!r}"
                            )

    return (len(errors) == 0, errors)


def main(argv):
    """CLI entry point.

    Args:
        argv: list of CLI arguments (without program name). First positional
              argument (optional) is the project directory. Defaults to cwd.
              Pass --cache-stats [dir] to display cache statistics.

    Returns:
        Exit code: 0 if valid, 1 if validation errors were found.
    """
    if argv and argv[0] == "--cache-stats":
        from evidence_cache import cache_stats
        project_dir = argv[1] if len(argv) > 1 else os.getcwd()
        stats = cache_stats(os.path.join(project_dir, "assets", ".forge-cache"))
        print(f"Cache stats: {stats['entries']} entries, {stats['size_bytes']} bytes")
        return 0
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
