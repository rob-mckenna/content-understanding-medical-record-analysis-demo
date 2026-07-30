"""Map an ACU patient banner to a FHIR R4 Patient resource."""
from __future__ import annotations


def to_fhir(patient: dict, *, patient_urn: str) -> dict:
    identifiers = []
    for mrn in patient.get("mrn", []) or []:
        identifiers.append({
            "system": f"urn:facility:{(mrn.get('facility') or 'unknown').lower()}",
            "value": mrn.get("value"),
            "type": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "MR"}]
            },
        })
    if patient.get("accountNumber"):
        identifiers.append({
            "system": "urn:acct",
            "value": patient["accountNumber"],
            "type": {
                "coding": [{"system": "http://terminology.hl7.org/CodeSystem/v2-0203", "code": "AN"}]
            },
        })

    sex_map = {"M": "male", "F": "female", "U": "unknown", "Other": "other"}

    return {
        "resourceType": "Patient",
        "id": patient_urn,
        "identifier": identifiers,
        "name": [{"text": patient.get("patientName")}] if patient.get("patientName") else [],
        "birthDate": patient.get("dateOfBirth"),
        "gender": sex_map.get(patient.get("sex", ""), "unknown"),
    }
