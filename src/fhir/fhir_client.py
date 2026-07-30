"""Thin wrapper around Azure Health Data Services FHIR service."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FhirClient:
    base_url: str  # e.g. https://<workspace>-<service>.fhir.azurehealthcareapis.com

    async def submit_bundle(self, bundle: dict) -> dict:
        """POST a transaction Bundle. Uses Azure AD auth via DefaultAzureCredential."""
        # TODO: azure-identity + httpx.
        return {"posted": True, "entryCount": len(bundle.get("entry", []))}
