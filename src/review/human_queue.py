"""Route low-confidence fields to Cosmos DB for human review."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReviewItem:
    id: str
    document_class: str
    field_path: str
    value: Any
    confidence: float
    page_number: int
    bbox: tuple[float, float, float, float] | None
    crop_url: str | None
    alternates: list[dict] = field(default_factory=list)
    status: str = "pending"  # pending / accepted / edited / rejected


def needs_review(confidence: float, *, gate: float = 0.9) -> bool:
    return confidence < gate


class ReviewQueue:
    def __init__(self, cosmos_conn_str: str, database: str = "review", container: str = "queue") -> None:
        self.cosmos_conn_str = cosmos_conn_str
        self.database = database
        self.container = container

    async def enqueue(self, item: ReviewItem) -> None:
        # TODO: azure-cosmos client insert.
        pass

    async def resolve(self, item_id: str, verdict: str, edited_value: Any | None = None) -> None:
        # TODO: patch status; write back to FHIR pipeline.
        pass
