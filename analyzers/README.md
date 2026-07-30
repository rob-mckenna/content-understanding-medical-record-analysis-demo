# Analyzers

One classifier + one analyzer per document class. The classifier routes each
page (or contiguous run) to the correct analyzer.

| File | Purpose |
|---|---|
| `classifier-document-router.json` | 15-way multiclass classifier + cover/unknown |
| `discharge-summary.json` | Full production-shape analyzer (reference example) |
| `consultation-note.json` | Consultation note stub |
| `progress-note.json` | Progress / SOAP note stub |
| `cardiology-ecg.json` | ECG + cardiology report stub |
| `lab-results.json` | CBC / chemistry / POC panels stub |
| `immunizations.json` | Immunization record stub |
| `intake-output.json` | I/O flowsheet stub |
| `medication-admin-record.json` | MAR stub |
| `pmh-problems.json` | PMH / problems list stub |
| `orders-admit-transfer.json` | Admit/Transfer/Discharge order stub |
| `orders-laboratory.json` | Lab order stub |
| `orders-nursing.json` | Nursing order stub |
| `orders-medication.json` | Medication order stub |
| `orders-radiology.json` | Radiology order stub |
| `plan-of-care.json` | Plan of care stub |

Each stub follows the same shape as `discharge-summary.json`. Flesh out the
`fieldSchema` per class per the fields listed in the top-level README and
`docs/analyzer-authoring-guide.md`.

## Register all

```powershell
./register-all.ps1 -AcuEndpoint https://<your-acu>.cognitiveservices.azure.com
```
