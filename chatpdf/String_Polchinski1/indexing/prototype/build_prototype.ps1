$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskCache = Join-Path $PSScriptRoot 'texcache'
New-Item -ItemType Directory -Path $taskCache -Force | Out-Null
$env:TEXMFVAR = $taskCache
$env:TEXMFCACHE = $taskCache
$taskLua = 'C:\texlive\2026\bin\windows\lualatex.exe'
& $taskLua -interaction=nonstopmode -halt-on-error index_prototype.tex
if ($LASTEXITCODE -ne 0) { throw 'Initial LuaLaTeX failed.' }
& 'C:\texlive\2026\bin\windows\makeindex.exe' index_prototype.idx
if ($LASTEXITCODE -ne 0) { throw 'MakeIndex failed.' }
& $taskLua -interaction=nonstopmode -halt-on-error index_prototype.tex
if ($LASTEXITCODE -ne 0) { throw 'Second LuaLaTeX failed.' }
& $taskLua -interaction=nonstopmode -halt-on-error index_prototype.tex
if ($LASTEXITCODE -ne 0) { throw 'Final LuaLaTeX failed.' }
