param([switch]$ResumeAfterFirstPass)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskTex = 'String_Polchinski1_jp'
$taskLua = 'C:\texlive\2026\bin\windows\lualatex.exe'
$taskBib = 'C:\texlive\2026\bin\windows\bibtex.exe'
$taskIndex = 'C:\texlive\2026\bin\windows\makeindex.exe'
$taskPython = 'C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$taskTexCache = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'tmp\polchinski_tex_cache'
New-Item -ItemType Directory -Path $taskTexCache -Force | Out-Null
$env:TEXMFVAR = $taskTexCache
$env:TEXMFCACHE = $taskTexCache
& $taskPython -X utf8 assemble.py
if ($LASTEXITCODE -ne 0) { throw 'Assembly failed.' }
if (-not $ResumeAfterFirstPass) {
    & $taskLua -interaction=nonstopmode -halt-on-error -output-directory=build "$taskTex.tex"
    if ($LASTEXITCODE -ne 0) { throw 'First LuaLaTeX pass failed.' }
    & $taskBib "build/$taskTex"
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX pass failed.' }
}
function Update-TaskIndex {
    & $taskPython -X utf8 indexing/build_page_spans.py
    if ($LASTEXITCODE -ne 0) { throw 'Index page mapping failed.' }
    & $taskPython -X utf8 indexing/generate_index.py
    if ($LASTEXITCODE -ne 0) { throw 'Index generation failed.' }
    & $taskIndex -s indexing/bilingual.ist -o "build/$taskTex.ind" -t "build/$taskTex.ilg" "build/$taskTex.idx"
    if ($LASTEXITCODE -ne 0) { throw 'MakeIndex failed.' }
}
Update-TaskIndex
$taskStable = $false
for ($taskPass = 2; $taskPass -le 6; $taskPass++) {
    $taskIndexBefore = (Get-FileHash -LiteralPath "build/$taskTex.ind" -Algorithm SHA256).Hash
    $taskContentsBefore = (Get-FileHash -LiteralPath "build/$taskTex.toc" -Algorithm SHA256).Hash
    & $taskLua -interaction=nonstopmode -halt-on-error -output-directory=build "$taskTex.tex"
    if ($LASTEXITCODE -ne 0) { throw "LuaLaTeX pass $taskPass failed." }
    Update-TaskIndex
    $taskIndexAfter = (Get-FileHash -LiteralPath "build/$taskTex.ind" -Algorithm SHA256).Hash
    $taskContentsAfter = (Get-FileHash -LiteralPath "build/$taskTex.toc" -Algorithm SHA256).Hash
    if ($taskPass -ge 3 -and $taskIndexBefore -eq $taskIndexAfter -and $taskContentsBefore -eq $taskContentsAfter) {
        $taskStable = $true
        break
    }
}
if (-not $taskStable) { throw 'Index or table of contents did not stabilize.' }
Copy-Item -LiteralPath "build/$taskTex.pdf" -Destination "pdf/$taskTex.pdf" -Force
Write-Output "Compiled PDF: $PSScriptRoot\pdf\$taskTex.pdf"
