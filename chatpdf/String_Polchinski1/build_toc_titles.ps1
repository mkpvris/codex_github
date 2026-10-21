param([ValidateSet('normal','extended')][string]$Variant = 'normal')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskStem = 'String_Polchinski1_jp'
$taskFolder = if ($Variant -eq 'extended') { 'build_index_extended' } else { 'build' }
$taskSource = if ($Variant -eq 'extended') { "${taskStem}_index_extended.tex" } else { "$taskStem.tex" }
$taskOutput = if ($Variant -eq 'extended') { "${taskStem}_index_extended.pdf" } else { "$taskStem.pdf" }
$taskCache = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'tmp\polchinski_tex_cache'
$env:TEXMFVAR = $taskCache
$env:TEXMFCACHE = $taskCache
for ($taskPass = 1; $taskPass -le 3; $taskPass++) {
    & 'C:\texlive\2026\bin\windows\lualatex.exe' -interaction=nonstopmode -halt-on-error "-jobname=$taskStem" "-output-directory=$taskFolder" $taskSource
    if ($LASTEXITCODE -ne 0) { throw "$Variant LuaLaTeX pass $taskPass failed" }
    if ($taskPass -eq 1) {
        & 'C:\texlive\2026\bin\windows\bibtex.exe' "$taskFolder/$taskStem"
        if ($LASTEXITCODE -ne 0) { throw "$Variant BibTeX failed" }
    }
}
Copy-Item -LiteralPath "qa/toc_title_build_inputs/$Variant.idx" -Destination "$taskFolder/$taskStem.idx" -Force
Copy-Item -LiteralPath "$taskFolder/$taskStem.pdf" -Destination "pdf/$taskOutput" -Force
Write-Output "Completed $Variant : pdf/$taskOutput"
