"""Map lab / vital / observation names to LOINC codes."""
from __future__ import annotations

from .types import CodedConcept


def to_loinc(test_name: str, *, specimen: str | None = None, unit: str | None = None) -> CodedConcept | None:
    # TODO: LOINC lookup (Text Analytics for Health / UMLS / local LOINC db).
    return None
