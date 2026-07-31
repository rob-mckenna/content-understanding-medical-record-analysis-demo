# Deployable Function App (v2 Python model)

Minimal Azure Functions v2 project that consumes the Content Understanding
service and runs the pipeline end-to-end for the demo.

## Functions

| Name | Trigger | Description |
|---|---|---|
| `analyze` | HTTP POST `/api/analyze` (function key) | Accepts raw PDF bytes, submits ACU `inputs[0].data` payload, and returns extraction JSON. |
| `healthcheck` | HTTP GET `/api/health` | Confirms the app can read from ACU (counts registered analyzers). |

## Deploy

```powershell
# Package and deploy with OneDeploy
Compress-Archive -Path functionapp/* -DestinationPath functionapp.zip -Force
az functionapp deploy `
  --resource-group rg-cu-mra-demo `
  --name func-mra-demo-pjoi `
  --src-path functionapp.zip `
  --type zip
```

## App settings expected

Already set by Bicep:

- `AzureWebJobsStorage`
- `FUNCTIONS_WORKER_RUNTIME=python`
- `FUNCTIONS_EXTENSION_VERSION=~4`
- `ACU_ENDPOINT`
- `OUTPUT_CONTAINER`

Add these post-Bicep for the ACU-linked flow:

```powershell
az functionapp config appsettings set --name func-mra-demo-pjoi -g rg-cu-mra-demo `
  --settings ACU_ENDPOINT=https://acu-mra-demo.services.ai.azure.com `
             ACU_API_VERSION=2025-11-01 `
             DEFAULT_ANALYZER=healthcareDischargeSummaryV1
```

## Managed identity

The Function App uses its system-assigned identity to authenticate to ACU
(`DefaultAzureCredential`). Grant it `Cognitive Services User` on the ACU
account.

## Local run

```powershell
cd functionapp
func start
```

Requires Azure Functions Core Tools v4.
