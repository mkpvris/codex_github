$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Path 'pdf' -Force | Out-Null
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf 2404.15416.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    & bibtex pdf/2404.15416
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    1..2 | ForEach-Object {
        & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf 2404.15416.tex
        if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    }
    Write-Output (Join-Path $PSScriptRoot 'pdf\2404.15416.pdf')
}
finally {
    Pop-Location
}
