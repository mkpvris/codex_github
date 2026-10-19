$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 -output-directory=pdf 1109.4192v2_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'First LuaLaTeX pass failed.' }
    & bibtex pdf/1109.4192v2_jp
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    & python work/group_bibliography.py
    if ($LASTEXITCODE -ne 0) { throw 'Reference grouping failed.' }
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 -output-directory=pdf 1109.4192v2_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'Second LuaLaTeX pass failed.' }
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -synctex=1 -output-directory=pdf 1109.4192v2_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'Third LuaLaTeX pass failed.' }
} finally { Pop-Location }
