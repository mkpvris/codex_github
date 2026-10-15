$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $env:TEXMFVAR = Join-Path $PSScriptRoot 'build-cache'
    New-Item -ItemType Directory -Force -Path $env:TEXMFVAR, 'pdf' | Out-Null
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf 0907.5424v2_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    & bibtex pdf/0907.5424v2_jp
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    1..2 | ForEach-Object {
        & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf 0907.5424v2_jp.tex
        if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    }
} finally {
    Pop-Location
}
