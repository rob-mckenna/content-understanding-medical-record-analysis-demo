# Content Understanding — Medical Record Analysis Demo

Reference architecture for processing large, mixed-format medical records with
**Azure Content Understanding (ACU)**, **Azure AI Foundry**, and **FHIR** on
**Azure Health Data Services (AHDS)**.

> This repo is a **reference architecture and scaffold**, not a production
> product. It shows how to structure analyzers, orchestration, code
> normalization, FHIR mapping, and human-in-the-loop review for large medical
> records at scale.

---

## Why this exists

Traditional OCR and Document Intelligence struggle with real medical records
because a single PDF typically contains:

- 15+ heterogeneous document classes (discharge summaries, consults, ECGs,
  progress notes, labs, immunizations, MAR, orders, care plans, PMH, etc.)
- Semi-structured layouts that shift page-to-page
- Repeating patient headers — sometimes for **different** patients within the
  same file
- Abnormal-value flags encoded as color or parenthetical hints (`(H)`, `(L)`,
  orange text) that layout-only models discard
- Merged/wrapped tables (CBC, chemistry panels, I/O flowsheets)
- Signature and attestation blocks that break reading order
- Volumes of 100–1000+ pages per record

The design here handles those problems with a **classifier-routed, schema-driven,
grounded** pipeline.

---

## Architecture

```
                         ┌───────────────────────────────────┐
     PDF (N pages) ─────▶│  Page Splitter + Prebuilt-Layout  │
                         └────────────────┬──────────────────┘
                                          │
                              ┌───────────▼────────────┐
                              │  ACU Classifier        │  15-way, multimodal
                              └───────────┬────────────┘
                                          │
      ┌────────────┬────────────┬─────────┼─────────┬────────────┬────────────┐
      ▼            ▼            ▼         ▼         ▼            ▼            ▼
   Discharge   Consult      Progress    Labs    Meds/MAR    Imaging     Immunizations
   Analyzer    Analyzer     Analyzer   Analyzer  Analyzer   Analyzer     Analyzer
      │            │            │         │         │            │            │
      └────────────┴────────────┴─────────┼─────────┴────────────┴────────────┘
                                          ▼
                              ┌────────────────────────┐
                              │  Aggregator (Functions)│  dedupe, patient match
                              └───────────┬────────────┘
                                          ▼
                              ┌────────────────────────┐
                              │  Normalize (RxNorm,    │  UMLS / Text Analytics
                              │  LOINC, ICD-10, CPT)   │  for Health
                              └───────────┬────────────┘
                                          ▼
                              ┌────────────────────────┐
                              │  FHIR Mapper           │
                              └───────────┬────────────┘
                                          ▼
                              ┌────────────────────────┐
                              │  Azure Health Data     │
                              │  Services — FHIR R4    │
                              └────────────────────────┘

     Low-confidence fields ─▶ Human Review Queue (Cosmos DB) ─▶ approval UI
```

Full architecture details: [`docs/architecture.md`](docs/architecture.md).

---

## Repository layout

```
.
├── analyzers/          ACU classifier + one analyzer per document class
├── docs/               Architecture, analyzer authoring, FHIR mapping, OCR playbook
├── infra/              Bicep for ACU, Storage, Functions, AHDS FHIR, Key Vault
├── notebooks/          End-to-end demo notebooks (classify → extract → FHIR)
├── samples/            Placeholder for sample PDFs (do not commit PHI)
├── src/
│   ├── ingest/         Blob-trigger Function, page splitter, classifier router
│   ├── extract/        ACU client (async, retry, throttling)
│   ├── normalize/      Code mappers (RxNorm/LOINC/ICD-10) + date repair
│   ├── aggregate/      Multi-MRN patient matcher, deduplication
│   ├── fhir/           FHIR R4 mappers + bundle builder + AHDS client
│   └── review/         Human-in-the-loop queue (Cosmos DB)
├── tests/              Unit + integration tests
├── ui/                 Optional Streamlit demo UI
└── .github/workflows/  CI + deploy
```

---

## Document classes handled

| # | Class | Primary FHIR Anchor |
|---|---|---|
| 1 | Discharge Summary | `Composition`, `Encounter` |
| 2 | Consultation Note | `DocumentReference`, `Condition` |
| 3 | Cardiology / ECG Report | `Observation` (ECG panel), `DiagnosticReport` |
| 4 | Progress Note | `Observation`, `ClinicalImpression` |
| 5 | Laboratory Results | `Observation`, `DiagnosticReport` |
| 6 | Immunizations | `Immunization` |
| 7 | Intake & Output Flowsheet | `Observation` (fluid balance) |
| 8 | Medication Administration Record | `MedicationAdministration` |
| 9 | Past Medical History / Problems | `Condition` |
| 10 | Orders — Admit/Transfer/Discharge | `ServiceRequest`, `Encounter` |
| 11 | Orders — Laboratory | `ServiceRequest` (lab) |
| 12 | Orders — Nursing | `ServiceRequest` (nursing) |
| 13 | Orders — Medications | `MedicationRequest` |
| 14 | Orders — Radiology | `ServiceRequest`, `ImagingStudy` |
| 15 | Plan of Care | `CarePlan`, `Goal` |

---

## Quickstart

```powershell
# 1. Configure Azure
az login
az account set --subscription <SUB_ID>

# 2. Deploy infrastructure
cd infra
az deployment sub create --location eastus2 --template-file main.bicep `
  --parameters envName=demo-dev

# 3. Register analyzers
cd ../analyzers
./register-all.ps1 -AcuEndpoint https://<your-acu>.cognitiveservices.azure.com

# 4. Drop a PDF in the input container and watch it flow
az storage blob upload --container-name input `
  --file ./samples/sample-medical-record.pdf `
  --account-name <storage-account>
```

Detailed setup: [`docs/architecture.md`](docs/architecture.md).

---

## Key design principles

- **One analyzer per document class** — tight schemas, predictable cost.
- **Grounding always on** — every field carries page + bounding box provenance.
- **Confidence-gated auto-processing** — anything below threshold routes to
  human review before touching FHIR.
- **Post-extraction code normalization** — free-text → RxNorm / LOINC / ICD-10 /
  CPT / SNOMED using UMLS + Text Analytics for Health.
- **Patient-boundary aware chunking** — a single 300-page PDF may contain
  multiple patients; splitter respects that.
- **No PHI in logs** — only IDs, confidences, and structural counts.

---

## Data handling

- **No PHI is committed to this repository.** The `samples/` folder is a
  placeholder — synthetic or de-identified test data only.
- All Azure resources deployed by `infra/` are configured with private
  networking placeholders, customer-managed key support, and diagnostic
  logging to a dedicated Log Analytics workspace.
- FHIR service uses Azure AD auth and role-based access; SMART on FHIR is
  optional and documented.

---

## Status

Reference scaffold. Analyzer JSON, mappers, and notebooks are illustrative and
require validation against a real ACU deployment before production use.

## License

MIT — see [LICENSE](LICENSE).
