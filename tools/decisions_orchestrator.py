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
    return _format_iso_utc(review_dt.replace(tzinfo=None))


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
