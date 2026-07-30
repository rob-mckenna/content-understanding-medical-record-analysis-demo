# Infrastructure

Bicep for the reference architecture.

## Deploy

```powershell
az login
az account set --subscription <SUB_ID>

az deployment sub create `
  --location eastus2 `
  --template-file main.bicep `
  --parameters envName=demo-dev adminObjectId=<YOUR_AAD_OID>
```

## Resources created

- Log Analytics + Application Insights
- Key Vault (RBAC, purge protection)
- Storage (ADLS Gen2) with `input` / `output` / `quarantine` / `review-crops` containers
- Azure Content Understanding (AI Services multi-service account)
- Azure Functions on Flex Consumption plan (Linux, Python)
- Cosmos DB (serverless) for human review queue
- Azure Health Data Services workspace + FHIR R4 service

## Not yet included

- Private endpoints on every data-plane resource (add per your networking model)
- Customer-managed key (CMK) — Key Vault key + `encryption` blocks
- Diagnostic settings on every resource
- Azure AI Foundry hub/project for evaluation and prompt-flow orchestration
- RBAC assignments beyond the identity `type: SystemAssigned`
- Service Bus for cross-analyzer messaging

Extend `modules/core.bicep` with additional `modules/*.bicep` files as needed
(`networking.bicep`, `foundry.bicep`, `service-bus.bicep`, etc.).
