# Golden expected outputs

Populate this folder with JSON files that pair to sample PDFs:

- `<sample>.classifier.json` — expected classifier labels per page
- `<sample>.extraction.<doc-class>.json` — expected analyzer output
- `<sample>.bundle.json` — expected FHIR transaction bundle

Used by integration tests to detect analyzer regressions.
