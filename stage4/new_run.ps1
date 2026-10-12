param([Parameter(Mandatory=$true)][ValidatePattern('^p4-[a-z0-9-]+$')][string]$Name)
$ErrorActionPreference='Stop'
$stageWork=Split-Path $PSScriptRoot -Parent
$stageRun=Join-Path $stageWork ('stage2/runtime/runs/'+$Name)
$stageEvidence=Join-Path $stageWork ('stage2/evidence/runs/'+$Name)
if((Test-Path -LiteralPath $stageRun) -or (Test-Path -LiteralPath $stageEvidence)){throw 'Use a fresh run name'}
$stageAllowed=[IO.Path]::GetFullPath((Join-Path $stageWork 'stage2/runtime/runs'))+[IO.Path]::DirectorySeparatorChar
if(![IO.Path]::GetFullPath($stageRun).StartsWith($stageAllowed,[StringComparison]::OrdinalIgnoreCase)){throw 'Outside new test root'}
New-Item -ItemType Directory -Path $stageRun | Out-Null
$stageAcl=New-Object Security.AccessControl.DirectorySecurity
$stageAcl.SetAccessRuleProtection($true,$false)
$stageUser=[Security.Principal.WindowsIdentity]::GetCurrent().User
$stageAcl.SetOwner($stageUser)
foreach($stageSid in @($stageUser.Value,'S-1-5-18','S-1-5-32-544')){
    $stageRule=New-Object Security.AccessControl.FileSystemAccessRule((New-Object Security.Principal.SecurityIdentifier($stageSid)),'FullControl','ContainerInherit,ObjectInherit','None','Allow')
    $stageAcl.AddAccessRule($stageRule)
}
Set-Acl -LiteralPath $stageRun -AclObject $stageAcl
New-Item -ItemType Directory -Path (Join-Path $stageRun 'kernel-core/profiles') | Out-Null
New-Item -ItemType Directory -Path $stageEvidence | Out-Null
# Compatibility marker for the existing guard. Empty is stricter than profile-only.
@{runtime_root=$stageRun;core_dir=(Join-Path $stageRun 'kernel-core');provider_profile_only=$true} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stageRun 'isolation.json') -Encoding utf8NoBOM
'NON-SECRET ACL CHECK ONLY' | Set-Content -LiteralPath (Join-Path $stageRun 'kernel-core/profiles/acl-canary.txt') -Encoding utf8NoBOM
@{run=$stageRun;empty_provider_core=$true;old_state_copied=$false;credential_copied=$false;root_sddl=(Get-Acl -LiteralPath $stageRun).Sddl;owner_sid=$stageUser.Value} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $stageEvidence 'initialization.json') -Encoding utf8NoBOM
Write-Output ('New protected empty run: '+$Name)
