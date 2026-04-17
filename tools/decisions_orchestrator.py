"""Decision Log orchestration — Type 1 / Type 2 reversibility, lifecycle ops.

Pure-function library over the forge-decisions.json data model. No network I/O.
Atomic writes via tempfile + os.replace (same pattern as evidence_orchestrator).

CLI-free — all entrypoints are Python functions consumed by the validator and
by scripts/cabinet_framing_simulate.py.
"""
from datetime import datetime, timedelta
import logging
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


def _to_naive_utc(dt):
    """Return a naive-UTC datetime. Tz-aware inputs are converted to UTC
    and stripped of tzinfo; naive inputs are returned as-is (assumed UTC
    per project convention).

    Used by append_decision to make datetime subtraction safe across
    mixed aware/naive pairs. Matches compute_review_at's tz handling.
    """
    from datetime import timezone
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


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


def append_decision(doc, decision):
    """Append a decision to the doc's decisions array with upsert semantics.

    Mutates doc in-place. No I/O. Also maintains doc['project_decision_index']
    for the decision's project_id.

    Upsert (dedup) rules — a no-op occurs when ANY of these matches an existing entry:
    (a) Same 'id' as an existing entry (historical W2 behavior — dedup by id).
    (b) Same (title, decided_by, project_id) triple AND |decided_at_delta| < 60s
        (Wave 3 addition — prevents simulation-driver reruns from accumulating
        near-duplicate entries).

    The 60s window is the time skew a repeated simulation run produces when the
    human operator re-invokes the driver within a minute. Genuine follow-up
    decisions on the same topic land at different minutes and are preserved.

    Wave 3 — Task 0.1.
    """
    # Rule (a) — id-based dedup (existing W2 behavior preserved at the pure layer)
    existing_ids = {d.get("id") for d in doc.get("decisions", [])}
    if decision.get("id") in existing_ids:
        return

    # Rule (b) — upsert collapse within 60s on (title, decided_by, project_id)
    incoming_key = (decision.get("title"), decision.get("decided_by"), decision.get("project_id"))
    if all(x is not None for x in incoming_key):
        try:
            incoming_dt = _parse_iso(decision["decided_at"])
        except (ValueError, TypeError, KeyError, AttributeError):
            incoming_dt = None
        if incoming_dt is not None:
            # Normalize to naive-UTC so subtraction never crashes on mixed
            # aware/naive pairs. Naive timestamps are treated as UTC, matching
            # the convention used in compute_review_at and how the simulation
            # driver emits Z-suffixed timestamps.
            incoming_utc = _to_naive_utc(incoming_dt)
            for existing in doc.get("decisions", []):
                existing_key = (
                    existing.get("title"),
                    existing.get("decided_by"),
                    existing.get("project_id"),
                )
                if existing_key != incoming_key:
                    continue
                try:
                    existing_dt = _parse_iso(existing["decided_at"])
                except (ValueError, TypeError, KeyError, AttributeError):
                    continue
                existing_utc = _to_naive_utc(existing_dt)
                if abs((incoming_utc - existing_utc).total_seconds()) < 60:
                    return  # no-op: upsert collapse

    # Append
    doc.setdefault("decisions", []).append(decision)

    # Maintain project_decision_index
    pid = decision.get("project_id")
    if pid:
        index = doc.setdefault("project_decision_index", {})
        current = set(index.get(pid, []))
        current.add(decision["id"])
        index[pid] = sorted(current)


def append_decision_persist(project_id, decision, decisions_path):
    """Persist a decision to forge-decisions.json atomically (I/O wrapper around append_decision).

    Atomically writes to the primary path AND mirrors to <parent>/assets/<basename>
    when that sibling directory exists — the live dashboard reads from assets/
    via the local http.server, so the mirror prevents split-brain UX where the
    backend writes decisions but the UI shows 0.

    Delegates the in-memory mutation (append + project_decision_index update +
    upsert dedup) to the pure append_decision(doc, decision). Any caller that
    wants pure semantics can use append_decision() directly.
    """
    with open(decisions_path) as f:
        doc = _json.load(f)

    # Ensure the incoming decision carries the project_id so the pure function
    # can update project_decision_index[project_id] without needing the separate
    # argument (and without breaking backward compat — any existing callers pass
    # project_id separately but also include it inside the decision dict per the
    # Wave 2 schema).
    if decision.get("project_id") != project_id:
        decision = dict(decision, project_id=project_id)

    append_decision(doc, decision)

    _atomic_write_json(decisions_path, doc)

    parent = os.path.dirname(os.path.abspath(decisions_path)) or "."
    assets_dir = os.path.join(parent, "assets")
    if os.path.isdir(assets_dir):
        mirror_path = os.path.join(assets_dir, os.path.basename(decisions_path))
        try:
            _atomic_write_json(mirror_path, doc)
        except OSError as e:
            logging.warning("decisions_orchestrator: mirror write to %s failed: %s", mirror_path, e)


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


def close_decision_persist(path, decision_id, *, new_status="committed"):
    """Load-mutate-atomic-write-mirror wrapper around close_decision.

    Opens `path`, parses as JSON, calls the pure close_decision, atomic-writes
    back to `path`, and mirrors to <parent>/assets/<basename> if that sibling
    directory exists (matches append_decision_persist's mirror convention —
    the live dashboard reads from assets/).

    Propagates ValueError / KeyError from the pure function unchanged so the
    dashboard UI can distinguish "bad status" / "bad transition" / "not found"
    signals.

    Atomicity: if the pure function raises, the primary file is untouched
    (no disk write attempted until after the mutation succeeds in memory).

    See also: append_decision_persist (creation), reverse_decision_persist (type-2 override).

    Wave 3 — Task 0.2.
    """
    with open(path) as f:
        doc = _json.load(f)
    close_decision(doc, decision_id, new_status)  # pure — raises on bad state
    _atomic_write_json(path, doc)
    parent = os.path.dirname(os.path.abspath(path)) or "."
    assets_dir = os.path.join(parent, "assets")
    if os.path.isdir(assets_dir):
        mirror_path = os.path.join(assets_dir, os.path.basename(path))
        try:
            _atomic_write_json(mirror_path, doc)
        except OSError as e:
            logging.warning("decisions_orchestrator: mirror write to %s failed: %s", mirror_path, e)


def reverse_decision_persist(path, decision_id, successor_id):
    """Load-mutate-atomic-write-mirror wrapper around reverse_decision.

    Opens `path`, parses as JSON, calls the pure reverse_decision (which sets
    status='reversed' and reversed_by=successor_id on the original), atomic-writes
    back, and mirrors to <parent>/assets/ if present.

    Propagates ValueError (self-reference or already-reversed) and KeyError
    (missing decision_id or missing successor_id) from the pure function.

    The reversal reason is carried in the successor decision's `context` field,
    not here — keep this wrapper's signature minimal.

    See also: append_decision_persist (creation), close_decision_persist (lifecycle close).

    Wave 3 — Task 0.2.
    """
    with open(path) as f:
        doc = _json.load(f)
    reverse_decision(doc, decision_id, successor_id)  # pure — raises on bad state
    _atomic_write_json(path, doc)
    parent = os.path.dirname(os.path.abspath(path)) or "."
    assets_dir = os.path.join(parent, "assets")
    if os.path.isdir(assets_dir):
        mirror_path = os.path.join(assets_dir, os.path.basename(path))
        try:
            _atomic_write_json(mirror_path, doc)
        except OSError as e:
            logging.warning("decisions_orchestrator: mirror write to %s failed: %s", mirror_path, e)


def query_by_project(doc, project_id):
    """Return decisions belonging to `project_id`, in insertion order.

    Unknown project_id → empty list. Does not consult project_decision_index —
    scans the decisions array directly so the result is self-consistent even if
    the index is stale.

    Wave 3 — Task 0.3.
    """
    return [d for d in doc.get("decisions", []) if d.get("project_id") == project_id]


def query_by_status(doc, status):
    """Return decisions with matching status, in insertion order.

    Raises ValueError if `status` is not one of DECISION_STATUSES.

    Wave 3 — Task 0.3.
    """
    if status not in DECISION_STATUSES:
        raise ValueError(
            f"status must be one of {sorted(DECISION_STATUSES)}, got: {status!r}"
        )
    return [d for d in doc.get("decisions", []) if d.get("status") == status]


def query_due_soon(doc, now, horizon_days=30):
    """Return open decisions whose review_at is at or before `now + horizon_days`.

    Only decisions with status == 'open' are eligible — reviewed, committed, and
    reversed decisions are excluded regardless of review_at. This matches the
    semantics of `review_decisions_due(doc, now_iso)` (which uses the same
    open-only filter but takes a point-in-time rather than a look-ahead window).

    `now` must be a timezone-aware datetime. Naive review_at values in the doc
    are treated as UTC (matches `_to_naive_utc` / `compute_review_at` convention).

    Decisions with missing or malformed review_at are silently skipped — they
    can't be "due" if we don't know when.

    Wave 3 — Task 0.3.
    """
    horizon = now + timedelta(days=horizon_days)
    horizon_naive = _to_naive_utc(horizon)
    out = []
    for d in doc.get("decisions", []):
        if d.get("status") != "open":
            continue
        review_at = d.get("review_at")
        if not review_at:
            continue
        try:
            review_dt = _parse_iso(review_at)
        except (ValueError, TypeError, AttributeError):
            continue
        review_naive = _to_naive_utc(review_dt)
        if review_naive <= horizon_naive:
            out.append(d)
    return out


def query_sorted_by_review_at(doc, reverse=False):
    """Return decisions sorted by review_at.

    Ascending by default (due-soonest first); pass reverse=True for descending.
    Decisions with missing or malformed review_at sort to the END regardless of
    direction — graceful degradation so they don't crash the sort but don't
    distract the operator either.

    Implementation note: we partition into valid/invalid buckets and only sort
    the valid bucket, then append invalid. A single `sorted(..., key=...)` with
    a sentinel key doesn't work for both directions — `reverse=True` would flip
    the valid/invalid ordering too, moving invalids to the front.

    Wave 3 — Task 0.3.
    """
    valid = []
    invalid = []
    for d in doc.get("decisions", []):
        review_at = d.get("review_at")
        if not review_at:
            invalid.append(d)
            continue
        try:
            dt = _parse_iso(review_at)
        except (ValueError, TypeError, AttributeError):
            invalid.append(d)
            continue
        valid.append((_to_naive_utc(dt), d))

    valid.sort(key=lambda pair: pair[0], reverse=reverse)
    return [d for _, d in valid] + invalid


def heatmap_buckets(pre_mortem_items):
    """Aggregate pre-mortem items into a 25-cell 5x5 grid (likelihood x impact).

    Returns a dict keyed by (likelihood, impact) tuples in the range 1..5.
    Each value is the count of items at that cell. All 25 keys are always
    present (value 0 if no items there) — simplifies the downstream rendering
    code (JS heatmap widget in Wave 3 Task 5) because it can iterate the full
    grid without missing-key handling.

    Items with likelihood or impact outside [1, 5], with non-integer values,
    with boolean values, or with missing keys are silently dropped.

    This helper lives here alongside Wave 3 query helpers for bundling
    convenience. A future refactor could move it to tools/validator.py (which
    owns pre_mortem schema validation) or a dedicated tools/pre_mortem_analysis.py.

    The JS dashboard widget mirrors this logic — if they diverge, it's a bug.

    Wave 3 — Task 0.4.
    """
    buckets = {(l, i): 0 for l in range(1, 6) for i in range(1, 6)}
    for item in pre_mortem_items:
        l = item.get("likelihood")
        i = item.get("impact")
        # Reject booleans explicitly — isinstance(True, int) is True in Python.
        if isinstance(l, bool) or isinstance(i, bool):
            continue
        if not isinstance(l, int) or not isinstance(i, int):
            continue
        if 1 <= l <= 5 and 1 <= i <= 5:
            buckets[(l, i)] += 1
    return buckets
