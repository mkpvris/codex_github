$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    & lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 1609.00716v1_jp.tex
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    & bibtex pdf/1609.00716v1_jp
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    $taskBblPath = Join-Path $PSScriptRoot 'pdf\1609.00716v1_jp.bbl'
    Copy-Item -LiteralPath $taskBblPath -Destination 'pdf\1609.00716v1_jp.bibtex_original.bbl' -Force
    $taskBbl = [System.IO.File]::ReadAllText($taskBblPath)
    $taskLabels = @{'Maldacena:2002vr'=9;'Cornwall:1974km'=19;'Cheung:2007st'=21;'Behbahani:2011it'=22;'Achucarro:2012sm'=23;'Seery:2006vu'=25;'Pimentel:2012tw'=28;'Senatore:2012ya'=29}
    foreach ($taskKey in $taskLabels.Keys) {
        $taskBbl = $taskBbl.Replace(('\bibitem{' + $taskKey + '}'), ('\bibitem[' + $taskLabels[$taskKey] + ']{' + $taskKey + '}'))
    }
    $taskBbl = $taskBbl.Replace('\bibitem{Senatore:2009cf}', '\par\medskip\makeatletter\immediate\write\@auxout{\string\bibcite{Senatore:2009cf}{28}}\makeatother')
    $taskBbl = [regex]::Replace($taskBbl, '\\begin\{thebibliography\}\{[^}]+\}', '\begin{thebibliography}{29}')
    [System.IO.File]::WriteAllText($taskBblPath, $taskBbl, [System.Text.UTF8Encoding]::new($false))
    1..2 | ForEach-Object {
        & lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf 1609.00716v1_jp.tex
        if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    }
} finally {
    Pop-Location
}
