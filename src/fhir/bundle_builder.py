"""Build a FHIR Bundle (transaction) per encounter from an aggregated extraction."""
from __future__ import annotations

import uuid

from .mappers import condition, immunization, medication_request, observation, patient


def _entry(urn: str, resource: dict, url: str) -> dict:
    return {
        "fullUrl": urn,
        "resource": resource,
        "request": {"method": "POST", "url": url},
    }


def build_bundle(aggregated: dict) -> dict:
    """Turn an aggregated `(patient, encounter, extractions)` dict into a Bundle."""
    patient_urn = f"urn:uuid:{uuid.uuid4()}"
    encounter_urn = f"urn:uuid:{uuid.uuid4()}"

    entries: list[dict] = []
    pt_resource = patient.to_fhir(aggregated.get("patient", {}), patient_urn=patient_urn)
    entries.append(_entry(patient_urn, pt_resource, "Patient"))

    enc = aggregated.get("encounter", {})
    encounter_resource = {
        "resourceType": "Encounter",
        "status": "finished",
        "class": {"system": "http://terminology.hl7.org/CodeSystem/v3-ActCode", "code": "IMP"},
        "subject": {"reference": patient_urn},
        "period": {
            "start": enc.get("admitDateTime"),
            "end": enc.get("dischargeDateTime"),
        },
    }
    entries.append(_entry(encounter_urn, encounter_resource, "Encounter"))

    for dx in aggregated.get("diagnoses", []) or []:
        entries.append(_entry(
            f"urn:uuid:{uuid.uuid4()}",
            condition.to_fhir(dx, patient_urn=patient_urn, encounter_urn=encounter_urn),
            "Condition",
        ))
    for mr in aggregated.get("medications", []) or []:
        entries.append(_entry(
            f"urn:uuid:{uuid.uuid4()}",
            medication_request.to_fhir(mr, patient_urn=patient_urn, encounter_urn=encounter_urn),
            "MedicationRequest",
        ))
    for lab in aggregated.get("labs", []) or []:
        entries.append(_entry(
            f"urn:uuid:{uuid.uuid4()}",
            observation.lab_to_fhir(lab, patient_urn=patient_urn, encounter_urn=encounter_urn),
            "Observation",
        ))
    for imm in aggregated.get("immunizations", []) or []:
        entries.append(_entry(
            f"urn:uuid:{uuid.uuid4()}",
            immunization.to_fhir(imm, patient_urn=patient_urn, encounter_urn=encounter_urn),
            "Immunization",
        ))

    return {
        "resourceType": "Bundle",
        "type": "transaction",
        "entry": entries,
    }
