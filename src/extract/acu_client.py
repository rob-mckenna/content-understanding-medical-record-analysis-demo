"""Async client wrapper around Azure Content Understanding.

Real usage should use `azure-ai-contentunderstanding` when GA, or the raw REST
API. This scaffold shows the intended shape only.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass


@dataclass
class AcuClient:
    endpoint: str
    classifier_id: str
    api_version: str = "2025-11-01"
    max_concurrency: int = 8

    def __post_init__(self) -> None:
        self._sem = asyncio.Semaphore(self.max_concurrency)

    async def layout(self, pdf_bytes: bytes) -> list[dict]:
        """Run prebuilt layout; return one page dict per PDF page."""
        async with self._sem:
            # TODO: call ACU layout endpoint, poll for result, return pages.
            return []

    async def classify_pages(self, pdf_bytes: bytes) -> list[tuple[str, float]]:
        """Return one (label, confidence) tuple per page."""
        async with self._sem:
            # TODO: call classifier with a rolling page window.
            return []

    async def extract(
        self,
        pdf_bytes: bytes,
        *,
        analyzer_id: str,
        page_range: tuple[int, int],
    ) -> dict:
        """Extract fields for one logical document."""
        async with self._sem:
            # TODO: call analyzer, poll, return grounded field dict.
            return {"analyzerId": analyzer_id, "pageRange": page_range, "fields": {}}
