$ErrorActionPreference = 'Stop'
$taskSource = $PSScriptRoot
$taskTarget = 'C:\Users\false\codex\chatpdf\Decoherence and the Quantum-to-Classical Transition'
if ([IO.Path]::GetFullPath($taskTarget) -ne 'C:\Users\false\codex\chatpdf\Decoherence and the Quantum-to-Classical Transition') { throw 'Unexpected destination.' }
New-Item -ItemType Directory -Path $taskTarget -Force | Out-Null
$taskPrevious = Join-Path $taskTarget 'pdf\Decoherence and the Quantum-to-Classical Transition.pdf'
if (Test-Path -LiteralPath $taskPrevious) {
    $taskHistory = Join-Path $taskTarget 'pdf\history'
    New-Item -ItemType Directory -Path $taskHistory -Force | Out-Null
    Copy-Item -LiteralPath $taskPrevious -Destination (Join-Path $taskHistory ('before_update_'+(Get-Date -Format 'yyyyMMdd_HHmmss')+'.pdf'))
}
Get-ChildItem -LiteralPath $taskSource -Force | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $taskTarget -Recurse -Force }
$taskCount=0
Get-ChildItem -LiteralPath $taskSource -Recurse -File -Force | ForEach-Object {
    $taskRelative=[IO.Path]::GetRelativePath($taskSource,$_.FullName)
    $taskCopied=Join-Path $taskTarget $taskRelative
    if ((Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $taskCopied -Algorithm SHA256).Hash) { throw ('Copy mismatch: '+$taskRelative) }
    $taskCount++
}
Write-Output ('Saved and verified '+$taskCount+' files: '+$taskTarget)
