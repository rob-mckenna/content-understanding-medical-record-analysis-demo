// Reference Bicep for the medical-record processing pipeline.
// Not production-hardened — customize networking, CMK, and diagnostic
// settings to your environment before deploying to a regulated tenant.

targetScope = 'subscription'

@description('Short environment name, e.g. demo-dev / demo-prod.')
param envName string

@description('Azure region for all resources.')
param location string = 'eastus2'

@description('Object ID of the user or group to grant data-plane admin access.')
param adminObjectId string = ''

var rgName = 'rg-cu-mra-${envName}'

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: {
    workload: 'medical-record-analysis'
    env: envName
  }
}

module core 'modules/core.bicep' = {
  name: 'core'
  scope: rg
  params: {
    envName: envName
    location: location
    adminObjectId: adminObjectId
  }
}

output resourceGroup string = rg.name
output storageAccount string = core.outputs.storageAccountName
output functionApp string = core.outputs.functionAppName
output acuAccount string = core.outputs.acuAccountName
output fhirServiceUrl string = core.outputs.fhirServiceUrl
output cosmosAccount string = core.outputs.cosmosAccountName
output keyVault string = core.outputs.keyVaultName
