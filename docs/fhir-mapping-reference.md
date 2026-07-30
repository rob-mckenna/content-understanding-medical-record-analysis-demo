# FHIR Mapping Reference

Target: **FHIR R4** on **Azure Health Data Services**.

| ACU Extraction | FHIR Resource | Key Elements |
|---|---|---|
| Patient banner | `Patient` | `identifier[]`, `name`, `birthDate`, `gender`, `address` |
| Admit/discharge dates + location | `Encounter` | `period`, `class`, `location`, `participant`, `hospitalization.dischargeDisposition` |
| Discharge summary as a whole | `Composition` (type `LP173418-7`) | Sections reference the resources below |
| Diagnoses, problems list | `Condition` | `code` (ICD-10 / SNOMED), `clinicalStatus`, `verificationStatus`, `onset[x]` |
| Medication orders | `MedicationRequest` | `medicationCodeableConcept` (RxNorm), `dosageInstruction`, `requester` |
| MAR entries | `MedicationAdministration` | `effectiveDateTime`, `dosage`, `performer` |
| Lab results | `Observation` (category `laboratory`) + `DiagnosticReport` | `code` (LOINC), `valueQuantity`, `referenceRange`, `interpretation` |
| ECG panel | `Observation` panel (LOINC `11524-6`) with components | Rate, PR, QRS, QT, QTc, Axis |
| Imaging orders | `ServiceRequest` + `ImagingStudy` | `code`, `bodySite`, `reasonCode` |
| Immunizations | `Immunization` | `vaccineCode` (CVX), `occurrenceDateTime`, `lotNumber`, `site`, `route` |
| Vitals | `Observation` (category `vital-signs`) | Temp, HR, RR, BP, SpO2 with LOINC codes |
| Intake & Output | `Observation` (LOINC `9192-6` intake / `9187-6` output) | `valueQuantity`, `effectivePeriod` |
| Plan of Care | `CarePlan` + `Goal` | `activity`, `goal`, `author` |
| Consultation note | `DocumentReference` + linked `Condition` / `ClinicalImpression` | `type` LOINC `11488-4` |
| Provenance / signatures | `Provenance` | `agent`, `recorded`, `signature` |

## Bundle strategy

- One **`Bundle` (type: `transaction`)** per encounter.
- `Patient` first, then `Encounter`, then clinical resources, referencing the
  in-bundle URNs (`urn:uuid:…`).
- Use conditional create (`ifNoneExist`) on `Patient` keyed by MRN to prevent
  duplicates when the same patient appears in multiple files.

## Identifier strategy

- `Patient.identifier` includes every MRN as a separate entry with
  `system` = facility URI.
- `Encounter.identifier` = source account number + facility.
- Extraction confidence and source page/bbox are attached via
  `meta.tag` and a companion `Provenance` resource.

## Terminology bindings

| Domain | Preferred code system |
|---|---|
| Diagnoses | ICD-10-CM, SNOMED CT |
| Medications | RxNorm |
| Labs, vitals | LOINC |
| Procedures | CPT, SNOMED CT |
| Immunizations | CVX |
| Route, site | SNOMED CT |
| Units | UCUM |

Normalization details: see `src/normalize/`.
