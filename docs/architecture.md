# Architecture

## Goals

Process large (100–1000+ page) medical records at scale by combining:

- **Azure Content Understanding (ACU)** for classification + grounded extraction
- **Azure AI Foundry** for evaluation, prompt-flow orchestration, and monitoring
- **Azure Health Data Services (AHDS) FHIR** as the canonical destination
- **Text Analytics for Health / UMLS** for coded-value normalization

## High-level flow

1. **Ingest** — PDF lands in `input` blob container. Blob-trigger Function starts.
2. **Split** — `page_splitter.py` produces per-page images + OCR text via ACU's
   prebuilt layout model. It also detects **patient banner boundaries** so a
   single file can hold multiple patients.
3. **Classify** — ACU classifier assigns each page (or contiguous run) to one of
   15 document classes (or `unknown/other`).
4. **Extract** — The router calls the matching specialist analyzer. Each
   analyzer produces a strict schema output with grounding (page + bounding box)
   and per-field confidence.
5. **Normalize** — Free-text drugs → RxNorm, labs → LOINC, diagnoses → ICD-10 /
   SNOMED, procedures → CPT. Dates are validated and repaired.
6. **Aggregate** — Group by `(mrn, encounter)`; resolve multi-MRN identities;
   deduplicate.
7. **Map to FHIR** — Build a `Bundle` per encounter; POST to AHDS FHIR service.
8. **Review** — Any field below confidence threshold routes to Cosmos DB review
   queue, surfaced by an optional Streamlit UI. Approved edits promote to FHIR.

## Component list

| Component | Azure Service |
|---|---|
| Blob input, output, quarantine | Storage Account (ADLS Gen2) |
| Orchestration | Azure Functions (Python, Flex Consumption) |
| Extraction | Azure Content Understanding |
| Evaluation, prompt-flow, monitoring | Azure AI Foundry |
| FHIR persistence | Azure Health Data Services — FHIR service |
| Code lookup | UMLS API + Text Analytics for Health |
| Human review queue | Cosmos DB (NoSQL) |
| Secrets | Key Vault |
| Observability | Log Analytics + App Insights |
| Optional demo UI | Container Apps (Streamlit) |

## Security posture

- Managed identity end-to-end; no keys in code.
- Private endpoints for Storage, ACU, FHIR, Cosmos DB, Key Vault.
- Customer-managed key (CMK) support flagged in Bicep parameters.
- Diagnostic settings on every resource → central Log Analytics.
- PHI never logged — only IDs, confidences, and structural counters.
- FHIR service uses Azure AD OAuth; SMART on FHIR launch documented separately.

## Scaling notes

- Functions scale on blob-trigger; ACU calls are gated by a semaphore in
  `acu_client.py` to respect account-level TPS.
- Splitter emits per-document messages to a Service Bus topic; specialist
  analyzers subscribe by document class for independent scale.
- Aggregator waits on completion of all documents for an encounter before
  emitting the FHIR bundle (correlation by `mrn + encounter_id`).

## Cost model

Rough envelope (validate with your rates):

| Item | Unit cost driver |
|---|---|
| ACU classification | pages processed |
| ACU extraction | documents (chunks) processed |
| Functions | GB-seconds |
| FHIR service | RU/s + storage |
| Log Analytics | GB ingested |
| Cosmos DB | RU/s |

Target: **< $X per 1,000 pages** end-to-end. A spreadsheet template lives at
`docs/cost-model.xlsx` (populate with your negotiated rates).

## Deployment topology

Single-region hub with private endpoints in a spoke VNet. Multi-region DR is
out of scope for this scaffold but the Bicep is structured to be
region-parameterized.
