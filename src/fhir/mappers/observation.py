"""Map lab / vital results to FHIR Observation resources."""
from __future__ import annotations


INTERPRETATION = {
    "normal":         {"code": "N", "display": "Normal"},
    "high":           {"code": "H", "display": "High"},
    "low":            {"code": "L", "display": "Low"},
    "critical-high":  {"code": "HH", "display": "Critical high"},
    "critical-low":   {"code": "LL", "display": "Critical low"},
    "abnormal":       {"code": "A", "display": "Abnormal"},
}


def lab_to_fhir(lab: dict, *, patient_urn: str, encounter_urn: str | None = None) -> dict:
    resource = {
        "resourceType": "Observation",
        "status": "final",
        "category": [{
            "coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]
        }],
        "subject": {"reference": patient_urn},
        "code": {
            "text": lab.get("testName"),
            "coding": [{"system": "http://loinc.org", "code": lab["loincCode"]}] if lab.get("loincCode") else [],
        },
    }
    if lab.get("resultValue") is not None:
        try:
            resource["valueQuantity"] = {
                "value": float(lab["resultValue"]),
                "unit": lab.get("resultUnit"),
                "system": "http://unitsofmeasure.org",
            }
        except (TypeError, ValueError):
            resource["valueString"] = str(lab["resultValue"])
    if lab.get("referenceRange"):
        resource["referenceRange"] = [{"text": lab["referenceRange"]}]
    if lab.get("abnormalFlag"):
        interp = INTERPRETATION.get(lab["abnormalFlag"])
        if interp:
            resource["interpretation"] = [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/v3-ObservationInterpretation",
                    **interp,
                }]
            }]
    if lab.get("collectionDateTime"):
        resource["effectiveDateTime"] = lab["collectionDateTime"]
    if encounter_urn:
        resource["encounter"] = {"reference": encounter_urn}
    return resource
