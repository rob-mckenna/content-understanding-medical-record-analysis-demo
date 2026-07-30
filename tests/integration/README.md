# Integration tests

Requires:

- A registered ACU account with all analyzers deployed via `analyzers/register-all.ps1`.
- Environment variables:
  - `ACU_ENDPOINT`
  - `ACU_KEY` (or use `DefaultAzureCredential`)
  - `FHIR_URL`

Run:

```powershell
pytest tests/integration -m integration
```

Do not commit real PHI into this folder. Use synthetic samples only.
