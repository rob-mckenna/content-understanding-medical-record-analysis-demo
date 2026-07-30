"""Map immunization entries to FHIR Immunization resources."""
from __future__ import annotations


def to_fhir(imm: dict, *, patient_urn: str, encounter_urn: str | None = None) -> dict:
    resource = {
        "resourceType": "Immunization",
        "status": "completed",
        "patient": {"reference": patient_urn},
        "vaccineCode": {
            "text": imm.get("vaccineName"),
            "coding": [{"system": "http://hl7.org/fhir/sid/cvx", "code": imm["cvxCode"]}] if imm.get("cvxCode") else [],
        },
        "occurrenceDateTime": imm.get("dateGiven"),
        "lotNumber": imm.get("lotNumber"),
        "expirationDate": imm.get("expirationDate"),
        "route": {"text": imm.get("route")} if imm.get("route") else None,
        "site": {"text": imm.get("site")} if imm.get("site") else None,
        "manufacturer": {"display": imm["manufacturer"]} if imm.get("manufacturer") else None,
    }
    if encounter_urn:
        resource["encounter"] = {"reference": encounter_urn}
    return {k: v for k, v in resource.items() if v not in (None, {}, [])}
