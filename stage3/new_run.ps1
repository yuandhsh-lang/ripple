param([Parameter(Mandatory=$true)][ValidatePattern('^p3-[a-z0-9-]+$')][string]$Name)
$ErrorActionPreference = 'Stop'
$stageWork = Split-Path $PSScriptRoot -Parent
$stageRun = Join-Path $stageWork ('stage2/runtime/runs/' + $Name)
$stageEvidence = Join-Path $stageWork ('stage2/evidence/runs/' + $Name)
if ((Test-Path -LiteralPath $stageRun) -or (Test-Path -LiteralPath $stageEvidence)) { throw 'Choose a fresh run name.' }
$stageAllowed = [IO.Path]::GetFullPath((Join-Path $stageWork 'stage2/runtime/runs')) + [IO.Path]::DirectorySeparatorChar
if (![IO.Path]::GetFullPath($stageRun).StartsWith($stageAllowed,[StringComparison]::OrdinalIgnoreCase)) { throw 'Outside test root.' }
New-Item -ItemType Directory -Path $stageRun | Out-Null
$stageAcl = New-Object Security.AccessControl.DirectorySecurity
$stageAcl.SetAccessRuleProtection($true,$false)
$stageUser = [Security.Principal.WindowsIdentity]::GetCurrent().User
$stageAcl.SetOwner($stageUser)
foreach($stageSid in @($stageUser.Value,'S-1-5-18','S-1-5-32-544')) {
    $stageRule = New-Object Security.AccessControl.FileSystemAccessRule(
        (New-Object Security.Principal.SecurityIdentifier($stageSid)),
        'FullControl','ContainerInherit,ObjectInherit','None','Allow')
    $stageAcl.AddAccessRule($stageRule)
}
Set-Acl -LiteralPath $stageRun -AclObject $stageAcl
$stageProfiles = Join-Path $stageRun 'kernel-core/profiles'
New-Item -ItemType Directory -Path $stageProfiles -Force | Out-Null
New-Item -ItemType Directory -Path $stageEvidence | Out-Null
$stageTarget = Join-Path $stageProfiles '_main.json'
Copy-Item -LiteralPath (Join-Path $stageWork 'stage2/runtime/kernel-core/profiles/_main.json') -Destination $stageTarget
$stageMarker = @{runtime_root=$stageRun;core_dir=(Join-Path $stageRun 'kernel-core');provider_profile_only=$true}
$stageMarker | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stageRun 'isolation.json') -Encoding utf8NoBOM
$stageReceipt = @{run=$stageRun;profile=$stageTarget;owner_sid=$stageUser.Value;root_sddl=(Get-Acl -LiteralPath $stageRun).Sddl;profile_sddl=(Get-Acl -LiteralPath $stageTarget).Sddl;copied_only_provider_profile=$true;copied_history=$false}
$stageReceipt | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stageEvidence 'secure-initialization.json') -Encoding utf8NoBOM
$stageStream = [IO.File]::OpenRead($stageTarget); $stageStream.Dispose()
Write-Output ('Protected fresh test run: ' + $stageRun)
