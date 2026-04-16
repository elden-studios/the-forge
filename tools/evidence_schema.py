"""Evidence object schema — dataclass, allowed-value enums, ID generator.

This module is the foundation for all evidence handling. Pure data, no I/O.
"""
from dataclasses import asdict, dataclass, field
from typing import List
import uuid


SOURCE_TYPES = frozenset({
    "primary_government",
    "primary_company",
    "analyst",
    "reputable_media",
    "user_reviews",
    "community",
    "blog",
    "unknown",  # default when no rule matches
})

SIGNAL_TAGS = frozenset({"FACT", "INFERENCE", "HYPOTHESIS", "OPINION"})


def new_evidence_id():
    """Generate a fresh evidence ID like 'ev-7f2a3c'."""
    return f"ev-{uuid.uuid4().hex[:6]}"


@dataclass
class Evidence:
    id: str
    claim: str
    source_url: str
    source_title: str
    source_type: str
    quality_score: int
    retrieved_at: str  # ISO 8601 UTC
    retrieved_by: List[str]
    queried_via: str
    excerpt: str
    confidence: float
    signal_tag: str

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)
