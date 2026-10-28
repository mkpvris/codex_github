param([string]$ExcludeChapters='')
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$taskPython = 'C:\Users\false\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$taskConfig=Get-Content -LiteralPath 'project_config.json' -Raw | ConvertFrom-Json
New-Item -ItemType Directory -Path 'build','pdf','build\texcache' -Force | Out-Null
$env:TEXMFVAR = Join-Path $PSScriptRoot 'build\texcache'
$env:TEXMFCACHE = $env:TEXMFVAR
$env:openout_any = 'a'
& $taskPython -X utf8 'prepare_bibliography.py'
if ($LASTEXITCODE -ne 0) { throw 'Bibliography preparation failed.' }
& $taskPython -X utf8 'assemble.py' --exclude $ExcludeChapters
if ($LASTEXITCODE -ne 0) { throw 'Assembly failed.' }
$taskName=$taskConfig.build_jobname
& lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build ('-jobname='+$taskName) $taskConfig.tex_filename *> 'build\pass1_console.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'build\pass1_console.txt' -Tail 40; throw 'First LuaLaTeX failed.' }
& bibtex ('build\'+$taskName) *> 'build\bibtex_console.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'build\bibtex_console.txt' -Tail 40; throw 'BibTeX failed.' }
& lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build ('-jobname='+$taskName) $taskConfig.tex_filename *> 'build\pass2_console.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'build\pass2_console.txt' -Tail 40; throw 'Second LuaLaTeX failed.' }
& lualatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build ('-jobname='+$taskName) $taskConfig.tex_filename *> 'build\pass3_console.txt'
if ($LASTEXITCODE -ne 0) { Get-Content 'build\pass3_console.txt' -Tail 40; throw 'Third LuaLaTeX failed.' }
Copy-Item -LiteralPath ('build\'+$taskName+'.pdf') -Destination (Join-Path 'pdf' $taskConfig.pdf_filename) -Force
Write-Output ('Built: pdf\'+$taskConfig.pdf_filename)
