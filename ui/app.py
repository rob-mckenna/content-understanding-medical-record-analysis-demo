"""Streamlit demo UI.

Run locally:
    streamlit run ui/app.py

Shows: PDF upload -> classifier heatmap -> extraction preview -> FHIR bundle.
Wire the actual ACU + FHIR calls into `src/` and import them here.
"""
from __future__ import annotations

import streamlit as st

st.set_page_config(page_title="Medical Record Analysis Demo", layout="wide")
st.title("Medical Record Analysis Demo")
st.caption("Azure Content Understanding + FHIR reference pipeline")

uploaded = st.file_uploader("Upload a medical record PDF", type=["pdf"])
if uploaded is None:
    st.info("Upload a synthetic medical record PDF to begin.")
    st.stop()

st.success(f"Received: {uploaded.name} ({uploaded.size:,} bytes)")

with st.expander("1. Classify pages", expanded=True):
    st.write("Wire in `AcuClient.classify_pages(...)` here.")

with st.expander("2. Extract per document class"):
    st.write("Wire in `AcuClient.extract(...)` for each logical document.")

with st.expander("3. FHIR bundle preview"):
    st.write("Wire in `src.fhir.bundle_builder.build_bundle(...)` here.")

with st.expander("4. Human review queue"):
    st.write("Wire in `src.review.human_queue.ReviewQueue` here.")
