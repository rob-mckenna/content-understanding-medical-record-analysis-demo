"""Map free-text medications to RxNorm codes.

Real implementation: call UMLS `/rest/search` on the RxNorm vocab, then verify
via `RxNorm REST /approximateTerm.json`. Fall back to Text Analytics for Health.
"""
from __future__ import annotations

from .types import CodedConcept


def to_rxnorm(text: str, *, dose: str | None = None, route: str | None = None) -> CodedConcept | None:
    """Return the best RxNorm match for `text`, or None if unresolved."""
    # TODO: real UMLS/RxNorm call.
    return None
