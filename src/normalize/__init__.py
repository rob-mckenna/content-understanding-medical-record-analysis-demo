"""Normalize free-text medical concepts to standard code systems.

Each mapper accepts free-text plus optional context and returns a
`CodedConcept` with the top match + alternates + confidence. Real
implementations back onto UMLS + Text Analytics for Health.
"""
