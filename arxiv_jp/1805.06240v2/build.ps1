$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$name = '1805.06240v2_jp'
& lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf "$name.tex" *> 'qa\build-lualatex-1.txt'
if ($LASTEXITCODE -ne 0) { throw 'First LuaLaTeX pass failed' }
$env:BIBINPUTS = "$PSScriptRoot;"
$env:BSTINPUTS = "$PSScriptRoot;"
Push-Location -LiteralPath 'pdf'
try {
    & bibtex $name *> '..\qa\build-bibtex.txt'
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed' }
} finally { Pop-Location }
& lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf "$name.tex" *> 'qa\build-lualatex-2.txt'
if ($LASTEXITCODE -ne 0) { throw 'Second LuaLaTeX pass failed' }
& lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf "$name.tex" *> 'qa\build-lualatex-3.txt'
if ($LASTEXITCODE -ne 0) { throw 'Third LuaLaTeX pass failed' }
Write-Output "Build complete: pdf\$name.pdf"
