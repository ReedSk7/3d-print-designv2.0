# Project-only dependency setup and locked app build. Activation is unnecessary.
# One-time setup (also after dependency/app changes): pwsh -NoProfile -File .\scripts\setup.ps1
# Example: .\scripts\setup.ps1 -PythonVersion 3.13
# Or: .\scripts\setup.ps1 -PythonExecutable 'C:\Tools\Python312\python.exe'
[CmdletBinding()]
param(
    [ValidateSet('3.12', '3.13')]
    [string]$PythonVersion = '3.12',
    [string]$PythonExecutable = ''
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot '.venv'
$VenvPython = Join-Path $VenvPath 'Scripts\python.exe'
$LockPath = Join-Path $RepoRoot 'requirements-lock.txt'
$AppPath = Join-Path $RepoRoot 'app'

function Invoke-CheckedNative {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed (exit $LASTEXITCODE): $Program $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $LockPath -PathType Leaf)) {
    throw "Missing dependency lock: $LockPath"
}
if (-not (Test-Path -LiteralPath (Join-Path $AppPath 'package-lock.json') -PathType Leaf)) {
    throw 'Missing app/package-lock.json. Restore the project lock before setup.'
}
if (-not (Get-Command -Name 'node.exe' -CommandType Application -ErrorAction SilentlyContinue) -or
    -not (Get-Command -Name 'npm.cmd' -CommandType Application -ErrorAction SilentlyContinue)) {
    throw 'Node.js and npm are required to build the local app. Install a supported Node.js LTS release, reopen PowerShell 7, then run scripts/setup.ps1 again. Setup does not install global tools.'
}
$Npm = (Get-Command -Name 'npm.cmd' -CommandType Application -ErrorAction Stop).Source

if (Test-Path -LiteralPath $VenvPath) {
    if (-not (Test-Path -LiteralPath (Join-Path $VenvPath 'pyvenv.cfg') -PathType Leaf) -or
        -not (Test-Path -LiteralPath $VenvPython -PathType Leaf)) {
        throw 'Existing .venv is not a usable Windows virtual environment. Preserve it and select a new checkout or move it aside manually; setup will not overwrite it.'
    }
} else {
    $LauncherArgs = @()
    if ($PythonExecutable) {
        $Launcher = (Get-Command -Name $PythonExecutable -CommandType Application -ErrorAction Stop).Source
    } else {
        $Launcher = (Get-Command -Name 'py' -CommandType Application -ErrorAction Stop).Source
        $LauncherArgs = @("-$PythonVersion")
    }
    $VersionProbe = 'import sys; print(sys.executable); print(sys.version); sys.exit(0 if sys.version_info[:2] in ((3,12),(3,13)) else 1)'
    Invoke-CheckedNative -Program $Launcher -Arguments ($LauncherArgs + @('-c', $VersionProbe))
    Invoke-CheckedNative -Program $Launcher -Arguments ($LauncherArgs + @('-m', 'venv', $VenvPath))
}

# A folder named .venv is not sufficient: reject a global/misdirected interpreter.
$IsolationProbe = 'import pathlib,sys; expected=pathlib.Path(sys.argv[1]).resolve(); valid=sys.prefix!=sys.base_prefix and pathlib.Path(sys.prefix).resolve()==expected and sys.version_info[:2] in ((3,12),(3,13)); print("Project interpreter:",sys.executable); sys.exit(0 if valid else 1)'
Invoke-CheckedNative -Program $VenvPython -Arguments @('-c', $IsolationProbe, $VenvPath)
Invoke-CheckedNative -Program $VenvPython -Arguments @('-m', 'pip', '--isolated', '--require-virtualenv', 'install', '--prefix', $VenvPath, '-r', $LockPath)
Invoke-CheckedNative -Program $VenvPython -Arguments @('-m', 'pip', 'check')
Push-Location -LiteralPath $AppPath
try {
    Invoke-CheckedNative -Program $Npm -Arguments @('ci')
    Invoke-CheckedNative -Program $Npm -Arguments @('run', 'build')
} finally {
    Pop-Location
}
Invoke-CheckedNative -Program $VenvPython -Arguments @((Join-Path $PSScriptRoot 'check_workshop_build.py'))
Invoke-CheckedNative -Program $VenvPython -Arguments @((Join-Path $PSScriptRoot 'check_environment.py'))
Invoke-CheckedNative -Program $VenvPython -Arguments @('-B', (Join-Path $PSScriptRoot 'serve_workshop.py'), '--check-only')
Write-Host 'Project dependencies and current app build are ready. Open Print Workshop.cmd for normal launch. OpenSCAD, Bambu Studio and Codex remain separate installations; no printer settings were changed.'
