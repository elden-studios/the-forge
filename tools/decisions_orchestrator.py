"""Decision Log orchestration — Type 1 / Type 2 reversibility, lifecycle ops.

Pure-function library over the forge-decisions.json data model. No network I/O.
Atomic writes via tempfile + os.replace (same pattern as evidence_orchestrator).

CLI-free — all entrypoints are Python functions consumed by the validator and
by scripts/cabinet_framing_simulate.py.
"""
from datetime import datetime, timedelta
import uuid


DECISION_STATUSES = frozenset({"open", "reviewed", "reversed", "committed"})
REVERSIBILITY = frozenset({"type_1", "type_2"})

# Per spec: Type 1 (one-way door) reviewed at 90d, Type 2 (two-way door) at 30d
_REVIEW_DAYS = {"type_1": 90, "type_2": 30}


def new_decision_id():
    """Generate a fresh decision ID like 'dec-7f2a3c9d'."""
    return f"dec-{uuid.uuid4().hex[:8]}"


def _parse_iso(iso):
    """Parse an ISO 8601 timestamp, accepting fractional seconds and Z suffix.

    Matches the pattern used by tools/validator.py and tools/evidence_freshness.py
    so all three modules handle real-world timestamps consistently.
    """
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def _format_iso_utc(dt):
    """Format a datetime as ISO 8601 UTC with a Z suffix (matches retrieved_at style)."""
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def compute_review_at(decided_at_iso, reversibility):
    """Return review_at ISO string for a decision.

    Type 1 (one-way door): 90 days after decided_at.
    Type 2 (two-way door): 30 days after decided_at.

    Raises ValueError on invalid reversibility or malformed decided_at.
    """
    if reversibility not in REVERSIBILITY:
        raise ValueError(
            f"reversibility must be one of {sorted(REVERSIBILITY)}, got: {reversibility!r}"
        )
    try:
        dt = _parse_iso(decided_at_iso)
    except (ValueError, TypeError, AttributeError) as e:
        raise ValueError(
            f"decided_at must be a valid ISO 8601 string, got: {decided_at_iso!r} ({e})"
        )
    review_dt = dt + timedelta(days=_REVIEW_DAYS[reversibility])
    # If tz-aware, convert to UTC before stripping tz — prevents silent
    # offset drop (e.g., +03:00 would otherwise be reported as Z without
    # the 3-hour shift being applied).
    if review_dt.tzinfo is not None:
        from datetime import timezone
        review_dt = review_dt.astimezone(timezone.utc).replace(tzinfo=None)
    return _format_iso_utc(review_dt)


import json as _json
import os
import tempfile


def _atomic_write_json(path, doc):
    """Write JSON atomically via tempfile + os.replace.

    Mirrors tools/evidence_orchestrator._atomic_write_json — same invariant
    that a mid-write interruption leaves the original file intact.
    """
    dir_ = os.path.dirname(path) or "."
    stem = os.path.basename(path).rsplit(".", 1)[0]
    fd, tmp = tempfile.mkstemp(dir=dir_, prefix=f".{stem}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            _json.dump(doc, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            try:
                os.remove(tmp)
            except OSError:
                pass
        raise


def append_decision(project_id, decision, decisions_path):
    """Persist a decision to forge-decisions.json atomically.

    Atomically writes to the primary path AND mirrors to <parent>/assets/<basename>
    when that sibling directory exists — the live dashboard reads from assets/
    via the local http.server, so the mirror prevents split-brain UX where the
    backend writes decisions but the UI shows 0.

    Updates project_decision_index[project_id] to include the new decision id,
    extending (not replacing) any existing list. Deduped by id.
    """
    with open(decisions_path) as f:
        doc = _json.load(f)

    existing_ids = {d["id"] for d in doc.get("decisions", [])}
    if decision["id"] not in existing_ids:
        doc["decisions"].append(decision)
        existing_ids.add(decision["id"])

    index = doc.setdefault("project_decision_index", {})
    current = set(index.get(project_id, []))
    current.add(decision["id"])
    index[project_id] = sorted(current)

    _atomic_write_json(decisions_path, doc)

    parent = os.path.dirname(os.path.abspath(decisions_path)) or "."
    assets_dir = os.path.join(parent, "assets")
    if os.path.isdir(assets_dir):
        mirror_path = os.path.join(assets_dir, os.path.basename(decisions_path))
        try:
            _atomic_write_json(mirror_path, doc)
        except OSError:
            pass


def review_decisions_due(doc, now_iso):
    """Return the list of open decisions whose review_at has passed.

    A decision is 'due' only if status == 'open' AND review_at <= now.
    Already-reviewed / reversed / committed decisions are excluded.
    """
    now_dt = _parse_iso(now_iso)
    due = []
    for d in doc.get("decisions", []):
        if d.get("status") != "open":
            continue
        review_at = d.get("review_at")
        if not review_at:
            continue
        try:
            review_dt = _parse_iso(review_at)
        except (ValueError, TypeError):
            continue
        if review_dt <= now_dt:
            due.append(d)
    return due


def close_decision(doc, decision_id, new_status):
    """Transition a decision from 'open' to 'reviewed' or 'committed'.

    Mutates doc in-place. Caller is responsible for persistence.
    Raises ValueError on unknown status OR on attempting to close a
    decision whose current status is NOT 'open' (terminal states are
    terminal). Raises KeyError on unknown decision_id.

    Note: use reverse_decision() to transition to 'reversed' (it needs
    a successor reference).
    """
    CLOSE_TARGETS = {"reviewed", "committed"}
    if new_status not in CLOSE_TARGETS:
        raise ValueError(
            f"close_decision status must be one of {sorted(CLOSE_TARGETS)}, "
            f"got: {new_status!r}. Use reverse_decision() for 'reversed'."
        )
    for d in doc.get("decisions", []):
        if d.get("id") == decision_id:
            current = d.get("status")
            if current != "open":
                raise ValueError(
                    f"decision {decision_id} has status {current!r}; "
                    f"close_decision only transitions from 'open'"
                )
            d["status"] = new_status
            return
    raise KeyError(f"decision not found: {decision_id}")


def reverse_decision(doc, decision_id, successor_id):
    """Mark a decision as 'reversed' and link the successor that overrode it.

    Mutates doc in-place. Both decisions must already exist and must be
    distinct. The original decision cannot already be reversed.
    """
    if decision_id == successor_id:
        raise ValueError(
            f"decision cannot reverse itself: {decision_id}"
        )
    decisions_by_id = {d.get("id"): d for d in doc.get("decisions", [])}

    if decision_id not in decisions_by_id:
        raise KeyError(f"decision not found: {decision_id}")
    if successor_id not in decisions_by_id:
        raise KeyError(f"successor decision not found: {successor_id}")

    original = decisions_by_id[decision_id]
    if original.get("status") == "reversed":
        raise ValueError(f"decision {decision_id} is already reversed")

    original["status"] = "reversed"
    original["reversed_by"] = successor_id
