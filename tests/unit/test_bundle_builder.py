from src.fhir.bundle_builder import build_bundle


def test_bundle_shape():
    aggregated = {
        "patient": {
            "patientName": "Test, Patient A",
            "dateOfBirth": "1955-06-01",
            "sex": "M",
            "mrn": [{"value": "MRN-1", "facility": "General"}],
        },
        "encounter": {"admitDateTime": "2026-01-01", "dischargeDateTime": "2026-01-05"},
        "diagnoses": [{"diagnosisText": "Pneumonia", "icd10Code": "J18.9", "status": "active"}],
        "medications": [{"medicationName": "amoxicillin", "dose": "500", "doseUnit": "mg", "route": "PO", "status": "new"}],
        "labs": [{"testName": "Sodium", "resultValue": "138", "resultUnit": "mmol/L", "abnormalFlag": "normal"}],
        "immunizations": [{"vaccineName": "Influenza", "cvxCode": "141", "dateGiven": "2026-01-04"}],
    }
    bundle = build_bundle(aggregated)
    assert bundle["resourceType"] == "Bundle"
    assert bundle["type"] == "transaction"
    resource_types = [e["resource"]["resourceType"] for e in bundle["entry"]]
    for rt in ["Patient", "Encounter", "Condition", "MedicationRequest", "Observation", "Immunization"]:
        assert rt in resource_types
