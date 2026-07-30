"""Shared types for coded-value normalization."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class CodedConcept:
    system: str
    code: str
    display: str
    confidence: float
    alternates: list["CodedConcept"] = field(default_factory=list)
