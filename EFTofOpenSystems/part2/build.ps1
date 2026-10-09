# Run from PowerShell: .\build.ps1
# Output: pdf\template.pdf
$ErrorActionPreference = 'Stop'
Push-Location -LiteralPath $PSScriptRoot
try {
    New-Item -ItemType Directory -Path 'pdf' -Force | Out-Null
    $part2Args = @('-interaction=batchmode','-halt-on-error','-file-line-error','-synctex=1','-output-directory=pdf','template.tex')
    & lualatex @part2Args
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX first pass failed.' }
    & bibtex 'pdf/template'
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    & lualatex @part2Args
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX second pass failed.' }
    & lualatex @part2Args
    if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX final pass failed.' }
    $part2Log = Get-Content -LiteralPath 'pdf\template.log' -Raw
    if ($part2Log -match 'undefined references|Citation .+ undefined|Reference .+ undefined') {
        throw 'Unresolved references in pdf/template.log.'
    }
    Write-Output 'OK: pdf/template.pdf'
} finally {
    Pop-Location
}
