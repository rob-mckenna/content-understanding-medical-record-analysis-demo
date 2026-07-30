"""Map a diagnosis / problem entry to a FHIR Condition resource."""
from __future__ import annotations


CLINICAL_STATUS = {
    "active":    "active",
    "chronic":   "active",
    "recurrent": "recurrence",
    "resolved":  "resolved",
    "unknown":   "unknown",
}


def to_fhir(dx: dict, *, patient_urn: str, encounter_urn: str | None = None) -> dict:
    code = {"text": dx.get("diagnosisText")}
    codings = []
    if dx.get("icd10Code"):
        codings.append({"system": "http://hl7.org/fhir/sid/icd-10-cm", "code": dx["icd10Code"]})
    if dx.get("snomedCode"):
        codings.append({"system": "http://snomed.info/sct", "code": dx["snomedCode"]})
    if codings:
        code["coding"] = codings

    resource = {
        "resourceType": "Condition",
        "subject": {"reference": patient_urn},
        "code": code,
        "clinicalStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                "code": CLINICAL_STATUS.get(dx.get("status", "unknown"), "unknown"),
            }]
        },
        "verificationStatus": {
            "coding": [{
                "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                "code": "confirmed",
            }]
        },
    }
    if encounter_urn:
        resource["encounter"] = {"reference": encounter_urn}
    if dx.get("onsetDate"):
        resource["onsetDateTime"] = dx["onsetDate"]
    return resource
