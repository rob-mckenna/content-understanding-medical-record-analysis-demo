# Notebooks

Four end-to-end walkthroughs. Each notebook is a `.py`-style scaffold — open
in VS Code or Jupyter and add cells as you wire in real ACU credentials.

| Notebook | Purpose |
|---|---|
| `01-classify-sample.ipynb`  | Run the classifier on a sample PDF and visualize per-page labels + confidences. |
| `02-extract-discharge.ipynb`| End-to-end extraction on a discharge summary; show grounding overlays. |
| `03-fhir-bundle-demo.ipynb` | Combine extracts into a FHIR bundle and POST to AHDS. |
| `04-confidence-analysis.ipynb` | Confidence distribution + human-review rate analysis. |

For the customer demo:

1. `01` — show the router in action on a 300-page PDF.
2. `02` — zoom into one discharge summary; overlay bounding boxes.
3. `03` — build a FHIR bundle, POST to AHDS, then query it back.
4. `04` — dashboard the per-field confidence distribution.
