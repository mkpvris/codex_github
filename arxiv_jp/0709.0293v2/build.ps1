$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    New-Item -ItemType Directory -Force -Path 'pdf' | Out-Null
    lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 0709.0293v2_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    bibtex pdf/0709.0293v2_jp
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    1..2 | ForEach-Object {
        lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 0709.0293v2_jp.tex
        if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    }
}
finally { Pop-Location }
