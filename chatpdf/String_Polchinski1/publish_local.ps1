$ErrorActionPreference = 'Stop'
$taskSource = $PSScriptRoot
$taskTarget = 'C:\codex\chatpdf\String_Polchinski1'
if ([IO.Path]::GetFullPath($taskTarget) -ne 'C:\codex\chatpdf\String_Polchinski1') {
    throw 'Unexpected output path'
}
New-Item -ItemType Directory -Path $taskTarget -Force | Out-Null
$taskPrevious = Join-Path $taskTarget 'pdf\String_Polchinski1_jp.pdf'
if (Test-Path -LiteralPath $taskPrevious) {
    $taskHistory = Join-Path $taskTarget 'pdf\history'
    New-Item -ItemType Directory -Path $taskHistory -Force | Out-Null
    $taskStamp = Get-Date -Format 'yyyyMMdd_HHmmss'
    Copy-Item -LiteralPath $taskPrevious -Destination (Join-Path $taskHistory "before_update_$taskStamp.pdf")
}
Get-ChildItem -LiteralPath $taskSource -Force | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $taskTarget -Recurse -Force
}
$taskSourceHash = (Get-FileHash -LiteralPath (Join-Path $taskSource 'pdf\String_Polchinski1_jp.pdf') -Algorithm SHA256).Hash
$taskTargetHash = (Get-FileHash -LiteralPath $taskPrevious -Algorithm SHA256).Hash
if ($taskSourceHash -ne $taskTargetHash) { throw 'PDF hash mismatch after copying.' }
Write-Output "Saved and verified: $taskPrevious"
