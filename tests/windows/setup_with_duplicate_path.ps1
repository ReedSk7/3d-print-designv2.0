# Run the real setup once, with a second PATH match for each required executable.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not $IsWindows) { throw 'This setup regression requires Windows and PowerShell 7.' }

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (Test-Path -LiteralPath (Join-Path $RepoRoot '.venv')) {
    throw 'Run this regression in a fresh checkout without .venv so Python selection is exercised.'
}

$Names = @('npm.cmd', 'python.exe', 'node.exe')
$OriginalFirst = @{}
foreach ($Name in $Names) {
    $Commands = @(Get-Command -Name $Name -CommandType Application -ErrorAction Stop)
    $OriginalFirst[$Name] = $Commands[0].Source
}

$OriginalPath = $env:PATH
$FixturePath = Join-Path ([System.IO.Path]::GetTempPath()) ('workshop duplicate path ' + [guid]::NewGuid().ToString('N'))
$null = New-Item -ItemType Directory -Path $FixturePath
try {
    # These must fail immediately if selected; the real tools stay first on PATH.
    Set-Content -LiteralPath (Join-Path $FixturePath 'npm.cmd') -Encoding ascii -Value @(
        '@echo off',
        'echo ERROR: duplicate PATH npm fixture was selected 1>&2',
        'exit /b 91'
    )
    foreach ($Name in @('python.exe', 'node.exe')) {
        [System.IO.File]::WriteAllBytes((Join-Path $FixturePath $Name), [byte[]]@(0))
    }
    $env:PATH = $OriginalPath + [System.IO.Path]::PathSeparator + $FixturePath

    foreach ($Name in $Names) {
        # Do not use -All: these are the exact lookup flags behind the regression.
        $Commands = @(Get-Command -Name $Name -CommandType Application -ErrorAction Stop)
        $Sources = @($Commands.Source | Sort-Object -Unique)
        if ($Sources.Count -lt 2 -or $Sources -notcontains (Join-Path $FixturePath $Name)) {
            throw "Fixture did not expose distinct duplicate PATH matches for $Name."
        }
        if ($Commands[0].Source -ne $OriginalFirst[$Name]) {
            throw "Fixture changed the first PATH match for $Name."
        }
        Write-Host "Confirmed duplicate PATH matches for $Name; real executable remains first."
    }

    & (Join-Path $RepoRoot 'scripts\setup.ps1') -PythonExecutable 'python.exe'
    if ($LASTEXITCODE -ne 0) { throw "Actual setup failed with exit $LASTEXITCODE." }
} finally {
    $env:PATH = $OriginalPath
    Remove-Item -LiteralPath $FixturePath -Recurse -Force
}
