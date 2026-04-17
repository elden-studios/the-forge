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
