"""Blob-trigger Azure Function entry point.

Orchestrates the end-to-end flow for a single PDF:

    blob upload -> layout -> classify -> split -> extract -> normalize
        -> aggregate -> map to FHIR -> POST to AHDS

This scaffold only shows the shape; wire up bindings in `function.json`
alongside this file when you scaffold the actual Function App.
"""
from __future__ import annotations

import logging
import os
from dataclasses import asdict

from src.extract.acu_client import AcuClient
from src.ingest.acu_router import analyzer_for
from src.ingest.page_splitter import split_pdf, summarize

log = logging.getLogger(__name__)


async def process_pdf(pdf_bytes: bytes, *, blob_name: str) -> dict:
    """End-to-end orchestration for one PDF.

    Returns a small non-PHI summary suitable for logging. All extracted content
    is streamed to the output container / FHIR service, not returned in the log.
    """
    acu = AcuClient(
        endpoint=os.environ["ACU_ENDPOINT"],
        classifier_id="medical-record-document-router-v1",
    )

    layout_pages = await acu.layout(pdf_bytes)
    classifier_labels = await acu.classify_pages(pdf_bytes)

    docs = split_pdf(layout_pages=layout_pages, classifier_labels=classifier_labels)
    log.info(
        "Split PDF %s into logical documents: %s",
        blob_name,
        summarize(docs),
    )

    for doc in docs:
        analyzer_id = analyzer_for(doc.document_class)
        if analyzer_id is None:
            log.info(
                "Routing pages %d-%d to review (label=%s)",
                doc.start_page, doc.end_page, doc.document_class,
            )
            continue
        # Real implementation would slice pdf_bytes to just those pages and call ACU.
        _ = await acu.extract(pdf_bytes, analyzer_id=analyzer_id, page_range=(doc.start_page, doc.end_page))

    return summarize(docs)
