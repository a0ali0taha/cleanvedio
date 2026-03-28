# Optional alias; forwards to deploy_portable_em.ps1
param(
    [switch]$SkipBuild,
    [string]$OutDir = "portable\CleanVedioPortable"
)
& (Join-Path $PSScriptRoot "deploy_portable_em.ps1") @PSBoundParameters
