<#
.SYNOPSIS
    Register all classifiers and analyzers with an Azure Content Understanding account.

.EXAMPLE
    ./register-all.ps1 -AcuEndpoint https://<name>.cognitiveservices.azure.com
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)]
    [string]$AcuEndpoint,

    [string]$ApiVersion = "2025-11-01",

    [string[]]$Analyzer
)

$ErrorActionPreference = "Stop"

$token = az account get-access-token --resource https://cognitiveservices.azure.com --query accessToken -o tsv
if (-not $token) { throw "az CLI not signed in." }
$headers = @{ Authorization = "Bearer $token"; "Content-Type" = "application/json" }

# Resolve shared $ref before POSTing (ACU expects fully inlined schemas).
function Resolve-Refs {
    param([string]$Path)
    $raw = Get-Content $Path -Raw
    $obj = $raw | ConvertFrom-Json -Depth 20
    $sharedDir = Join-Path (Split-Path $Path -Parent) "shared"
    $json = $obj | ConvertTo-Json -Depth 20
    # Simple string replace for the $ref pattern used in the scaffold.
    $inlined = [regex]::Replace($json, '"\$ref":\s*"shared/([^"]+)"', {
        param($m)
        $refFile = Join-Path $sharedDir $m.Groups[1].Value
        (Get-Content $refFile -Raw).TrimEnd(',').TrimEnd()
    })
    return $inlined
}

# Register classifier.
$classifierPath = Join-Path $PSScriptRoot "classifier-document-router.json"
if (Test-Path $classifierPath) {
    $body = Get-Content $classifierPath -Raw
    $id = (($body | ConvertFrom-Json).classifierId)
    Write-Host "Registering classifier: $id"
    Invoke-RestMethod -Method Put `
        -Uri "$AcuEndpoint/contentunderstanding/classifiers/${id}?api-version=$ApiVersion" `
        -Headers $headers -Body $body | Out-Null
}

# Register analyzers.
$files = if ($Analyzer) {
    $Analyzer | ForEach-Object { Join-Path $PSScriptRoot $_ }
} else {
    Get-ChildItem $PSScriptRoot -Filter *.json |
        Where-Object { $_.BaseName -ne "classifier-document-router" -and $_.Directory.Name -ne "shared" }
}

foreach ($f in $files) {
    $body = Resolve-Refs -Path $f.FullName
    $id = (($body | ConvertFrom-Json).analyzerId)
    Write-Host "Registering analyzer: $id"
    Invoke-RestMethod -Method Put `
        -Uri "$AcuEndpoint/contentunderstanding/analyzers/${id}?api-version=$ApiVersion" `
        -Headers $headers -Body $body | Out-Null
}

Write-Host "Done."
