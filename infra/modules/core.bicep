// Core resources for the medical-record analysis pipeline.
// SCAFFOLD — populate resource properties (SKUs, networking, CMK) before use.

@description('Short environment name.')
param envName string

@description('Azure region.')
param location string

@description('Object ID granted data-plane admin access.')
param adminObjectId string = ''

var suffix = uniqueString(resourceGroup().id)
var storageName = toLower('stcumra${envName}${substring(suffix, 0, 6)}')
var acuName     = 'acu-mra-${envName}'
var funcName    = 'func-mra-${envName}-${substring(suffix, 0, 4)}'
var planName    = 'plan-mra-${envName}'
var kvName      = 'kv-mra-${envName}-${substring(suffix, 0, 4)}'
var laName      = 'log-mra-${envName}'
var aiName      = 'ai-mra-${envName}'
var cosmosName  = 'cos-mra-${envName}-${substring(suffix, 0, 4)}'
var ahdsWs      = 'ahds-mra-${envName}'
var fhirName    = 'fhir1'

resource la 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: laName
  location: location
  properties: {
    sku: { name: 'PerGB2018' }
    retentionInDays: 90
  }
}

resource ai 'Microsoft.Insights/components@2020-02-02' = {
  name: aiName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: la.id
  }
}

resource kv 'Microsoft.KeyVault/vaults@2024-04-01-preview' = {
  name: kvName
  location: location
  properties: {
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
  }
}

resource storage 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: storageName
  location: location
  sku: { name: 'Standard_ZRS' }
  kind: 'StorageV2'
  properties: {
    isHnsEnabled: true
    minimumTlsVersion: 'TLS1_2'
    allowBlobPublicAccess: false
    supportsHttpsTrafficOnly: true
    networkAcls: { defaultAction: 'Allow', bypass: 'AzureServices' }
  }
}

resource inputContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  name: '${storage.name}/default/input'
  properties: { publicAccess: 'None' }
}
resource outputContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  name: '${storage.name}/default/output'
  properties: { publicAccess: 'None' }
}
resource quarantineContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  name: '${storage.name}/default/quarantine'
  properties: { publicAccess: 'None' }
}
resource reviewCropsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2024-01-01' = {
  name: '${storage.name}/default/review-crops'
  properties: { publicAccess: 'None' }
}

resource acu 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  name: acuName
  location: location
  kind: 'AIServices'
  sku: { name: 'S0' }
  identity: { type: 'SystemAssigned' }
  properties: {
    customSubDomainName: acuName
    publicNetworkAccess: 'Enabled' // switch to Disabled + PE for prod
  }
}

resource plan 'Microsoft.Web/serverfarms@2024-04-01' = {
  name: planName
  location: location
  sku: { name: 'FC1', tier: 'FlexConsumption' }
  properties: { reserved: true }
}

resource func 'Microsoft.Web/sites@2024-04-01' = {
  name: funcName
  location: location
  kind: 'functionapp,linux'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      appSettings: [
        { name: 'AzureWebJobsStorage__accountName', value: storage.name }
        { name: 'FUNCTIONS_WORKER_RUNTIME',        value: 'python' }
        { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: ai.properties.ConnectionString }
        { name: 'ACU_ENDPOINT', value: 'https://${acu.properties.customSubDomainName}.cognitiveservices.azure.com' }
        { name: 'INPUT_CONTAINER',      value: 'input' }
        { name: 'OUTPUT_CONTAINER',     value: 'output' }
        { name: 'QUARANTINE_CONTAINER', value: 'quarantine' }
      ]
    }
  }
}

resource cosmos 'Microsoft.DocumentDB/databaseAccounts@2024-08-15' = {
  name: cosmosName
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [ { locationName: location, failoverPriority: 0 } ]
    capabilities: [ { name: 'EnableServerless' } ]
  }
}

resource ahds 'Microsoft.HealthcareApis/workspaces@2024-03-31' = {
  name: ahdsWs
  location: location
}

resource fhir 'Microsoft.HealthcareApis/workspaces/fhirservices@2024-03-31' = {
  parent: ahds
  name: fhirName
  location: location
  kind: 'fhir-R4'
  identity: { type: 'SystemAssigned' }
  properties: {
    authenticationConfiguration: {
      authority: environment().authentication.loginEndpoint + subscription().tenantId
      audience: 'https://${ahdsWs}-${fhirName}.fhir.azurehealthcareapis.com'
      smartProxyEnabled: false
    }
  }
}

output storageAccountName string = storage.name
output functionAppName    string = func.name
output acuAccountName     string = acu.name
output cosmosAccountName  string = cosmos.name
output keyVaultName       string = kv.name
output fhirServiceUrl     string = 'https://${ahdsWs}-${fhirName}.fhir.azurehealthcareapis.com'
