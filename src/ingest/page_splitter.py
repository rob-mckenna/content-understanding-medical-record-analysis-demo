"""Split a multi-document PDF into logical documents.

The splitter uses ACU's prebuilt-layout output to detect **patient-banner
boundaries** and per-page classifier labels. A logical document is any
contiguous run of pages with the same classifier label AND the same patient
banner.

Public API:

    split_pdf(pdf_bytes, layout_result, classifier_result) -> list[LogicalDocument]
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass(frozen=True)
class PatientBanner:
    """Minimum fingerprint of a patient banner block on a page."""
    patient_name: str | None
    mrn_values: tuple[str, ...]
    account_number: str | None
    facility_name: str | None

    def matches(self, other: "PatientBanner") -> bool:
        # Two banners are the "same patient" if any MRN matches AND names agree.
        if not self.mrn_values or not other.mrn_values:
            return False
        if not set(self.mrn_values) & set(other.mrn_values):
            return False
        if self.patient_name and other.patient_name and self.patient_name != other.patient_name:
            return False
        return True


@dataclass
class LogicalDocument:
    document_class: str
    start_page: int
    end_page: int  # inclusive
    banner: PatientBanner
    classifier_confidence: float
    page_confidences: list[float] = field(default_factory=list)


def _extract_banner(layout_page: dict) -> PatientBanner:
    """Extract a banner fingerprint from a page-level layout dict.

    The real implementation parses ACU's layout `keyValuePairs` for the fields
    NAME, MRN, Acct #, Facility. This scaffold is a placeholder.
    """
    return PatientBanner(
        patient_name=None,
        mrn_values=tuple(),
        account_number=None,
        facility_name=None,
    )


def split_pdf(
    *,
    layout_pages: list[dict],
    classifier_labels: list[tuple[str, float]],
) -> list[LogicalDocument]:
    """Merge contiguous same-class pages that share a patient banner.

    Args:
        layout_pages: One dict per PDF page, from ACU prebuilt-layout.
        classifier_labels: `(label, confidence)` per page, from the classifier.

    Returns:
        A list of `LogicalDocument` runs. Runs never cross patient boundaries.
    """
    if len(layout_pages) != len(classifier_labels):
        raise ValueError("layout_pages and classifier_labels length mismatch")

    docs: list[LogicalDocument] = []
    current: LogicalDocument | None = None

    for idx, (page, (label, conf)) in enumerate(zip(layout_pages, classifier_labels)):
        banner = _extract_banner(page)

        if label in {"cover-separator"}:
            # Flush any open document; skip separator pages.
            if current is not None:
                docs.append(current)
                current = None
            continue

        if current is None:
            current = LogicalDocument(
                document_class=label,
                start_page=idx,
                end_page=idx,
                banner=banner,
                classifier_confidence=conf,
                page_confidences=[conf],
            )
            continue

        same_class = label == current.document_class
        same_patient = banner.matches(current.banner)

        if same_class and same_patient:
            current.end_page = idx
            current.page_confidences.append(conf)
            current.classifier_confidence = min(current.classifier_confidence, conf)
        else:
            docs.append(current)
            current = LogicalDocument(
                document_class=label,
                start_page=idx,
                end_page=idx,
                banner=banner,
                classifier_confidence=conf,
                page_confidences=[conf],
            )

    if current is not None:
        docs.append(current)

    return docs


def summarize(docs: Iterable[LogicalDocument]) -> dict:
    """Return a small summary suitable for logging (no PHI)."""
    docs = list(docs)
    return {
        "logical_document_count": len(docs),
        "class_counts": {
            cls: sum(1 for d in docs if d.document_class == cls)
            for cls in {d.document_class for d in docs}
        },
        "low_confidence_docs": [
            {"class": d.document_class, "start_page": d.start_page, "end_page": d.end_page}
            for d in docs
            if d.classifier_confidence < 0.75
        ],
    }
