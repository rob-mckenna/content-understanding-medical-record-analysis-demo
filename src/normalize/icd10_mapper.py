"""Map free-text diagnoses to ICD-10-CM and SNOMED CT."""
from __future__ import annotations

from .types import CodedConcept


def to_icd10(text: str) -> CodedConcept | None:
    """Return the best ICD-10-CM match for a diagnosis string."""
    return None


def to_snomed(text: str) -> CodedConcept | None:
    """Return the best SNOMED CT match for a diagnosis string."""
    return None
