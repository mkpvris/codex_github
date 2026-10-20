$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskTex = 'String_Polchinski1_jp'
$taskLua = 'C:\texlive\2026\bin\windows\lualatex.exe'
$taskBib = 'C:\texlive\2026\bin\windows\bibtex.exe'
$taskTexCache = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) 'tmp\polchinski_tex_cache'
New-Item -ItemType Directory -Path $taskTexCache -Force | Out-Null
$env:TEXMFVAR = $taskTexCache
$env:TEXMFCACHE = $taskTexCache
& $taskLua -interaction=nonstopmode -halt-on-error -output-directory=build "$taskTex.tex"
if ($LASTEXITCODE -ne 0) { throw 'First LuaLaTeX pass failed.' }
& $taskBib "build/$taskTex"
if ($LASTEXITCODE -ne 0) { throw 'BibTeX pass failed.' }
& $taskLua -interaction=nonstopmode -halt-on-error -output-directory=build "$taskTex.tex"
if ($LASTEXITCODE -ne 0) { throw 'Second LuaLaTeX pass failed.' }
& $taskLua -interaction=nonstopmode -halt-on-error -output-directory=build "$taskTex.tex"
if ($LASTEXITCODE -ne 0) { throw 'Third LuaLaTeX pass failed.' }
Copy-Item -LiteralPath "build/$taskTex.pdf" -Destination "pdf/$taskTex.pdf" -Force
Write-Output "Compiled PDF: $PSScriptRoot\pdf\$taskTex.pdf"
