"""Union-find style patient matcher.

A single medical record may contain several MRNs (facility-specific) plus an
account number and FIN. This matcher unions any records that share at least
one identifier and yields a canonical `PatientKey` per person.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Identifier:
    system: str
    value: str


@dataclass
class PatientKey:
    canonical_id: str
    identifiers: set[Identifier] = field(default_factory=set)


class UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        while self.parent.get(x, x) != x:
            self.parent[x] = self.parent.get(self.parent[x], self.parent[x])
            x = self.parent[x]
        self.parent.setdefault(x, x)
        return x

    def union(self, a: str, b: str) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def group_by_patient(records: list[list[Identifier]]) -> dict[str, PatientKey]:
    """Group records that share any identifier into a canonical PatientKey.

    `records[i]` is the list of identifiers seen on the i-th extracted document.
    """
    uf = UnionFind()
    id_to_first: dict[Identifier, str] = {}

    for idx, ids in enumerate(records):
        rec_key = f"rec:{idx}"
        uf.find(rec_key)
        for ident in ids:
            k = f"id:{ident.system}:{ident.value}"
            uf.find(k)
            uf.union(rec_key, k)
            id_to_first.setdefault(ident, rec_key)

    groups: dict[str, PatientKey] = defaultdict(lambda: PatientKey(canonical_id=""))
    for ident in id_to_first:
        root = uf.find(f"id:{ident.system}:{ident.value}")
        pk = groups[root]
        if not pk.canonical_id:
            pk.canonical_id = root
        pk.identifiers.add(ident)

    return dict(groups)
