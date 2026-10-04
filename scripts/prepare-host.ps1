# SPDX-License-Identifier: Apache-2.0
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$baseline = Get-Content -LiteralPath (Join-Path $projectRoot 'host-baseline.json') -Raw | ConvertFrom-Json
$hostPath = Join-Path $projectRoot '.host/robrix2'
if (!(Test-Path -LiteralPath $hostPath)) {
    New-Item -ItemType Directory -Path (Split-Path -Parent $hostPath) -Force | Out-Null
    & git clone --depth 1 --single-branch --branch $baseline.branch $baseline.repository $hostPath
    if ($LASTEXITCODE -ne 0) { throw 'Host clone failed.' }
}
$remote = & git -C $hostPath remote get-url origin
if ($LASTEXITCODE -ne 0 -or $remote -ne $baseline.repository) { throw 'Unexpected host repository; refusing to alter it.' }
$changes = & git -C $hostPath status --porcelain
if ($LASTEXITCODE -ne 0 -or $changes) { throw 'Host has local changes; refusing to alter it.' }
$head = & git -C $hostPath rev-parse HEAD
if ($head -ne $baseline.commit) {
    & git -C $hostPath fetch --depth 1 origin $baseline.commit
    if ($LASTEXITCODE -ne 0) { throw 'Pinned host fetch failed.' }
    & git -C $hostPath checkout --detach $baseline.commit
    if ($LASTEXITCODE -ne 0) { throw 'Pinned host checkout failed.' }
}
$verified = & git -C $hostPath rev-parse HEAD
if ($verified -ne $baseline.commit) { throw 'Pinned host verification failed.' }
Write-Output "Host: $hostPath"
Write-Output "Verified commit: $verified"
