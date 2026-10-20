$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    New-Item -ItemType Directory -Path 'pdf' -Force | Out-Null
    & lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 2006.16285v1_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    & mpost -interaction=nonstopmode pdf/graphs.mp
    if ($LASTEXITCODE -ne 0) { throw 'MetaPost failed.' }
    & bibtex pdf/2006.16285v1_jp
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    1..2 | ForEach-Object {
        & lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 2006.16285v1_jp.tex
        if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    }
}
finally {
    Pop-Location
}
