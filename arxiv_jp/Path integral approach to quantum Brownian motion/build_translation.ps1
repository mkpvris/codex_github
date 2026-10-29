$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    $documentStem = 'Path_integral_approach_to_quantum_Brownian_motion_jp'
    New-Item -ItemType Directory -Path 'pdf' -Force | Out-Null
    & lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf ($documentStem + '.tex')
    if ($LASTEXITCODE -ne 0) { throw 'First LuaLaTeX pass failed.' }
    & bibtex ('pdf/' + $documentStem)
    if ($LASTEXITCODE -ne 0) { throw 'BibTeX failed.' }
    for ($passNumber=0; $passNumber -lt 2; $passNumber++) {
        & lualatex -interaction=nonstopmode -halt-on-error -output-directory=pdf ($documentStem + '.tex')
        if ($LASTEXITCODE -ne 0) { throw 'LuaLaTeX failed.' }
    }
}
finally { Pop-Location }
