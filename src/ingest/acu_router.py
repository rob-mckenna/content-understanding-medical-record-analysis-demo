"""Map a classifier label to the specialist analyzer that should extract it."""
from __future__ import annotations

CLASS_TO_ANALYZER: dict[str, str] = {
    "discharge-summary":         "healthcare-discharge-summary-v1",
    "consultation-note":         "healthcare-consultation-note-v1",
    "progress-note":             "healthcare-progress-note-v1",
    "cardiology-ecg":            "healthcare-cardiology-ecg-v1",
    "lab-results":               "healthcare-lab-results-v1",
    "immunizations":             "healthcare-immunizations-v1",
    "intake-output":             "healthcare-intake-output-v1",
    "medication-admin-record":   "healthcare-medication-admin-record-v1",
    "pmh-problems":              "healthcare-pmh-problems-v1",
    "orders-admit-transfer":     "healthcare-orders-admit-transfer-v1",
    "orders-laboratory":         "healthcare-orders-laboratory-v1",
    "orders-nursing":            "healthcare-orders-nursing-v1",
    "orders-medication":         "healthcare-orders-medication-v1",
    "orders-radiology":          "healthcare-orders-radiology-v1",
    "plan-of-care":              "healthcare-plan-of-care-v1",
}

REVIEW_LABELS = {"unknown-other"}
SKIP_LABELS = {"cover-separator"}


def analyzer_for(label: str) -> str | None:
    """Return the analyzer ID for a class label, or None if it should be skipped/reviewed."""
    if label in SKIP_LABELS:
        return None
    if label in REVIEW_LABELS:
        return None
    if label not in CLASS_TO_ANALYZER:
        raise KeyError(f"No analyzer mapped for classifier label '{label}'")
    return CLASS_TO_ANALYZER[label]
