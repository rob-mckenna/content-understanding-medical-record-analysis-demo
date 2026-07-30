"""Map a medication order to a FHIR MedicationRequest resource."""
from __future__ import annotations


STATUS_MAP = {
    "active":       "active",
    "continue":     "active",
    "new":          "active",
    "held":         "on-hold",
    "discontinued": "stopped",
    "completed":    "completed",
    "pending":      "draft",
    "changed":      "active",
}


def to_fhir(order: dict, *, patient_urn: str, encounter_urn: str | None = None) -> dict:
    med_cc: dict = {"text": order.get("medicationName") or order.get("brandName")}
    if order.get("rxNormCode"):
        med_cc["coding"] = [{"system": "http://www.nlm.nih.gov/research/umls/rxnorm", "code": order["rxNormCode"]}]

    resource = {
        "resourceType": "MedicationRequest",
        "status": STATUS_MAP.get(order.get("status", "active"), "active"),
        "intent": "order",
        "subject": {"reference": patient_urn},
        "medicationCodeableConcept": med_cc,
        "dosageInstruction": [{
            "text": " ".join(x for x in [
                order.get("dose"),
                order.get("doseUnit"),
                order.get("route"),
                order.get("frequency"),
            ] if x),
            "route": {"text": order.get("route")} if order.get("route") else None,
        }],
    }
    if encounter_urn:
        resource["encounter"] = {"reference": encounter_urn}
    if order.get("orderStartDateTime"):
        resource["authoredOn"] = order["orderStartDateTime"]
    return resource
