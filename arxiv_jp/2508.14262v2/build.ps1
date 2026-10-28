$ErrorActionPreference = 'Stop'
$paperName = '2508.14262v2_jp'
$savedBibInputs = $env:BIBINPUTS
$savedBstInputs = $env:BSTINPUTS
Push-Location -LiteralPath $PSScriptRoot
try {
    New-Item -ItemType Directory -Path 'pdf' -Force | Out-Null
    & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf "$paperName.tex" *> 'pdf/build_lualatex_1.txt'
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX first pass failed. See pdf/build_lualatex_1.txt.' }
    Push-Location -LiteralPath 'pdf'
    try {
        $env:BIBINPUTS = '..;'
        $env:BSTINPUTS = '..;'
        & bibtex $paperName *> 'build_bibtex.txt'
        if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed. See pdf/build_bibtex.txt.' }
    } finally {
        Pop-Location
        $env:BIBINPUTS = $savedBibInputs
        $env:BSTINPUTS = $savedBstInputs
    }
    foreach ($passNumber in 2, 3) {
        & lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=pdf "$paperName.tex" *> "pdf/build_lualatex_$passNumber.txt"
        if ($LASTEXITCODE -ne 0) { throw "LuaLaTeX pass $passNumber failed." }
    }
    Write-Output (Join-Path $PSScriptRoot "pdf/$paperName.pdf")
} finally {
    Pop-Location
}
