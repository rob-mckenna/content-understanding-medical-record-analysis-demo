# Analyzer Authoring Guide

Every specialist analyzer follows the same template:

1. **`baseAnalyzerId`** = `prebuilt-documentAnalyzer`.
2. **`config`**:
   - `enableOcr: true`
   - `enableLayout: true`
   - `enableGrounding: true`
   - `estimateFieldSourceAndConfidence: true`
   - `returnDetails: true`
3. **`fieldSchema`** — strict, typed, small.

## Field method choice

| Method | When to use |
|---|---|
| `extract` | Copy-verbatim values (names, IDs, dates, dose text). |
| `classify` | Value drawn from a fixed enum (status, route, disposition). |
| `generate` | Short natural-language summaries (hospital course, indication). |

Prefer `extract` + `classify` over `generate`. Generative fields are harder to
evaluate and more expensive.

## Shared patient banner

Every document class starts with the same demographics block. Keep it
consistent by copying the `patient` and `encounter` field definitions from
`analyzers/discharge-summary.json`. In a future iteration, factor it out via
`$ref`.

## Multi-MRN handling

MRN is always modeled as an array of `{ value, facility }` objects — the
sample record shows patients with three MRNs across systems.

## Abnormal-value flags

Labs must extract `abnormalFlag` as a classified enum
(`normal | high | low | critical-high | critical-low | abnormal`). ACU's
multimodal mode picks up color cues and parenthetical markers like `(H)` and
`(O)`; cross-check numerically against `referenceRange` in normalize step.

## Confidence thresholds

Default gate: **auto-accept ≥ 0.90, human-review 0.60–0.90, reject < 0.60**.
Tune per field family (dates typically need lower gates than free-text).

## Adding a new analyzer

1. Copy `analyzers/_template.json` (create by cloning `discharge-summary.json`
   and stripping domain fields).
2. Update `analyzerId`, `description`, and `fieldSchema.name`.
3. Add the class label to `classifier-document-router.json`.
4. Register the analyzer:
   ```powershell
   ./register-all.ps1 -AcuEndpoint <endpoint> -Analyzer new-analyzer.json
   ```
5. Add unit tests under `tests/unit/analyzers/`.
6. Add a golden expected JSON under `samples/expected/`.

## Versioning

Include a version suffix in `analyzerId` (`-v1`, `-v2`). Never mutate an
existing analyzer in place; publish a new version and update the router.
