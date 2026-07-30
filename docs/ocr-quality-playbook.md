# OCR Quality Playbook

Medical records amplify every OCR failure mode. Bake these mitigations in from
day one — retro-fitting them is expensive.

## Failure catalog

| # | Failure | Signal | Mitigation |
|---|---|---|---|
| 1 | Invalid dates (e.g. `6/78/0047`) | Regex fails, month/day out of range | `normalize/date_repair.py` — accept, flag, ask reviewer. Never silently coerce. |
| 2 | Split words across columns | Whitespace mid-token, dictionary miss | Reading-order reconstruction from ACU layout; validate against medical dictionary. |
| 3 | Abnormal-value color flags lost | Numeric value out of range but no `H`/`L` | Multimodal ACU + cross-check numeric vs `referenceRange` in post-processing. |
| 4 | Merged / wrapped table headers | Column count mismatch across rows | Table-repair post-step snaps values to nearest header by pixel x-coordinate. |
| 5 | Placeholder images ("DUMMY IMAGE", logos) | Repeated bounding boxes with OCR gibberish | Classifier ignore-list; strip during pre-processing. |
| 6 | Multi-MRN patients | Multiple MRNs in the header | Model as `array<{value, facility}>`; matcher unions them. |
| 7 | Patient switches mid-file | New banner detected | Splitter emits a new logical document at every banner boundary. |
| 8 | Signature blocks polluting narrative | Italic + "Electronically Signed" | Detect + extract as `Provenance`; strip from narrative. |
| 9 | Low OCR confidence on scanned pages | ACU confidence < threshold | Re-run through Document Intelligence Read v4 at higher DPI; fall back to human review. |
| 10 | Handwritten annotations | Handwriting present | Route to human queue; DI handwriting model as secondary. |
| 11 | Duplicated stapled pages | Same content, offset scan | Perceptual hash dedupe in splitter. |
| 12 | Rotated / skewed pages | Layout confidence low | Auto-deskew before ACU call. |
| 13 | Redaction bars misread as text | Solid blocks with OCR noise | Detect and mask before extraction. |

## Confidence gates (defaults)

| Field family | Auto-accept | Review | Reject |
|---|---|---|---|
| Patient name, MRN | ≥ 0.95 | 0.75–0.95 | < 0.75 |
| Dates | ≥ 0.90 | 0.60–0.90 | < 0.60 |
| Diagnoses (before code map) | ≥ 0.85 | 0.55–0.85 | < 0.55 |
| Medications | ≥ 0.90 | 0.65–0.90 | < 0.65 |
| Lab values | ≥ 0.90 | 0.70–0.90 | < 0.70 |
| Free-text summaries | never auto — always review sample-based | | |

## Human review queue

Anything below the auto-accept gate lands in Cosmos DB (`review-queue`
container) with:

- Extracted value + confidence
- Page number, bounding box, cropped image URL
- Suggested alternates (top-N)
- Reviewer verdict (accept / edit / reject)

Approved corrections feed a fine-tuning dataset for future classifier /
analyzer refinements.

## PHI safety in logs

- Log **field IDs and confidences only**. Never log values.
- Cropped images used for review are stored in a dedicated container with
  short TTL + private endpoint + CMK.
- App Insights sampling excludes any custom property named `phi.*`.
